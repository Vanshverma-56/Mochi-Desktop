
from datetime import date, datetime, time, timedelta

from PySide6.QtCore import Qt, QDate, QDateTime, QTime
from PySide6.QtGui import QTextCharFormat, QColor, QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QCalendarWidget,
    QFrame,
    QListWidget,
    QListWidgetItem,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QDateTimeEdit,
)


def to_qdatetime(value):
    """Convert a Python datetime into a Qt QDateTime safely."""
    return QDateTime(
        QDate(value.year, value.month, value.day),
        QTime(value.hour, value.minute, value.second),
    )


class MochiMessageDialog(QDialog):
    """Custom Mochi-styled message and confirmation dialog."""

    def __init__(
        self,
        parent=None,
        title="Mochi",
        message="",
        confirm_text="OK",
        cancel_text=None,
        danger=False,
    ):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setMinimumWidth(360)
        self.setMaximumWidth(460)
        self.setModal(True)

        self.setStyleSheet("""
            QDialog {
                background-color: #F8F5EE;
            }

            QLabel#DialogTitle {
                color: #292E29;
                font-size: 17px;
                font-weight: bold;
            }

            QLabel#DialogMessage {
                color: #77796F;
                font-size: 12px;
            }

            QPushButton {
                background-color: #EAE8DF;
                color: #3D473A;
                border: none;
                border-radius: 8px;
                padding: 9px 18px;
                font-size: 12px;
            }

            QPushButton:hover {
                background-color: #DCDDCF;
            }

            QPushButton#ConfirmButton {
                background-color: #596B55;
                color: white;
                font-weight: bold;
            }

            QPushButton#ConfirmButton:hover {
                background-color: #465842;
            }

            QPushButton#DangerButton {
                background-color: #A6534D;
                color: white;
                font-weight: bold;
            }

            QPushButton#DangerButton:hover {
                background-color: #8F433E;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(13)

        title_label = QLabel(title)
        title_label.setObjectName("DialogTitle")
        layout.addWidget(title_label)

        message_label = QLabel(message)
        message_label.setObjectName("DialogMessage")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        if cancel_text is not None:
            cancel_button = QPushButton(cancel_text)
            cancel_button.clicked.connect(self.reject)
            button_layout.addWidget(cancel_button)

        confirm_button = QPushButton(confirm_text)
        confirm_button.setObjectName(
            "DangerButton" if danger else "ConfirmButton"
        )
        confirm_button.clicked.connect(self.accept)
        button_layout.addWidget(confirm_button)

        layout.addLayout(button_layout)

    @staticmethod
    def show_message(
        parent,
        title,
        message,
        confirm_text="OK",
        danger=False,
    ):
        dialog = MochiMessageDialog(
            parent,
            title,
            message,
            confirm_text=confirm_text,
            danger=danger,
        )
        dialog.exec()

    @staticmethod
    def ask_confirmation(
        parent,
        title,
        message,
        confirm_text="Confirm",
        cancel_text="Cancel",
        danger=False,
    ):
        dialog = MochiMessageDialog(
            parent,
            title,
            message,
            confirm_text=confirm_text,
            cancel_text=cancel_text,
            danger=danger,
        )
        return dialog.exec() == QDialog.DialogCode.Accepted


class EventDialog(QDialog):
    """Dialog for creating and editing calendar events."""

    CATEGORIES = [
        "General",
        "Work",
        "Personal",
        "Study",
        "Health",
        "Social",
    ]

    def __init__(self, parent=None, event=None, selected_date=None):
        super().__init__(parent)

        self.event_item = event

        self.setWindowTitle("Edit Event" if event else "New Event")
        self.setMinimumWidth(440)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(15)

        heading = QLabel(
            "Edit event" if event else "Create an event"
        )
        heading.setStyleSheet("""
            font-size: 21px;
            font-weight: bold;
            color: #292E29;
        """)
        layout.addWidget(heading)

        subtitle = QLabel(
            "Add the details for your scheduled event."
        )
        subtitle.setStyleSheet(
            "color: #85877D; font-size: 12px;"
        )
        layout.addWidget(subtitle)

        form = QFormLayout()
        form.setSpacing(13)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText(
            "e.g. Project meeting"
        )

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText(
            "Add notes or additional details..."
        )
        self.description_input.setFixedHeight(85)

        self.start_input = QDateTimeEdit()
        self.start_input.setCalendarPopup(True)
        self.start_input.setDisplayFormat(
            "dd MMM yyyy, hh:mm AP"
        )

        self.end_input = QDateTimeEdit()
        self.end_input.setCalendarPopup(True)
        self.end_input.setDisplayFormat(
            "dd MMM yyyy, hh:mm AP"
        )

        if selected_date is not None:
            start = datetime.combine(
                selected_date,
                time(9, 0),
            )
            end = start + timedelta(hours=1)
        else:
            start = datetime.now().replace(
                minute=0,
                second=0,
                microsecond=0,
            ) + timedelta(hours=1)
            end = start + timedelta(hours=1)

        self.start_input.setDateTime(to_qdatetime(start))
        self.end_input.setDateTime(to_qdatetime(end))

        self.category_input = QComboBox()
        self.category_input.addItems(self.CATEGORIES)

        form.addRow("Event title", self.title_input)
        form.addRow("Description", self.description_input)
        form.addRow("Starts", self.start_input)
        form.addRow("Ends", self.end_input)
        form.addRow("Category", self.category_input)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )

        buttons.button(
            QDialogButtonBox.StandardButton.Save
        ).setText("Save event")

        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

        self.setStyleSheet("""
            QDialog {
                background-color: #F8F5EE;
            }

            QLabel {
                color: #292E29;
            }

            QLineEdit, QTextEdit, QComboBox, QDateTimeEdit {
                background-color: #FFFEFA;
                border: 1px solid #DEDCD2;
                border-radius: 8px;
                padding: 9px;
                color: #292E29;
            }

            QLineEdit:focus, QTextEdit:focus,
            QComboBox:focus, QDateTimeEdit:focus {
                border: 1px solid #71866A;
            }

            QPushButton {
                background-color: #EAE8DF;
                color: #3D473A;
                border: none;
                border-radius: 8px;
                padding: 9px 16px;
            }

            QPushButton:hover {
                background-color: #DCDDCF;
            }
        """)

        if event:
            self.title_input.setText(event["title"])

            self.description_input.setPlainText(
                event.get("description", "")
            )

            start = datetime.fromisoformat(
                event["start_datetime"]
            )
            self.start_input.setDateTime(to_qdatetime(start))

            if event.get("end_datetime"):
                end = datetime.fromisoformat(
                    event["end_datetime"]
                )
                self.end_input.setDateTime(to_qdatetime(end))

            category = event.get("category", "General")
            index = self.category_input.findText(category)

            if index >= 0:
                self.category_input.setCurrentIndex(index)

    def validate_and_accept(self):
        if not self.title_input.text().strip():
            MochiMessageDialog.show_message(
                self,
                "Missing title",
                "Please enter an event title.",
            )
            return

        if (
            self.end_input.dateTime()
            <= self.start_input.dateTime()
        ):
            MochiMessageDialog.show_message(
                self,
                "Invalid time",
                "The event end time must be after its start time.",
            )
            return

        self.accept()

    def get_event_data(self):
        return {
            "title": self.title_input.text().strip(),
            "description": (
                self.description_input.toPlainText().strip()
            ),
            "start_datetime": (
                self.start_input.dateTime()
                .toPython()
                .isoformat(timespec="seconds")
            ),
            "end_datetime": (
                self.end_input.dateTime()
                .toPython()
                .isoformat(timespec="seconds")
            ),
            "category": self.category_input.currentText(),
        }


class CalendarPage(QWidget):
    """Monthly calendar with persistent event management."""

    def __init__(self, calendar_service):
        super().__init__()

        self.calendar_service = calendar_service
        self.selected_date = date.today()

        self.setStyleSheet("""
            QWidget {
                color: #292E29;
                font-family: "Segoe UI";
            }

            QFrame#CalendarPanel {
                background-color: #FFFEFA;
                border: 1px solid #E8E4D9;
                border-radius: 16px;
            }

            QLabel#PageTitle {
                font-size: 27px;
                font-weight: bold;
                color: #292E29;
            }

            QLabel#Subtitle {
                color: #85877D;
                font-size: 12px;
            }

            QLabel#MonthHeading {
                font-size: 20px;
                font-weight: bold;
                color: #344231;
            }

            QLabel#PanelTitle {
                font-size: 18px;
                font-weight: bold;
                color: #30372F;
            }

            QLabel#EventCount {
                color: #85877D;
                font-size: 11px;
            }

            QPushButton {
                background-color: #EAE8DF;
                color: #3D473A;
                border: none;
                border-radius: 9px;
                padding: 9px 15px;
                font-size: 12px;
            }

            QPushButton:hover {
                background-color: #DCDDCF;
            }

            QPushButton#PrimaryButton {
                background-color: #596B55;
                color: white;
                font-weight: bold;
            }

            QPushButton#PrimaryButton:hover {
                background-color: #465842;
            }

            QPushButton#DeleteButton {
                background-color: #F5E5E3;
                color: #A34E49;
            }

            QPushButton:disabled {
                background-color: #EAE8E1;
                color: #B5B3AA;
                border: 1px solid #E4E1D9;
            }

            QPushButton#PrimaryButton:disabled {
                background-color: #EAE8E1;
                color: #B5B3AA;
            }

            QPushButton#DeleteButton:disabled {
                background-color: #EAE8E1;
                color: #B5B3AA;
            }

            QPushButton#DeleteButton:hover {
                background-color: #EED5D2;
            }

            QPushButton#MonthArrow {
                font-size: 17px;
                font-weight: bold;
                padding: 6px;
                min-width: 34px;
            }

            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
            }

            QListWidget::item {
                background-color: #F5F3EC;
                border: 1px solid #EAE6DA;
                border-radius: 9px;
                padding: 12px;
                margin-bottom: 7px;
            }

            QListWidget::item:selected {
                background-color: #E6EDE2;
                border: 1px solid #9AAA91;
                color: #293829;
            }

            QCalendarWidget QWidget {
                background-color: #FFFEFA;
            }

            QCalendarWidget QAbstractItemView {
                selection-background-color: #596B55;
                selection-color: white;
                color: #333A32;
                background-color: #FFFEFA;
                font-size: 13px;
                outline: none;
                gridline-color: #F0EDE5;
            }
        """)

        self.build_interface()
        self.refresh_calendar()

    def build_interface(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(17)

        heading_layout = QHBoxLayout()
        heading_layout.setSpacing(12)

        heading_text = QVBoxLayout()
        heading_text.setSpacing(4)

        title = QLabel("Calendar")
        title.setObjectName("PageTitle")

        subtitle = QLabel(
            "Keep track of your schedule, plans and important dates."
        )
        subtitle.setObjectName("Subtitle")

        heading_text.addWidget(title)
        heading_text.addWidget(subtitle)

        heading_layout.addLayout(heading_text)
        heading_layout.addStretch()

        self.today_button = QPushButton("Today")
        self.today_button.clicked.connect(self.go_to_today)
        heading_layout.addWidget(self.today_button)

        root.addLayout(heading_layout)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)

        calendar_panel = QFrame()
        calendar_panel.setObjectName("CalendarPanel")

        calendar_layout = QVBoxLayout(calendar_panel)
        calendar_layout.setContentsMargins(20, 16, 20, 16)
        calendar_layout.setSpacing(12)

        month_header = QHBoxLayout()
        month_header.setContentsMargins(0, 0, 0, 0)

        self.previous_month_button = QPushButton("‹")
        self.previous_month_button.setObjectName("MonthArrow")
        self.previous_month_button.clicked.connect(
            self.show_previous_month
        )

        self.month_heading = QLabel()
        self.month_heading.setObjectName("MonthHeading")
        self.month_heading.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.next_month_button = QPushButton("›")
        self.next_month_button.setObjectName("MonthArrow")
        self.next_month_button.clicked.connect(
            self.show_next_month
        )

        month_header.addStretch()
        month_header.addWidget(self.previous_month_button)
        month_header.addSpacing(12)
        month_header.addWidget(self.month_heading)
        month_header.addSpacing(12)
        month_header.addWidget(self.next_month_button)
        month_header.addStretch()

        calendar_layout.addLayout(month_header)

        self.calendar = QCalendarWidget()
        self.calendar.setNavigationBarVisible(False)
        self.calendar.setVerticalHeaderFormat(
            QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader
        )
        self.calendar.setHorizontalHeaderFormat(
            QCalendarWidget.HorizontalHeaderFormat.ShortDayNames
        )
        self.calendar.setGridVisible(True)
        self.calendar.setFirstDayOfWeek(
            Qt.DayOfWeek.Monday
        )
        self.calendar.setMinimumDate(QDate(2000, 1, 1))
        self.calendar.setMaximumDate(QDate(2100, 12, 31))
        self.calendar.setSelectedDate(QDate.currentDate())

        self.calendar.selectionChanged.connect(
            self.on_date_selected
        )
        self.calendar.currentPageChanged.connect(
            self.on_month_changed
        )

        calendar_layout.addWidget(self.calendar, 1)

        calendar_hint = QLabel(
            "Select a date to view its events."
        )
        calendar_hint.setStyleSheet(
            "color: #8A8C81; font-size: 11px; padding: 3px;"
        )
        calendar_layout.addWidget(calendar_hint)

        content_layout.addWidget(calendar_panel, 3)

        events_panel = QFrame()
        events_panel.setObjectName("CalendarPanel")

        events_layout = QVBoxLayout(events_panel)
        events_layout.setContentsMargins(20, 20, 20, 18)
        events_layout.setSpacing(11)

        self.events_heading = QLabel()
        self.events_heading.setObjectName("PanelTitle")
        events_layout.addWidget(self.events_heading)

        self.events_subtitle = QLabel()
        self.events_subtitle.setObjectName("EventCount")
        events_layout.addWidget(self.events_subtitle)

        self.events_list = QListWidget()

        self.events_list.itemSelectionChanged.connect(
            self.update_action_buttons
        )

        self.events_list.itemDoubleClicked.connect(
            lambda item: self.edit_selected_event()
        )
        events_layout.addWidget(self.events_list, 1)

        self.empty_label = QLabel(
            "Nothing scheduled for this date.\n"
            "Enjoy the breathing room!"
        )
        self.empty_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.empty_label.setStyleSheet("""
            color: #929489;
            font-size: 12px;
            padding: 12px;
            background-color: #F8F6F0;
            border-radius: 10px;
        """)
        events_layout.addWidget(self.empty_label, 1)

        self.add_button = QPushButton("+  Add event")
        self.add_button.setObjectName("PrimaryButton")
        self.add_button.clicked.connect(self.add_event)
        self.add_button.setMinimumHeight(42)
        events_layout.addWidget(self.add_button)

        action_layout = QHBoxLayout()
        action_layout.setSpacing(9)

        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(
            self.edit_selected_event
        )

        self.delete_button = QPushButton("Delete")
        self.delete_button.setObjectName("DeleteButton")
        self.delete_button.clicked.connect(
            self.delete_selected_event
        )

        action_layout.addWidget(self.edit_button)
        action_layout.addWidget(self.delete_button)

        events_layout.addLayout(action_layout)

        content_layout.addWidget(events_panel, 2)
        root.addLayout(content_layout, 1)

        self.update_month_heading()
        self.update_action_buttons()

    def update_month_heading(self):
        self.month_heading.setText(
            date(
                self.calendar.yearShown(),
                self.calendar.monthShown(),
                1,
            ).strftime("%B %Y")
        )

    def show_previous_month(self):
        self.calendar.showPreviousMonth()

    def show_next_month(self):
        self.calendar.showNextMonth()

    def on_month_changed(self, year, month):
        self.update_month_heading()
        self.refresh_calendar()

    def refresh_calendar(self):
        """Refresh date indicators and the selected date's events."""

        self.calendar.setDateTextFormat(
            QDate(),
            QTextCharFormat(),
        )

        year = self.calendar.yearShown()
        month = self.calendar.monthShown()

        month_start = date(year, month, 1)

        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)

        month_end = next_month - timedelta(days=1)

        events = self.calendar_service.get_events_between(
            datetime.combine(
                month_start,
                time.min,
            ).isoformat(),
            datetime.combine(
                month_end,
                time.max,
            ).isoformat(timespec="seconds"),
        )

        event_dates = set()

        for event in events:
            event_date = datetime.fromisoformat(
                event["start_datetime"]
            ).date()

            if month_start <= event_date <= month_end:
                event_dates.add(event_date)

        for event_date in event_dates:
            text_format = QTextCharFormat()
            text_format.setBackground(QColor("#E6EDE2"))
            text_format.setForeground(QColor("#344B32"))
            text_format.setFontWeight(QFont.Weight.Bold)

            self.calendar.setDateTextFormat(
                QDate(
                    event_date.year,
                    event_date.month,
                    event_date.day,
                ),
                text_format,
            )

        today = date.today()

        if today not in event_dates:
            today_format = QTextCharFormat()
            today_format.setForeground(QColor("#B66C83"))
            today_format.setFontWeight(QFont.Weight.Bold)

            self.calendar.setDateTextFormat(
                QDate(
                    today.year,
                    today.month,
                    today.day,
                ),
                today_format,
            )

        self.refresh_event_list()

    def refresh_event_list(self):
        self.events_list.clear()

        selected_qdate = self.calendar.selectedDate()

        self.selected_date = date(
            selected_qdate.year(),
            selected_qdate.month(),
            selected_qdate.day(),
        )

        start = datetime.combine(
            self.selected_date,
            time.min,
        ).isoformat()

        end = datetime.combine(
            self.selected_date,
            time.max,
        ).isoformat(timespec="seconds")

        events = self.calendar_service.get_events_between(
            start,
            end,
        )

        self.events_heading.setText(
            self.selected_date.strftime("%A, %d %B")
        )

        self.events_subtitle.setText(
            f"{len(events)} scheduled "
            f"{'event' if len(events) == 1 else 'events'}"
        )

        for event in events:
            start_time = datetime.fromisoformat(
                event["start_datetime"]
            ).strftime("%I:%M %p")

            if event.get("end_datetime"):
                end_time = datetime.fromisoformat(
                    event["end_datetime"]
                ).strftime("%I:%M %p")

                time_text = f"{start_time} – {end_time}"
            else:
                time_text = start_time

            category = event.get("category") or "General"

            item = QListWidgetItem(
                f"{event['title']}\n"
                f"{time_text}  •  {category}"
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                event["id"],
            )

            self.events_list.addItem(item)

        has_events = bool(events)

        self.events_list.setVisible(has_events)
        self.empty_label.setVisible(not has_events)

        self.update_action_buttons()

    def on_date_selected(self):
        self.refresh_event_list()

    def go_to_today(self):
        self.calendar.setCurrentPage(
            date.today().year,
            date.today().month,
        )
        self.calendar.setSelectedDate(QDate.currentDate())
        self.refresh_calendar()

    def add_event(self):
        if self.selected_date < date.today():
            MochiMessageDialog.show_message(
                self,
                "Past date",
                "You cannot add events to a past date.",
            )
            self.update_action_buttons()
            return

        dialog = EventDialog(
            parent=self,
            selected_date=self.selected_date,
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        data = dialog.get_event_data()

        try:
            self.calendar_service.create_event(**data)

        except (ValueError, TypeError) as error:
            MochiMessageDialog.show_message(
                self,
                "Unable to create event",
                str(error),
            )
            return

        except Exception as error:
            MochiMessageDialog.show_message(
                self,
                "Database error",
                f"The event could not be saved.\n\n{error}",
                danger=True,
            )
            return

        self.calendar.setCurrentPage(
            self.selected_date.year,
            self.selected_date.month,
        )

        self.refresh_calendar()

    def get_selected_event(self):
        item = self.events_list.currentItem()

        if item is None:
            return None

        event_id = item.data(
            Qt.ItemDataRole.UserRole
        )

        return self.calendar_service.get_event(event_id)

    def edit_selected_event(self):
        if self.selected_date < date.today():
            MochiMessageDialog.show_message(
                self,
                "Past date",
                "You cannot edit events on a past date.",
            )
            self.update_action_buttons()
            return

        event = self.get_selected_event()

        if event is None:
            return

        dialog = EventDialog(
            parent=self,
            event=event,
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        data = dialog.get_event_data()

        try:
            self.calendar_service.update_event(
                event_id=event["id"],
                **data,
            )

        except (ValueError, TypeError) as error:
            MochiMessageDialog.show_message(
                self,
                "Unable to update event",
                str(error),
            )
            return

        except Exception as error:
            MochiMessageDialog.show_message(
                self,
                "Database error",
                f"The event could not be updated.\n\n{error}",
                danger=True,
            )
            return

        self.refresh_calendar()

    def delete_selected_event(self):
        event = self.get_selected_event()

        if event is None:
            return

        answer = MochiMessageDialog.ask_confirmation(
            self,
            "Delete event",
            f"Are you sure you want to delete '{event['title']}'?",
            confirm_text="Delete",
            cancel_text="Cancel",
            danger=True,
        )

        if not answer:
            return

        try:
            self.calendar_service.delete_event(event["id"])

        except Exception as error:
            MochiMessageDialog.show_message(
                self,
                "Database error",
                f"The event could not be deleted.\n\n{error}",
                danger=True,
            )
            return

        self.refresh_calendar()

    def update_action_buttons(self):
        """Enable or disable event actions based on the selected date."""

        if not all(
            hasattr(self, name)
            for name in (
                "add_button",
                "edit_button",
                "delete_button",
                "events_list",
                "calendar",
            )
        ):
            return

        selected_date = self.calendar.selectedDate().toPython()
        today = date.today()

        is_past_date = selected_date < today
        has_selection = self.events_list.currentItem() is not None

        self.add_button.setEnabled(not is_past_date)

        self.edit_button.setEnabled(
            has_selection and not is_past_date
        )

        self.delete_button.setEnabled(has_selection)

        self.add_button.setToolTip(
            "You cannot add events to past dates."
            if is_past_date else "Add an event"
        )

        self.edit_button.setToolTip(
            "You cannot edit events on past dates."
            if is_past_date else "Edit selected event"
        )

        self.delete_button.setToolTip(
            "Delete selected event"
            if has_selection else "Select an event to delete"
        )
