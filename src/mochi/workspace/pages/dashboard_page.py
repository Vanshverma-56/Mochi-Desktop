from datetime import date, datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QProgressBar,
    QScrollArea,
    QSizePolicy,
)

from mochi.services.task_service import TaskService


class DashboardPage(QWidget):
    def __init__(self, task_service: TaskService, navigate_callback=None):
        super().__init__()

        self.task_service = task_service
        self.navigate_callback = navigate_callback

        self.setStyleSheet("""
            QWidget {
                color: #292B28;
            }

            QFrame#WelcomeCard {
                background-color: #E7DDCC;
                border-radius: 18px;
            }

            QFrame#MetricCard,
            QFrame#ContentCard {
                background-color: #FFFCF6;
                border: 1px solid #E9E2D6;
                border-radius: 16px;
            }

            QLabel#Muted {
                color: #85847B;
            }

            QLabel#MetricValue {
                font-size: 27px;
                font-weight: bold;
                color: #30382F;
            }

            QLabel#SectionTitle {
                font-size: 17px;
                font-weight: bold;
                color: #30382F;
            }

            QLabel#TaskTitle {
                font-size: 13px;
                font-weight: bold;
                color: #343730;
            }

            QLabel#TaskDetails {
                font-size: 11px;
                color: #85847B;
            }

            QPushButton#TextButton {
                background-color: transparent;
                color: #63785D;
                border: none;
                font-weight: bold;
                padding: 5px;
            }

            QPushButton#TextButton:hover {
                color: #354B32;
            }

            QProgressBar {
                background-color: #EAE5DA;
                border: none;
                border-radius: 5px;
                height: 9px;
                text-align: center;
            }

            QProgressBar::chunk {
                background-color: #758B6D;
                border-radius: 5px;
            }

            QScrollArea {
                border: none;
                background: transparent;
            }
        """)

        self.build_interface()
        self.refresh_dashboard()

        # Keep the clock updated.
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)

    def build_interface(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(10, 10, 14, 15)
        layout.setSpacing(17)

        # Header
        header_layout = QHBoxLayout()

        header_text = QVBoxLayout()
        self.greeting_label = QLabel()
        self.greeting_label.setStyleSheet(
            "font-size: 28px; font-weight: bold;"
        )

        self.date_label = QLabel()
        self.date_label.setObjectName("Muted")
        self.date_label.setStyleSheet("font-size: 13px;")

        header_text.addWidget(self.greeting_label)
        header_text.addWidget(self.date_label)

        self.clock_label = QLabel()
        self.clock_label.setAlignment(
            Qt.AlignmentFlag.AlignRight |
            Qt.AlignmentFlag.AlignVCenter
        )
        self.clock_label.setStyleSheet(
            "font-size: 19px; font-weight: bold; color: #63785D;"
        )

        header_layout.addLayout(header_text)
        header_layout.addStretch()
        header_layout.addWidget(self.clock_label)

        layout.addLayout(header_layout)

        # Welcome card
        welcome = QFrame()
        welcome.setObjectName("WelcomeCard")
        welcome.setMinimumHeight(115)

        welcome_layout = QVBoxLayout(welcome)
        welcome_layout.setContentsMargins(23, 18, 23, 18)
        welcome_layout.setSpacing(7)

        welcome_title = QLabel("Your day, at your own pace.")
        welcome_title.setStyleSheet(
            "font-size: 21px; font-weight: bold; color: #30382F;"
        )

        welcome_description = QLabel(
            "A little progress each day adds up to something wonderful."
        )
        welcome_description.setWordWrap(True)
        welcome_description.setStyleSheet(
            "font-size: 13px; color: #65675D;"
        )

        welcome_layout.addWidget(welcome_title)
        welcome_layout.addWidget(welcome_description)

        layout.addWidget(welcome)

        # Task overview
        overview_title = QLabel("Your overview")
        overview_title.setObjectName("SectionTitle")
        layout.addWidget(overview_title)

        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(12)

        self.total_value = self.create_metric_card(
            metrics_layout, "Total tasks"
        )
        self.active_value = self.create_metric_card(
            metrics_layout, "Active"
        )
        self.completed_value = self.create_metric_card(
            metrics_layout, "Completed"
        )
        self.overdue_value = self.create_metric_card(
            metrics_layout, "Overdue"
        )

        layout.addLayout(metrics_layout)

        # Progress
        progress_card = QFrame()
        progress_card.setObjectName("ContentCard")

        progress_layout = QVBoxLayout(progress_card)
        progress_layout.setContentsMargins(18, 13, 18, 13)
        progress_layout.setSpacing(8)

        progress_header = QHBoxLayout()

        progress_title = QLabel("Your progress")
        progress_title.setStyleSheet(
            "font-size: 14px; font-weight: bold;"
        )

        self.progress_label = QLabel("0% completed")
        self.progress_label.setObjectName("Muted")

        progress_header.addWidget(progress_title)
        progress_header.addStretch()
        progress_header.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)

        progress_layout.addLayout(progress_header)
        progress_layout.addWidget(self.progress_bar)

        layout.addWidget(progress_card)

        # Today's tasks and upcoming deadlines
        lists_layout = QHBoxLayout()
        lists_layout.setSpacing(13)

        today_card = self.create_content_card(
            "Today's tasks", lists_layout
        )

        self.today_tasks_layout = QVBoxLayout()
        self.today_tasks_layout.setSpacing(9)
        today_card.addLayout(self.today_tasks_layout)

        today_button = QPushButton("View all tasks")
        today_button.setObjectName("TextButton")
        today_button.setCursor(Qt.CursorShape.PointingHandCursor)
        today_button.clicked.connect(self.open_tasks)

        today_card.addWidget(today_button, alignment=Qt.AlignmentFlag.AlignRight)

        upcoming_card = self.create_content_card(
            "Upcoming deadlines", lists_layout
        )

        self.upcoming_tasks_layout = QVBoxLayout()
        self.upcoming_tasks_layout.setSpacing(9)
        upcoming_card.addLayout(self.upcoming_tasks_layout)

        upcoming_button = QPushButton("View all tasks")
        upcoming_button.setObjectName("TextButton")
        upcoming_button.setCursor(Qt.CursorShape.PointingHandCursor)
        upcoming_button.clicked.connect(self.open_tasks)

        upcoming_card.addWidget(
            upcoming_button,
            alignment=Qt.AlignmentFlag.AlignRight,
        )

        layout.addLayout(lists_layout)
        layout.addStretch()

        scroll_area.setWidget(content)
        outer_layout.addWidget(scroll_area)

    def create_metric_card(self, layout, title):
        card = QFrame()
        card.setObjectName("MetricCard")
        card.setMinimumHeight(88)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(13, 12, 13, 12)
        card_layout.setSpacing(5)

        heading = QLabel(title)
        heading.setObjectName("Muted")
        heading.setStyleSheet("font-size: 12px;")

        value = QLabel("0")
        value.setObjectName("MetricValue")

        card_layout.addWidget(heading)
        card_layout.addWidget(value)

        layout.addWidget(card)

        return value

    def create_content_card(self, title, parent_layout):
        card = QFrame()
        card.setObjectName("ContentCard")
        card.setMinimumHeight(190)
        card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 14, 15, 13)
        card_layout.setSpacing(10)

        heading = QLabel(title)
        heading.setObjectName("SectionTitle")

        card_layout.addWidget(heading)

        parent_layout.addWidget(card)

        return card_layout

    def update_clock(self):
        now = datetime.now()

        hour = now.hour

        if hour < 12:
            greeting = "Good morning!"
        elif hour < 17:
            greeting = "Good afternoon!"
        else:
            greeting = "Good evening!"

        self.greeting_label.setText(greeting)
        self.date_label.setText(
            now.strftime("%A, %d %B %Y")
        )
        self.clock_label.setText(
            now.strftime("%I:%M:%S %p")
        )

    def parse_due_date(self, value):
        """Convert supported stored date formats into date objects."""

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
                return datetime.strptime(
                    value, date_format
                ).date()
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
        label.setStyleSheet("font-size: 12px; padding: 5px 0;")
        layout.addWidget(label)

    def add_task_row(self, layout, task, detail):
        row = QFrame()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 5, 0, 5)
        row_layout.setSpacing(8)

        priority = task.get("priority", "Medium")

        priority_colours = {
            "High": "#C66B60",
            "Medium": "#B28B4E",
            "Low": "#758B6D",
        }

        indicator = QLabel("●")
        indicator.setStyleSheet(
            f"color: {priority_colours.get(priority, '#85847B')};"
            "font-size: 11px;"
        )

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

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

        row_layout.addWidget(indicator, alignment=Qt.AlignmentFlag.AlignTop)
        row_layout.addLayout(text_layout, 1)

        layout.addWidget(row)

    def refresh_dashboard(self):
        """Refresh all dashboard information from the shared TaskService."""

        tasks = self.task_service.get_all_tasks()

        today = date.today()

        completed = [
            task for task in tasks
            if task.get("is_completed")
        ]

        active = [
            task for task in tasks
            if not task.get("is_completed")
        ]

        dated_active = []

        for task in active:
            due_date = self.parse_due_date(task.get("due_date"))

            if due_date is not None:
                dated_active.append((due_date, task))

        overdue = [
            (due_date, task)
            for due_date, task in dated_active
            if due_date < today
        ]

        today_tasks = [
            (due_date, task)
            for due_date, task in dated_active
            if due_date == today
        ]

        upcoming = [
            (due_date, task)
            for due_date, task in dated_active
            if due_date > today
        ]

        priority_order = {
            "High": 0,
            "Medium": 1,
            "Low": 2,
        }

        dated_sort = lambda item: (
            item[0],
            priority_order.get(
                item[1].get("priority", "Medium"), 1
            ),
        )

        today_tasks.sort(key=dated_sort)
        upcoming.sort(key=dated_sort)

        # Update overview cards.
        total_count = len(tasks)
        completed_count = len(completed)
        active_count = len(active)
        overdue_count = len(overdue)

        self.total_value.setText(str(total_count))
        self.active_value.setText(str(active_count))
        self.completed_value.setText(str(completed_count))
        self.overdue_value.setText(str(overdue_count))

        # Update progress.
        progress = (
            round((completed_count / total_count) * 100)
            if total_count else 0
        )

        self.progress_bar.setValue(progress)
        self.progress_label.setText(
            f"{progress}% completed"
        )

        # Today's tasks.
        self.clear_layout(self.today_tasks_layout)

        if today_tasks:
            for due_date, task in today_tasks[:4]:
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

        # Upcoming deadlines.
        self.clear_layout(self.upcoming_tasks_layout)

        if upcoming:
            for due_date, task in upcoming[:4]:
                self.add_task_row(
                    self.upcoming_tasks_layout,
                    task,
                    due_date.strftime("%d %b %Y"),
                )
        else:
            self.add_empty_message(
                self.upcoming_tasks_layout,
                "No upcoming deadlines. You're all clear!",
            )

    def open_tasks(self):
        if self.navigate_callback:
            self.navigate_callback("Tasks")

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_dashboard()