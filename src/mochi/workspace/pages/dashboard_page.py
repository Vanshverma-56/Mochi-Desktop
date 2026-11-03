from datetime import date, datetime
from math import cos, sin, pi

from PySide6.QtCore import Qt, QTimer, QPointF, QTime
from PySide6.QtGui import QPainter, QPen
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QProgressBar,
    QSizePolicy,
)


class AnalogClock(QWidget):
    """A native analogue clock that displays the computer's local time."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 120)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        radius = min(self.width(), self.height()) / 2 - 5
        painter.translate(self.width() / 2, self.height() / 2)

        # Clock face
        painter.setPen(QPen(Qt.GlobalColor.transparent))
        painter.setBrush(Qt.GlobalColor.white)
        painter.drawEllipse(QPointF(0, 0), radius, radius)

        # Outer ring
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(Qt.GlobalColor.lightGray, 1.5))
        painter.drawEllipse(QPointF(0, 0), radius, radius)

        # Hour markers
        for hour in range(12):
            angle = hour * 2 * pi / 12 - pi / 2

            outer = radius * 0.88
            inner = radius * (0.76 if hour % 3 == 0 else 0.82)

            start = QPointF(
                cos(angle) * inner,
                sin(angle) * inner,
            )
            end = QPointF(
                cos(angle) * outer,
                sin(angle) * outer,
            )

            width = 2.5 if hour % 3 == 0 else 1.2

            painter.setPen(
                QPen(
                    Qt.GlobalColor.darkGray,
                    width,
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                )
            )
            painter.drawLine(start, end)

        now = QTime.currentTime()

        hour_angle = (
            (now.hour() % 12 + now.minute() / 60)
            * 2 * pi / 12 - pi / 2
        )

        minute_angle = (
            (now.minute() + now.second() / 60)
            * 2 * pi / 60 - pi / 2
        )

        second_angle = (
            now.second() * 2 * pi / 60 - pi / 2
        )

        # Hour hand
        painter.setPen(
            QPen(
                Qt.GlobalColor.darkGray,
                5,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )
        painter.drawLine(
            QPointF(0, 0),
            QPointF(
                cos(hour_angle) * radius * 0.46,
                sin(hour_angle) * radius * 0.46,
            ),
        )

        # Minute hand
        painter.setPen(
            QPen(
                Qt.GlobalColor.darkGray,
                3,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )
        painter.drawLine(
            QPointF(0, 0),
            QPointF(
                cos(minute_angle) * radius * 0.68,
                sin(minute_angle) * radius * 0.68,
            ),
        )

        # Second hand
        painter.setPen(
            QPen(
                Qt.GlobalColor.red,
                1.5,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )
        painter.drawLine(
            QPointF(0, 0),
            QPointF(
                cos(second_angle) * radius * 0.76,
                sin(second_angle) * radius * 0.76,
            ),
        )

        # Centre point
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(Qt.GlobalColor.darkGray)
        painter.drawEllipse(QPointF(0, 0), 4, 4)


class DashboardPage(QWidget):
    def __init__(self, task_service, navigate_callback=None):
        super().__init__()

        self.task_service = task_service
        self.navigate_callback = navigate_callback
        self.clock_mode = "analog"

        self.setStyleSheet("""
            QWidget {
                color: #292F2A;
                font-family: "Segoe UI";
            }

            QLabel#Muted {
                color: #747D70;
            }

            QLabel#SectionTitle {
                color: #354B38;
                font-size: 16px;
                font-weight: bold;
            }

            QLabel#MetricValue {
                color: #FFFFFF;
                font-size: 27px;
                font-weight: bold;
            }

            QLabel#MetricHeading {
                color: #E7EEE3;
                font-size: 11px;
                font-weight: 600;
            }

            QLabel#TaskTitle {
                color: #303A31;
                font-size: 12px;
                font-weight: bold;
            }

            QLabel#TaskDetails {
                color: #788174;
                font-size: 10px;
            }

            QFrame#WelcomeCard {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #E5EBDD,
                    stop: 0.55 #F1EAE0,
                    stop: 1 #F4E2E2
                );
                border: 1px solid #D9E0D1;
                border-radius: 18px;
            }

            QFrame#MetricCard {
                background-color: #586E55;
                border: 1px solid #50654D;
                border-radius: 15px;
            }

            QFrame#MetricCard:hover {
                background-color: #647B60;
                border: 1px solid #71866C;
            }

            QFrame#ContentCard,
            QFrame#ShortcutCard {
                background-color: #FFFCF6;
                border: 1px solid #DEDCCF;
                border-radius: 15px;
            }

            QFrame#ContentCard {
                border-top: 3px solid #84977A;
            }

            QFrame#ClockCard {
                background-color: #EAF0E5;
                border: 1px solid #D4DFCE;
                border-top: 3px solid #71896B;
                border-radius: 15px;
            }

            QPushButton#TextButton {
                background-color: transparent;
                color: #526D4E;
                border: none;
                font-weight: bold;
                padding: 5px;
            }

            QPushButton#TextButton:hover {
                color: #283F2C;
            }

            QPushButton#ClockToggle {
                background-color: #DCE8D6;
                color: #405C3E;
                border: 1px solid #C7D8BF;
                border-radius: 9px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: bold;
            }

            QPushButton#ClockToggle:hover {
                background-color: #CCDCC5;
            }

            QProgressBar {
                background-color: #E2E8DC;
                border: none;
                border-radius: 5px;
                height: 9px;
            }

            QProgressBar::chunk {
                background-color: #718B68;
                border-radius: 5px;
            }
        """)

        self.build_interface()
        self.refresh_dashboard()
        self.update_clock()

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)

    def build_interface(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 8, 14, 8)
        root.setSpacing(10)

        # HEADER
        header = QHBoxLayout()
        header.setSpacing(10)

        header_text = QVBoxLayout()
        header_text.setSpacing(1)

        self.date_label = QLabel()
        self.date_label.setObjectName("Muted")
        self.date_label.setStyleSheet(
            "font-size: 11px; font-weight: 600;"
        )

        self.greeting_label = QLabel()
        self.greeting_label.setStyleSheet(
            "font-size: 27px; font-weight: bold; color: #354B38;"
        )

        self.subtitle_label = QLabel(
            "A little progress goes a long way."
        )
        self.subtitle_label.setObjectName("Muted")
        self.subtitle_label.setStyleSheet("font-size: 12px;")

        header_text.addWidget(self.date_label)
        header_text.addWidget(self.greeting_label)
        header_text.addWidget(self.subtitle_label)

        header.addLayout(header_text)
        header.addStretch()

        root.addLayout(header)

        # WELCOME CARD
        welcome = QFrame()
        welcome.setObjectName("WelcomeCard")
        welcome.setFixedHeight(100)

        welcome_layout = QHBoxLayout(welcome)
        welcome_layout.setContentsMargins(20, 12, 20, 12)
        welcome_layout.setSpacing(14)

        welcome_icon = QLabel("✿")
        welcome_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_icon.setFixedSize(50, 50)
        welcome_icon.setStyleSheet("""
            background-color: #F3DCDD;
            color: #B76F72;
            border-radius: 25px;
            font-size: 26px;
        """)

        welcome_text = QVBoxLayout()
        welcome_text.setSpacing(5)

        welcome_title = QLabel("Your day, at your own pace.")
        welcome_title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #354B38;"
        )

        welcome_description = QLabel(
            "Make room for what matters. "
            "Mochi is here to keep everything in one place."
        )
        welcome_description.setWordWrap(True)
        welcome_description.setStyleSheet(
            "font-size: 12px; color: #626F60;"
        )

        welcome_text.addWidget(welcome_title)
        welcome_text.addWidget(welcome_description)

        welcome_layout.addWidget(welcome_icon)
        welcome_layout.addLayout(welcome_text, 1)

        paw = QLabel("🐾")
        paw.setStyleSheet("font-size: 22px;")
        welcome_layout.addWidget(paw)

        root.addWidget(welcome)

        # METRIC CARDS
        metrics = QHBoxLayout()
        metrics.setSpacing(10)

        self.total_value = self.create_metric_card(
            metrics, "▤", "Total tasks"
        )
        self.active_value = self.create_metric_card(
            metrics, "▶", "Active"
        )
        self.completed_value = self.create_metric_card(
            metrics, "✓", "Completed"
        )
        self.overdue_value = self.create_metric_card(
            metrics, "!", "Overdue"
        )

        root.addLayout(metrics)

        # PROGRESS
        progress_card = QFrame()
        progress_card.setObjectName("ContentCard")
        progress_card.setFixedHeight(83)

        progress_layout = QVBoxLayout(progress_card)
        progress_layout.setContentsMargins(15, 9, 15, 9)
        progress_layout.setSpacing(5)

        progress_header = QHBoxLayout()

        progress_title = QLabel("▥  Your progress")
        progress_title.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #40583F;"
        )

        self.progress_label = QLabel("0%")
        self.progress_label.setStyleSheet(
            "font-size: 17px; font-weight: bold; color: #40583F;"
        )

        progress_header.addWidget(progress_title)
        progress_header.addStretch()
        progress_header.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False)

        self.progress_detail = QLabel("0 of 0 tasks completed")
        self.progress_detail.setObjectName("Muted")
        self.progress_detail.setStyleSheet("font-size: 10px;")

        progress_layout.addLayout(progress_header)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_detail)

        root.addWidget(progress_card)

        # MAIN DASHBOARD
        main_row = QHBoxLayout()
        main_row.setSpacing(12)

        # LEFT COLUMN: CLOCK ABOVE TODAY'S TASKS
        left_column = QVBoxLayout()
        left_column.setSpacing(10)

        # CLOCK PANEL
        clock_card = QFrame()
        clock_card.setObjectName("ClockCard")
        clock_card.setFixedHeight(195)

        clock_layout = QVBoxLayout(clock_card)
        clock_layout.setContentsMargins(14, 9, 14, 9)
        clock_layout.setSpacing(3)

        clock_header = QHBoxLayout()

        clock_title = QLabel("◷  Your time")
        clock_title.setStyleSheet(
            "font-size: 15px; font-weight: bold; color: #40583F;"
        )

        self.clock_toggle = QPushButton("Digital 24h")
        self.clock_toggle.setObjectName("ClockToggle")
        self.clock_toggle.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.clock_toggle.clicked.connect(self.toggle_clock_mode)

        clock_header.addWidget(clock_title)
        clock_header.addStretch()
        clock_header.addWidget(self.clock_toggle)

        clock_layout.addLayout(clock_header)

        self.analog_clock = AnalogClock()

        self.digital_clock = QLabel()
        self.digital_clock.setFixedHeight(120)
        self.digital_clock.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.digital_clock.setStyleSheet(
            "font-size: 34px; font-weight: bold; color: #354B38;"
        )
        self.digital_clock.hide()

        self.clock_date = QLabel()
        self.clock_date.setFixedHeight(18)
        self.clock_date.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.clock_date.setObjectName("Muted")
        self.clock_date.setStyleSheet(
            "font-size: 10px; color: #65745F;"
        )

        clock_layout.addWidget(
            self.analog_clock,
            0,
            Qt.AlignmentFlag.AlignCenter,
        )
        clock_layout.addWidget(
            self.digital_clock,
            0,
            Qt.AlignmentFlag.AlignCenter,
        )
        clock_layout.addWidget(
            self.clock_date,
            0,
            Qt.AlignmentFlag.AlignCenter,
        )

        left_column.addWidget(clock_card)

        # TODAY'S TASKS PANEL
        today_card = self.create_panel("▦", "Today's tasks")
        today_card.setMinimumHeight(135)

        today_layout = today_card.layout()

        self.today_tasks_layout = QVBoxLayout()
        self.today_tasks_layout.setSpacing(5)

        today_layout.addLayout(self.today_tasks_layout)
        today_layout.addStretch()

        today_button = QPushButton("View all tasks  →")
        today_button.setObjectName("TextButton")
        today_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        today_button.clicked.connect(self.open_tasks)

        today_layout.addWidget(
            today_button,
            alignment=Qt.AlignmentFlag.AlignRight,
        )

        left_column.addWidget(today_card, 1)

        main_row.addLayout(left_column, 1)

        # RIGHT COLUMN: UPCOMING DEADLINES
        upcoming_card = self.create_panel(
            "◷", "Upcoming deadlines"
        )
        upcoming_card.setMinimumHeight(340)

        upcoming_layout = upcoming_card.layout()

        self.upcoming_tasks_layout = QVBoxLayout()
        self.upcoming_tasks_layout.setSpacing(8)

        upcoming_layout.addLayout(self.upcoming_tasks_layout)
        upcoming_layout.addStretch()

        upcoming_button = QPushButton("View all tasks  →")
        upcoming_button.setObjectName("TextButton")
        upcoming_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        upcoming_button.clicked.connect(self.open_tasks)

        upcoming_layout.addWidget(
            upcoming_button,
            alignment=Qt.AlignmentFlag.AlignRight,
        )

        main_row.addWidget(upcoming_card, 1)

        root.addLayout(main_row, 1)

        # QUICK ACCESS
        shortcuts = QHBoxLayout()
        shortcuts.setSpacing(10)

        self.create_shortcut(shortcuts, "▦", "Calendar", "Calendar")
        self.create_shortcut(shortcuts, "▤", "Notes", "Notes")
        self.create_shortcut(shortcuts, "◷", "Focus", "Focus")
        self.create_shortcut(shortcuts, "▣", "Logbook", "Logbook")

        root.addLayout(shortcuts)

    def create_metric_card(self, layout, icon, title):
        card = QFrame()
        card.setObjectName("MetricCard")
        card.setFixedHeight(82)

        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(12, 8, 10, 8)
        card_layout.setSpacing(10)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedSize(40, 40)
        icon_label.setStyleSheet("""
            background-color: #E4EBDD;
            color: #526B4D;
            border-radius: 20px;
            font-size: 19px;
            font-weight: bold;
        """)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)

        value = QLabel("0")
        value.setObjectName("MetricValue")

        heading = QLabel(title)
        heading.setObjectName("MetricHeading")

        text_layout.addWidget(value)
        text_layout.addWidget(heading)

        card_layout.addWidget(icon_label)
        card_layout.addLayout(text_layout, 1)

        layout.addWidget(card, 1)
        return value

    def create_panel(self, icon, title):
        card = QFrame()
        card.setObjectName("ContentCard")
        card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 10, 14, 10)
        card_layout.setSpacing(7)

        heading = QLabel(f"{icon}  {title}")
        heading.setObjectName("SectionTitle")

        card_layout.addWidget(heading)

        return card

    def create_shortcut(self, layout, icon, title, page_name):
        card = QFrame()
        card.setObjectName("ShortcutCard")
        card.setFixedHeight(48)

        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(10, 5, 10, 5)
        card_layout.setSpacing(7)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet(
            "font-size: 17px; color: #71896B;"
        )

        button = QPushButton(title)
        button.setObjectName("TextButton")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(
            lambda checked=False, name=page_name: self.open_page(name)
        )

        card_layout.addWidget(icon_label)
        card_layout.addWidget(button)
        card_layout.addStretch()

        layout.addWidget(card, 1)

    # CLOCK
    def toggle_clock_mode(self):
        if self.clock_mode == "analog":
            self.clock_mode = "digital"
            self.analog_clock.hide()
            self.digital_clock.show()
            self.clock_toggle.setText("Analogue")
        else:
            self.clock_mode = "analog"
            self.digital_clock.hide()
            self.analog_clock.show()
            self.clock_toggle.setText("Digital 24h")

    def update_clock(self):
        now = datetime.now()

        if now.hour < 12:
            greeting = "Good morning!"
        elif now.hour < 17:
            greeting = "Good afternoon!"
        else:
            greeting = "Good evening!"

        self.greeting_label.setText(greeting)

        self.date_label.setText(
            now.strftime("%A, %d %B %Y").upper()
        )

        self.digital_clock.setText(now.strftime("%H:%M:%S"))
        self.clock_date.setText(now.strftime("%A, %d %B %Y"))

        self.analog_clock.update()

    # TASK DATA
    def parse_due_date(self, value):
        if not value:
            return None

        value = str(value).strip()

        formats = (
            "%Y-%m-%d",
            "%d-%m-%Y",
            "%Y/%m/%d",
            "%d/%m/%Y",
        )

        for date_format in formats:
            try:
                return datetime.strptime(value, date_format).date()
            except ValueError:
                continue

        try:
            return datetime.fromisoformat(value).date()
        except ValueError:
            return None

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

            elif item.layout() is not None:
                self.clear_layout(item.layout())

    def add_empty_message(self, layout, message):
        label = QLabel(message)
        label.setObjectName("Muted")
        label.setWordWrap(True)
        label.setStyleSheet(
            "font-size: 11px; padding: 3px 0;"
        )

        layout.addWidget(label)

    def add_task_row(self, layout, task, detail):
        row = QFrame()

        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 3, 0, 3)
        row_layout.setSpacing(7)

        priority = task.get("priority", "Medium")

        colours = {
            "High": "#C66B60",
            "Medium": "#B28B4E",
            "Low": "#758B6D",
        }

        indicator = QLabel("●")
        indicator.setStyleSheet(
            f"color: {colours.get(priority, '#85847B')};"
            "font-size: 10px;"
        )

        text_layout = QVBoxLayout()
        text_layout.setSpacing(1)

        title = QLabel(task.get("title", "Untitled task"))
        title.setObjectName("TaskTitle")
        title.setWordWrap(True)

        details = QLabel(
            f"{detail}  ·  {priority} priority"
        )
        details.setObjectName("TaskDetails")
        details.setWordWrap(True)

        text_layout.addWidget(title)
        text_layout.addWidget(details)

        row_layout.addWidget(
            indicator,
            alignment=Qt.AlignmentFlag.AlignTop,
        )
        row_layout.addLayout(text_layout, 1)

        layout.addWidget(row)

    def refresh_dashboard(self):
        tasks = self.task_service.get_all_tasks()
        today = date.today()

        completed = [
            task for task in tasks if task.get("is_completed")
        ]

        active = [
            task for task in tasks if not task.get("is_completed")
        ]

        dated_active = []

        for task in active:
            due_date = self.parse_due_date(
                task.get("due_date")
            )

            if due_date is not None:
                dated_active.append((due_date, task))

        overdue = [
            item for item in dated_active if item[0] < today
        ]

        today_tasks = [
            item for item in dated_active if item[0] == today
        ]

        upcoming = [
            item for item in dated_active if item[0] > today
        ]

        priority_order = {
            "High": 0,
            "Medium": 1,
            "Low": 2,
        }

        sort_key = lambda item: (
            item[0],
            priority_order.get(
                item[1].get("priority", "Medium"), 1
            ),
        )

        today_tasks.sort(key=sort_key)
        upcoming.sort(key=sort_key)

        total_count = len(tasks)
        completed_count = len(completed)

        self.total_value.setText(str(total_count))
        self.active_value.setText(str(len(active)))
        self.completed_value.setText(str(completed_count))
        self.overdue_value.setText(str(len(overdue)))

        progress = (
            round(completed_count / total_count * 100)
            if total_count else 0
        )

        self.progress_bar.setValue(progress)
        self.progress_label.setText(f"{progress}%")

        self.progress_detail.setText(
            f"{completed_count} of {total_count} tasks completed"
        )

        # Today's panel: show no more than two tasks.
        self.clear_layout(self.today_tasks_layout)

        if today_tasks:
            for due_date, task in today_tasks[:2]:
                self.add_task_row(
                    self.today_tasks_layout,
                    task,
                    "Due today",
                )
        else:
            self.add_empty_message(
                self.today_tasks_layout,
                "Nothing scheduled for today. Enjoy the breathing room!",
            )

        # Upcoming panel: show up to three deadlines.
        self.clear_layout(self.upcoming_tasks_layout)

        if upcoming:
            for due_date, task in upcoming[:3]:
                self.add_task_row(
                    self.upcoming_tasks_layout,
                    task,
                    due_date.strftime("%d %b"),
                )
        else:
            self.add_empty_message(
                self.upcoming_tasks_layout,
                "No upcoming deadlines. You're all clear!",
            )

    # NAVIGATION
    def open_tasks(self):
        self.open_page("Tasks")

    def open_page(self, page_name):
        if self.navigate_callback:
            self.navigate_callback(page_name)

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_dashboard()