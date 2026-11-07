from datetime import date, datetime, time

from PySide6.QtCore import Qt, QDate, QTimer, Signal
from PySide6.QtGui import QTextCharFormat, QColor, QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QCalendarWidget,
    QListWidget,
    QListWidgetItem,
    QFrame,
    QDialog,
)

from mochi.workspace.pages.calendar_page import (
    EventDialog,
    MochiMessageDialog,
)


class CalendarWidget(QWidget):
    """Independent floating calendar using the shared CalendarService."""

    events_changed = Signal()

    def __init__(self, calendar_service):
        super().__init__()

        self.calendar_service = calendar_service
        self.selected_date = date.today()
        self.highlighted_dates = set()
        self._drag_position = None

        self.setWindowTitle("Widget - Calendar")
        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.resize(390, 540)
        self.setMinimumSize(350, 470)

        self.setStyleSheet("""
            QWidget {
                background-color: #F5F1E9;
                color: #292B28;
                font-family: "Segoe UI";
            }

            QFrame#Header {
                background-color: #292E29;
                border-radius: 12px;
            }

            QLabel#Title {
                color: #F5F1E9;
                font-size: 18px;
                font-weight: bold;
            }

            QLabel#Subtitle {
                color: #C5CCBF;
                font-size: 10px;
            }

            QFrame#Content {
                background-color: #FFFCF6;
                border: 1px solid #DEDCCF;
                border-radius: 12px;
            }

            QLabel#SectionTitle {
                color: #354B38;
                font-size: 13px;
                font-weight: bold;
            }

            QLabel#EmptyLabel {
                color: #898B80;
                font-size: 11px;
                padding: 8px;
            }

            QCalendarWidget {
                background-color: #FFFCF6;
                border: none;
            }

            QCalendarWidget QWidget {
                alternate-background-color: #F1EEE5;
            }

            QCalendarWidget QToolButton {
                color: #354B38;
                background-color: transparent;
                font-weight: bold;
                padding: 6px;
            }

            QCalendarWidget QToolButton:hover {
                background-color: #E9EDE5;
                border-radius: 6px;
            }

            QCalendarWidget QAbstractItemView {
                selection-background-color: #596B55;
                selection-color: white;
                color: #292B28;
                background-color: #FFFCF6;
                gridline-color: #EAE6DC;
            }

            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
                padding: 3px;
            }

            QListWidget::item {
                background-color: #F1EEE5;
                border-radius: 7px;
                padding: 9px;
                margin: 3px 0;
            }

            QListWidget::item:selected {
                background-color: #DCE5D7;
                color: #292B28;
            }

            QPushButton {
                background-color: #596B55;
                color: white;
                border: none;
                border-radius: 7px;
                padding: 8px 12px;
                font-size: 11px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #465641;
            }

            QPushButton#CloseButton {
                background-color: transparent;
                color: #F5F1E9;
                font-size: 17px;
                padding: 3px 8px;
            }

            QPushButton#CloseButton:hover {
                background-color: #41483F;
            }

            QPushButton:disabled {
                background-color: #C8C9C0;
                color: #77796F;
            }
        """)

        self.build_interface()
        self.refresh_calendar()
        self.refresh_event_list()

        # Keep this widget's view up to date when the workspace Calendar
        # changes events independently.
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_calendar)
        self.refresh_timer.start(3000)

    def build_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        # Header
        header = QFrame()
        header.setObjectName("Header")

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(14, 10, 10, 10)

        title_area = QVBoxLayout()
        title = QLabel("Calendar")
        title.setObjectName("Title")

        subtitle = QLabel("Your schedule at a glance")
        subtitle.setObjectName("Subtitle")

        title_area.addWidget(title)
        title_area.addWidget(subtitle)

        close_button = QPushButton("×")
        close_button.setObjectName("CloseButton")
        close_button.setFixedSize(30, 30)
        close_button.setToolTip("Hide Calendar")
        close_button.clicked.connect(self.hide)

        header_layout.addLayout(title_area)
        header_layout.addStretch()
        header_layout.addWidget(close_button)

        layout.addWidget(header)

        # Monthly calendar
        calendar_card = QFrame()
        calendar_card.setObjectName("Content")

        calendar_layout = QVBoxLayout(calendar_card)
        calendar_layout.setContentsMargins(10, 8, 10, 8)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setFirstDayOfWeek(Qt.DayOfWeek.Monday)
        self.calendar.clicked.connect(self.on_date_selected)
        self.calendar.currentPageChanged.connect(
            lambda year, month: self.refresh_calendar()
        )

        calendar_layout.addWidget(self.calendar)
        layout.addWidget(calendar_card)

        # Selected date and events
        events_card = QFrame()
        events_card.setObjectName("Content")

        events_layout = QVBoxLayout(events_card)
        events_layout.setContentsMargins(12, 10, 12, 10)
        events_layout.setSpacing(7)

        self.date_heading = QLabel()
        self.date_heading.setObjectName("SectionTitle")

        self.event_count = QLabel()
        self.event_count.setStyleSheet(
            "color: #898B80; font-size: 10px;"
        )

        events_layout.addWidget(self.date_heading)
        events_layout.addWidget(self.event_count)

        self.event_list = QListWidget()
        self.event_list.itemSelectionChanged.connect(
            self.update_action_buttons
        )
        events_layout.addWidget(self.event_list, 1)

        self.empty_label = QLabel("No events for this date.")
        self.empty_label.setObjectName("EmptyLabel")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        events_layout.addWidget(self.empty_label)

        actions = QHBoxLayout()

        self.add_button = QPushButton("Add Event")
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")

        self.add_button.clicked.connect(self.add_event)
        self.edit_button.clicked.connect(self.edit_selected_event)
        self.delete_button.clicked.connect(self.delete_selected_event)

        actions.addWidget(self.add_button)
        actions.addWidget(self.edit_button)
        actions.addWidget(self.delete_button)

        events_layout.addLayout(actions)
        layout.addWidget(events_card, 1)

        self.date_heading.setText(
            self.selected_date.strftime("%A, %d %B %Y")
        )

        self.update_action_buttons()

    def on_date_selected(self, selected_qdate):
        self.selected_date = date(
            selected_qdate.year(),
            selected_qdate.month(),
            selected_qdate.day(),
        )
        self.refresh_event_list()

    def refresh_calendar(self):
        """Refresh event-date highlights from the shared service."""

        for old_date in self.highlighted_dates:
            self.calendar.setDateTextFormat(
                QDate(old_date.year, old_date.month, old_date.day),
                QTextCharFormat(),
            )

        self.highlighted_dates.clear()

        today_format = QTextCharFormat()
        today_format.setFontWeight(QFont.Weight.Bold)
        today_format.setForeground(QColor("#354B38"))

        self.calendar.setDateTextFormat(
            QDate.currentDate(),
            today_format,
        )

        events = self.calendar_service.get_all_events()

        event_format = QTextCharFormat()
        event_format.setBackground(QColor("#E1E9DC"))
        event_format.setForeground(QColor("#354B38"))
        event_format.setFontWeight(QFont.Weight.Bold)

        for event in events:
            try:
                event_date = datetime.fromisoformat(
                    event["start_datetime"]
                ).date()
            except (TypeError, ValueError):
                continue

            self.calendar.setDateTextFormat(
                QDate(
                    event_date.year,
                    event_date.month,
                    event_date.day,
                ),
                event_format,
            )
            self.highlighted_dates.add(event_date)

        # Restore today's formatting if it also has an event.
        if date.today() in self.highlighted_dates:
            today_event_format = QTextCharFormat(event_format)
            today_event_format.setBackground(QColor("#C9D8C1"))
            self.calendar.setDateTextFormat(
                QDate.currentDate(),
                today_event_format,
            )

        self.refresh_event_list()

    def refresh_event_list(self):
        """Display events overlapping the currently selected date."""

        self.date_heading.setText(
            self.selected_date.strftime("%A, %d %B %Y")
        )

        start = datetime.combine(self.selected_date, time.min)
        end = datetime.combine(self.selected_date, time.max)

        events = self.calendar_service.get_events_between(
            start.isoformat(timespec="seconds"),
            end.isoformat(timespec="seconds"),
        )

        self.event_list.clear()

        for event in events:
            try:
                start_time = datetime.fromisoformat(
                    event["start_datetime"]
                ).strftime("%I:%M %p")
            except (TypeError, ValueError):
                start_time = "Time unavailable"

            category = event.get("category") or "General"

            item = QListWidgetItem(
                f"{start_time}  ·  {event['title']}  ·  {category}"
            )
            item.setData(Qt.ItemDataRole.UserRole, event)
            self.event_list.addItem(item)

        count = len(events)
        self.event_count.setText(
            f"{count} event{'s' if count != 1 else ''}"
        )
        self.empty_label.setVisible(count == 0)
        self.event_list.setVisible(count > 0)

        self.update_action_buttons()

    def update_action_buttons(self):
        selected = bool(self.event_list.selectedItems())

        self.add_button.setEnabled(
            self.selected_date >= date.today()
        )
        self.edit_button.setEnabled(
            selected and self.selected_date >= date.today()
        )
        self.delete_button.setEnabled(selected)

    def add_event(self):
        if self.selected_date < date.today():
            MochiMessageDialog.show_message(
                self,
                "Past date",
                "You cannot add events to a past date.",
            )
            return

        dialog = EventDialog(
            parent=self,
            selected_date=self.selected_date,
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self.calendar_service.create_event(
            **dialog.get_event_data()
        )

        self.refresh_calendar()
        self.events_changed.emit()

    def edit_selected_event(self):
        selected_items = self.event_list.selectedItems()

        if not selected_items:
            return

        if self.selected_date < date.today():
            MochiMessageDialog.show_message(
                self,
                "Past date",
                "You cannot edit events on a past date.",
            )
            return

        event = selected_items[0].data(Qt.ItemDataRole.UserRole)

        dialog = EventDialog(
            parent=self,
            event=event,
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self.calendar_service.update_event(
            event["id"],
            **dialog.get_event_data(),
        )

        self.refresh_calendar()
        self.events_changed.emit()

    def delete_selected_event(self):
        selected_items = self.event_list.selectedItems()

        if not selected_items:
            return

        event = selected_items[0].data(Qt.ItemDataRole.UserRole)

        confirmed = MochiMessageDialog.ask_confirmation(
            self,
            "Delete event",
            f"Are you sure you want to delete '{event['title']}'?",
        )

        if not confirmed:
            return

        self.calendar_service.delete_event(event["id"])

        self.refresh_calendar()
        self.events_changed.emit()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_calendar()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event):
        if (
            self._drag_position is not None
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            self.move(
                event.globalPosition().toPoint()
                - self._drag_position
            )
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_position = None
        super().mouseReleaseEvent(event)
