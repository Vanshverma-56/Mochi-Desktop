
from datetime import date, datetime, timedelta

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QFrame,
    QDialog,
    QCalendarWidget,
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QPainter, QTextCharFormat


BACKGROUND = "#F5F1E9"
CARD_BACKGROUND = "#FFFCF6"
CARD_BORDER = "#E9E2D6"
TEXT_PRIMARY = "#292B28"
TEXT_SECONDARY = "#77796F"
FOREST_GREEN = "#596B55"


class LogbookDatePickerDialog(QDialog):
    """Styled calendar for selecting a Logbook date."""

    def __init__(self, parent=None, selected_date=None, saved_dates=None):
        super().__init__(parent)

        self.setWindowTitle("Choose Date")
        self.setFixedWidth(390)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        heading = QLabel("Choose a day")
        heading.setStyleSheet("""
            color: #292B28;
            font-size: 19px;
            font-weight: bold;
            background: transparent;
        """)

        subtitle = QLabel(
            "Select a date to view or write your daily entry."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("""
            color: #77796F;
            font-size: 12px;
            background: transparent;
        """)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(False)
        self.calendar.setFirstDayOfWeek(Qt.DayOfWeek.Monday)
        self.calendar.setVerticalHeaderFormat(
            QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader
        )

        self.calendar.setMinimumDate(QDate(2000, 1, 1))
        self.calendar.setMaximumDate(QDate(2100, 12, 31))

        if selected_date is None:
            selected_date = QDate.currentDate()

        self.calendar.setSelectedDate(selected_date)
        self.calendar.setCurrentPage(
            selected_date.year(),
            selected_date.month(),
        )

        # Highlight dates that already have saved Logbook entries.
        saved_format = QTextCharFormat()
        saved_format.setBackground(QColor("#DCE8D7"))
        saved_format.setForeground(QColor("#435A3F"))
        saved_format.setFontWeight(700)

        for entry_date in saved_dates or []:
            saved_qdate = QDate.fromString(
                entry_date,
                Qt.DateFormat.ISODate,
            )

            if saved_qdate.isValid():
                self.calendar.setDateTextFormat(
                    saved_qdate,
                    saved_format,
                )

        self.calendar.setStyleSheet("""
            QCalendarWidget QWidget {
                background-color: #FFFCF6;
                color: #292B28;
                alternate-background-color: #F5F1E9;
            }

            QCalendarWidget QToolButton {
                background-color: #596B55;
                color: white;
                border: none;
                border-radius: 7px;
                padding: 7px;
                font-weight: bold;
                min-height: 24px;
            }

            QCalendarWidget QToolButton:hover {
                background-color: #465843;
            }

            QCalendarWidget QSpinBox {
                background-color: #FFFCF6;
                color: #292B28;
                border: 1px solid #E9E2D6;
                border-radius: 5px;
                padding: 4px;
            }

            QCalendarWidget QAbstractItemView {
                background-color: #FFFCF6;
                color: #292B28;
                selection-background-color: #596B55;
                selection-color: white;
                outline: 0;
                font-size: 13px;
                font-family: "Segoe UI";
            }

            QCalendarWidget QAbstractItemView:disabled {
                color: #C9C5BB;
                background-color: #F5F1E9;
            }
        """)

        self.calendar.clicked.connect(self.accept)

        legend = QHBoxLayout()
        legend.setSpacing(7)

        legend_dot = QLabel("●")
        legend_dot.setStyleSheet("""
            color: #829B77;
            font-size: 13px;
            background: transparent;
        """)

        legend_text = QLabel("Saved entry")
        legend_text.setStyleSheet("""
            color: #77796F;
            font-size: 11px;
            background: transparent;
        """)

        legend.addWidget(legend_dot)
        legend.addWidget(legend_text)
        legend.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #E8E4DA;
                color: #45483F;
                border: none;
                border-radius: 8px;
                padding: 9px 17px;
            }
            QPushButton:hover {
                background-color: #DCDDD1;
            }
        """)
        cancel_button.clicked.connect(self.reject)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)

        layout.addWidget(heading)
        layout.addWidget(subtitle)
        layout.addWidget(self.calendar)
        layout.addLayout(legend)
        layout.addLayout(button_layout)

        self.setStyleSheet("""
            QDialog {
                background-color: #F5F1E9;
                border: 1px solid #E9E2D6;
                border-radius: 14px;
            }
        """)

    def selected_date(self):
        return self.calendar.selectedDate()


class LogbookPage(QWidget):
    """Daily journal for recording thoughts and activities."""

    def __init__(self, logbook_service):
        super().__init__()

        self.logbook_service = logbook_service
        self.current_date = date.today()

        self.build_interface()
        self.load_entry()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(BACKGROUND))

    def build_interface(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(10, 10, 10, 10)
        main.setSpacing(14)

        heading = QLabel("▤  Daily Logbook")
        heading.setStyleSheet("""
            font-size: 29px;
            font-weight: bold;
            color: #292B28;
            background: transparent;
        """)

        subtitle = QLabel(
            "A little space to remember what each day was like."
        )
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #77796F;
            background: transparent;
        """)

        main.addWidget(heading)
        main.addWidget(subtitle)

        # Date navigation card.
        date_card = QFrame()
        date_card.setObjectName("DateCard")
        date_card.setStyleSheet("""
            QFrame#DateCard {
                background-color: #FFFCF6;
                border: 1px solid #E9E2D6;
                border-radius: 13px;
            }
        """)

        date_layout = QHBoxLayout(date_card)
        date_layout.setContentsMargins(15, 11, 15, 11)
        date_layout.setSpacing(10)

        self.previous_button = QPushButton("‹")
        self.previous_button.setObjectName("NavigationButton")
        self.previous_button.setFixedSize(40, 38)
        self.previous_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.previous_button.clicked.connect(
            lambda: self.change_date(-1)
        )

        self.date_picker = QPushButton()
        self.date_picker.setObjectName("DateButton")
        self.date_picker.setMinimumHeight(40)
        self.date_picker.setMinimumWidth(245)
        self.date_picker.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.date_picker.clicked.connect(self.open_date_picker)

        self.next_button = QPushButton("›")
        self.next_button.setObjectName("NavigationButton")
        self.next_button.setFixedSize(40, 38)
        self.next_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.next_button.clicked.connect(
            lambda: self.change_date(1)
        )

        self.today_button = QPushButton("Today")
        self.today_button.setObjectName("TodayButton")
        self.today_button.setMinimumHeight(38)
        self.today_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.today_button.clicked.connect(self.go_to_today)

        date_layout.addWidget(self.previous_button)
        date_layout.addWidget(self.date_picker)
        date_layout.addWidget(self.next_button)
        date_layout.addStretch()
        date_layout.addWidget(self.today_button)

        main.addWidget(date_card)

        # Entry editor card.
        editor_card = QFrame()
        editor_card.setObjectName("LogbookCard")
        editor_card.setStyleSheet("""
            QFrame#LogbookCard {
                background-color: #FFFCF6;
                border: 1px solid #E9E2D6;
                border-radius: 16px;
            }
            QLabel {
                background: transparent;
                border: none;
            }
        """)

        editor = QVBoxLayout(editor_card)
        editor.setContentsMargins(22, 20, 22, 20)
        editor.setSpacing(12)

        self.entry_heading = QLabel("")
        self.entry_heading.setStyleSheet("""
            font-size: 19px;
            font-weight: bold;
            color: #292B28;
        """)

        title_label = QLabel("Today's title")
        title_label.setStyleSheet(
            "font-size: 12px; color: #77796F;"
        )

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText(
            "Give this day a title (optional)"
        )
        self.title_input.setMinimumHeight(42)

        content_label = QLabel("Your thoughts")
        content_label.setStyleSheet(
            "font-size: 12px; color: #77796F;"
        )

        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText(
            "What happened today?\n\n"
            "What did you accomplish?\n\n"
            "Anything you want to remember?"
        )
        self.content_input.setMinimumHeight(300)

        self.status_label = QLabel(" ")
        self.status_label.setStyleSheet("""
            color: #77796F;
            font-size: 11px;
            background: transparent;
        """)

        actions = QHBoxLayout()
        actions.addWidget(self.status_label)
        actions.addStretch()

        self.save_button = QPushButton("Save Entry")
        self.save_button.setObjectName("SaveButton")
        self.save_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.save_button.clicked.connect(self.save_entry)

        actions.addWidget(self.save_button)

        editor.addWidget(self.entry_heading)
        editor.addWidget(title_label)
        editor.addWidget(self.title_input)
        editor.addWidget(content_label)
        editor.addWidget(self.content_input, 1)
        editor.addLayout(actions)

        main.addWidget(editor_card, 1)

        # Page-wide styling.
        self.setStyleSheet("""
            QLineEdit, QTextEdit {
                background-color: #FFFCF6;
                color: #292B28;
                border: 1px solid #E9E2D6;
                border-radius: 9px;
                padding: 9px;
                font-size: 13px;
            }

            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #81917B;
            }

            QPushButton {
                background-color: #EAE5DA;
                color: #454940;
                border: 1px solid #E4DED2;
                border-radius: 9px;
                padding: 9px 14px;
                font-size: 12px;
            }

            QPushButton:hover {
                background-color: #DDD7CA;
            }

            QPushButton#NavigationButton,
            QPushButton#TodayButton {
                background-color: #596B55;
                color: white;
                border: none;
                border-radius: 9px;
                font-weight: bold;
            }

            QPushButton#NavigationButton {
                font-size: 23px;
                padding: 0px;
            }

            QPushButton#NavigationButton:hover,
            QPushButton#TodayButton:hover {
                background-color: #465843;
            }

            QPushButton#DateButton {
                background-color: #E9EFE5;
                color: #43553F;
                border: 1px solid #D5E0D0;
                border-radius: 9px;
                font-size: 13px;
                font-weight: bold;
                padding: 8px 13px;
            }

            QPushButton#DateButton:hover {
                background-color: #DDE8D8;
            }

            QPushButton#SaveButton {
                background-color: #596B55;
                color: white;
                border: none;
                font-weight: bold;
                padding: 11px 22px;
            }

            QPushButton#SaveButton:hover {
                background-color: #465843;
            }
        """)

        self.update_date_button()

    def update_date_button(self):
        self.date_picker.setText(
            self.current_date.strftime("%A, %d %B %Y") + "  ▾"
        )

    def open_date_picker(self):
        saved_dates = [
            entry["entry_date"]
            for entry in self.logbook_service.get_all_entries()
        ]

        selected = QDate(
            self.current_date.year,
            self.current_date.month,
            self.current_date.day,
        )

        dialog = LogbookDatePickerDialog(
            self,
            selected_date=selected,
            saved_dates=saved_dates,
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            chosen = dialog.selected_date()

            self.date_picker.setFocus()
            self.set_current_date(
                date(chosen.year(), chosen.month(), chosen.day())
            )

    def change_date(self, days):
        new_date = self.current_date + timedelta(days=days)
        self.set_current_date(new_date)

    def go_to_today(self):
        self.set_current_date(date.today())

    def set_current_date(self, new_date):
        if new_date == self.current_date:
            return

        self.current_date = new_date
        self.update_date_button()
        self.load_entry()

    def load_entry(self):
        entry_date = self.current_date.isoformat()
        entry = self.logbook_service.get_entry(entry_date)

        self.entry_heading.setText(
            self.current_date.strftime("%A, %d %B %Y")
        )

        self.title_input.clear()
        self.content_input.clear()

        if entry:
            self.title_input.setText(entry["title"] or "")
            self.content_input.setPlainText(entry["content"] or "")
            self.status_label.setText(
                "Saved entry · " + self.format_timestamp(
                    entry["updated_at"]
                )
            )
        else:
            self.status_label.setText(
                "No entry saved for this day yet."
            )

    def save_entry(self):
        try:
            entry = self.logbook_service.save_entry(
                self.current_date.isoformat(),
                self.title_input.text(),
                self.content_input.toPlainText(),
            )
        except ValueError as error:
            self.status_label.setText(str(error))
            return

        self.status_label.setText(
            "Saved just now · "
            + self.format_timestamp(entry["updated_at"])
        )

    @staticmethod
    def format_timestamp(timestamp):
        try:
            value = datetime.fromisoformat(timestamp)
            return value.strftime("%d %b %Y, %I:%M %p")
        except (TypeError, ValueError):
            return "Saved"
