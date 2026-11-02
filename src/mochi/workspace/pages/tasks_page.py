from datetime import date

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QFrame,
    QComboBox, QScrollArea,
    QMessageBox, QDialog, QDialogButtonBox, QFormLayout,
    QCalendarWidget,
)
from PySide6.QtCore import Qt, QDate, QRectF, QTimer
from PySide6.QtGui import QColor, QPainter


BACKGROUND = "#F5F1E9"
CARD_BACKGROUND = "#FFFCF6"
CARD_BORDER = "#E9E2D6"
TEXT_PRIMARY = "#292B28"
TEXT_SECONDARY = "#77796F"
FOREST_GREEN = "#596B55"

PRIORITY_COLORS = {
    "High": {
        "background": "#F3DFDB",
        "foreground": "#A44339",
        "edge": "#C96E5C",
    },
    "Medium": {
        "background": "#F4E9D2",
        "foreground": "#97702E",
        "edge": "#D6A44E",
    },
    "Low": {
        "background": "#DFEBDD",
        "foreground": "#47734B",
        "edge": "#779A73",
    },
}

PRIORITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}


class TasksPage(QWidget):
    """Mochi task manager."""

    FILTERS = ["Upcoming", "Pending", "Completed", "No Due Date"]

    def __init__(self, task_service):
        super().__init__()

        self.task_service = task_service
        self.current_filter = "Upcoming"
        self.notification_timer = QTimer(self)
        self.notification_timer.setSingleShot(True)
        self.notification_timer.timeout.connect(self.hide_notification)

        self.build_interface()
        self.refresh_tasks()

    # --------------------------------------------------
    # BACKGROUND
    # --------------------------------------------------

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(BACKGROUND))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#C79B69"))

        positions = [
            (0.04, 0.16), (0.20, 0.38), (0.39, 0.13),
            (0.57, 0.34), (0.76, 0.16), (0.94, 0.39),
            (0.12, 0.73), (0.33, 0.84), (0.55, 0.69),
            (0.77, 0.87), (0.94, 0.72), (0.47, 0.51),
            (0.08, 0.49), (0.68, 0.52),
        ]

        painter.save()
        painter.setOpacity(0.12)

        for xr, yr in positions:
            self.draw_paw(
                painter,
                int(self.width() * xr),
                int(self.height() * yr),
            )

        painter.restore()

    @staticmethod
    def draw_paw(painter, x, y):
        painter.drawEllipse(QRectF(x - 10, y - 2, 20, 17))
        painter.drawEllipse(QRectF(x - 15, y - 15, 8, 10))
        painter.drawEllipse(QRectF(x - 5, y - 21, 8, 10))
        painter.drawEllipse(QRectF(x + 5, y - 21, 8, 10))
        painter.drawEllipse(QRectF(x + 12, y - 13, 8, 10))

    # --------------------------------------------------
    # INTERFACE
    # --------------------------------------------------

    def build_interface(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(10, 10, 10, 10)
        main.setSpacing(13)

        heading = QLabel("✓  Tasks")
        heading.setStyleSheet("""
            font-size: 29px;
            font-weight: bold;
            color: #292B28;
            background: transparent;
        """)

        subtitle = QLabel(
            "Organise your priorities and daily responsibilities."
        )
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #77796F;
            background: transparent;
        """)

        main.addWidget(heading)
        main.addWidget(subtitle)

        stats = QGridLayout()
        stats.setSpacing(12)

        self.total_value = self.create_stat_card(
            stats, 0, 0, "Total Tasks", "#29372D"
        )
        self.pending_value = self.create_stat_card(
            stats, 0, 1, "Pending", "#875B36"
        )
        self.completed_value = self.create_stat_card(
            stats, 0, 2, "Completed", "#496747"
        )
        self.progress_value = self.create_stat_card(
            stats, 0, 3, "Progress", "#42483F"
        )

        main.addLayout(stats)

        # Search and add task
        action = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search tasks... (e.g. project, study, report)"
        )
        self.search_input.textChanged.connect(self.refresh_tasks)

        add_button = QPushButton("+  Add Task")
        add_button.setObjectName("AddButton")
        add_button.clicked.connect(self.add_task)

        action.addWidget(self.search_input, 1)
        action.addWidget(add_button)
        main.addLayout(action)

        # Four filters only
        filters = QHBoxLayout()
        filters.setSpacing(9)
        self.filter_buttons = {}

        for name in self.FILTERS:
            button = QPushButton(name)
            button.setCheckable(True)
            button.setChecked(name == self.current_filter)
            button.clicked.connect(
                lambda checked=False, value=name: self.set_filter(value)
            )
            self.filter_buttons[name] = button
            filters.addWidget(button)

        filters.addStretch()
        main.addLayout(filters)

        # Scrollable task content
        self.task_container = QWidget()
        self.task_container.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground, True
        )

        self.task_layout = QVBoxLayout(self.task_container)
        self.task_layout.setContentsMargins(2, 5, 2, 5)
        self.task_layout.setSpacing(12)
        self.task_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setWidget(self.task_container)
        self.scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
        """)
        self.scroll.viewport().setStyleSheet("background: transparent;")
        main.addWidget(self.scroll, 1)

        # Undo notification, initially hidden
        self.notification = QFrame(self)
        self.notification.setObjectName("TaskNotification")
        self.notification.setStyleSheet("""
            QFrame#TaskNotification {
                background-color: #292E29;
                border: 1px solid #596B55;
                border-radius: 12px;
            }
            QLabel {
                color: #F5F1E9;
                background: transparent;
                font-size: 13px;
            }
            QPushButton {
                background-color: #E8EDE4;
                color: #354532;
                border: none;
                border-radius: 7px;
                padding: 7px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D6E0D0;
            }
        """)

        notification_layout = QHBoxLayout(self.notification)
        notification_layout.setContentsMargins(14, 9, 14, 9)

        self.notification_label = QLabel("")
        self.undo_button = QPushButton("Undo")
        self.undo_button.clicked.connect(self.undo_completion)

        notification_layout.addWidget(self.notification_label, 1)
        notification_layout.addWidget(self.undo_button)

        self.notification.hide()
        self.pending_undo_id = None
        self.pending_undo_original_filter = None

        self.setStyleSheet("""
            QWidget {
                color: #292B28;
                font-family: "Segoe UI";
            }
            QLineEdit, QComboBox, QDateEdit, QTextEdit {
                background-color: #FFFCF6;
                border: 1px solid #E9E2D6;
                border-radius: 9px;
                padding: 9px;
                color: #292B28;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus,
            QDateEdit:focus {
                border: 1px solid #87977E;
            }
            QPushButton {
                background-color: #E9E6DC;
                color: #45483F;
                border: none;
                border-radius: 8px;
                padding: 9px 14px;
            }
            QPushButton:hover {
                background-color: #DCDDD1;
            }
            QPushButton:checked {
                background-color: #DCE8D8;
                color: #315D37;
                font-weight: bold;
            }
            QPushButton#AddButton {
                background-color: #596B55;
                color: white;
                font-weight: bold;
                padding: 11px 17px;
            }
            QPushButton#AddButton:hover {
                background-color: #465843;
            }
        """)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.position_notification()

    def position_notification(self):
        if not hasattr(self, "notification"):
            return

        width = min(440, max(280, self.width() - 40))
        self.notification.setFixedWidth(width)
        self.notification.adjustSize()
        self.notification.move(
            (self.width() - width) // 2,
            self.height() - self.notification.height() - 18,
        )

    # --------------------------------------------------
    # STATISTICS
    # --------------------------------------------------

    def create_stat_card(self, grid, row, column, title, color):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #FFFCF6;
                border: 1px solid #E9E2D6;
                border-radius: 13px;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 11, 15, 11)
        layout.setSpacing(3)

        value = QLabel("0")
        value.setStyleSheet(f"""
            font-size: 25px;
            font-weight: bold;
            color: {color};
            border: none;
            background: transparent;
        """)

        label = QLabel(title)
        label.setStyleSheet("""
            color: #85867D;
            font-size: 11px;
            border: none;
            background: transparent;
        """)

        layout.addWidget(value)
        layout.addWidget(label)
        grid.addWidget(card, row, column)
        return value

    # --------------------------------------------------
    # FILTERING AND SEARCH
    # --------------------------------------------------

    def set_filter(self, filter_name):
        self.current_filter = filter_name

        for name, button in self.filter_buttons.items():
            button.setChecked(name == filter_name)

        self.refresh_tasks()

    def matches_search(self, task, query):
        searchable = " ".join([
            str(task.get("title") or ""),
            str(task.get("description") or ""),
            str(task.get("category") or ""),
        ]).casefold()

        words = query.casefold().split()
        return all(word in searchable for word in words)

    def priority_key(self, task):
        return PRIORITY_ORDER.get(task.get("priority", "Medium"), 1)

    def task_date(self, task):
        value = task.get("due_date")
        if not value:
            return None

        try:
            return date.fromisoformat(str(value)[:10])
        except (ValueError, TypeError):
            return None

    def date_heading(self, due):
        if due == date.today():
            return "Today  ·  " + due.strftime("%d %b · %A")
        return due.strftime("%d %b · %A")

    # --------------------------------------------------
    # REFRESH
    # --------------------------------------------------

    def clear_task_layout(self):
        while self.task_layout.count():
            item = self.task_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def refresh_tasks(self, *args):
        tasks = self.task_service.get_all_tasks()
        today = date.today()
        query = self.search_input.text().strip()

        tasks = [
            task for task in tasks
            if self.matches_search(task, query)
        ]

        total = len(tasks)
        completed = sum(bool(t["is_completed"]) for t in tasks)
        active = total - completed

        self.total_value.setText(str(total))
        self.pending_value.setText(str(sum(
            not t["is_completed"]
            and self.task_date(t) is not None
            and self.task_date(t) < today
            for t in tasks
        )))
        self.completed_value.setText(str(completed))
        self.progress_value.setText(
            f"{round(completed / total * 100) if total else 0}%"
        )

        self.clear_task_layout()

        if self.current_filter == "Completed":
            selected = [t for t in tasks if t["is_completed"]]
            self.render_completed(selected)
            return

        active_tasks = [t for t in tasks if not t["is_completed"]]

        if self.current_filter == "Upcoming":
            selected = [
                t for t in active_tasks
                if self.task_date(t) is not None
                and self.task_date(t) >= today
            ]
            self.render_deadline_groups(selected, today)
            return

        if self.current_filter == "Pending":
            selected = [
                t for t in active_tasks
                if self.task_date(t) is not None
                and self.task_date(t) < today
            ]
            self.render_overdue(selected, today)
            return

        if self.current_filter == "No Due Date":
            selected = [
                t for t in active_tasks
                if self.task_date(t) is None
            ]
            selected.sort(key=self.priority_key)
            self.add_section_header("No Due Date", len(selected))

            if not selected:
                self.add_empty_state(
                    "No flexible tasks. All your active tasks have deadlines."
                )
                return

            for task in selected:
                self.add_task_card(
                    task,
                    detail=task.get("category") or "General",
                )

    # --------------------------------------------------
    # SECTION HEADERS AND EMPTY STATES
    # --------------------------------------------------

    def add_section_header(self, title, count):
        header = QWidget()
        header.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground, True
        )

        layout = QVBoxLayout(header)
        layout.setContentsMargins(0, 5, 0, 0)

        row = QHBoxLayout()
        heading = QLabel(title)
        heading.setStyleSheet("""
            font-size: 19px;
            font-weight: bold;
            color: #292B28;
            background: transparent;
        """)

        count_label = QLabel(
            f"{count} task" + ("" if count == 1 else "s")
        )
        count_label.setStyleSheet("""
            background-color: #E8E8DF;
            color: #45483F;
            border-radius: 10px;
            padding: 4px 10px;
            font-size: 11px;
            font-weight: bold;
        """)

        row.addWidget(heading)
        row.addWidget(count_label)
        row.addStretch()
        layout.addLayout(row)
        self.task_layout.addWidget(header)

    def add_empty_state(self, message, icon="✧"):
        container = QWidget()
        container.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground, True
        )
        container.setStyleSheet("""
            QWidget {
                background: transparent;
                border: none;
            }
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(15, 16, 15, 16)
        layout.setSpacing(7)

        symbol = QLabel(icon)
        symbol.setAlignment(Qt.AlignmentFlag.AlignCenter)
        symbol.setStyleSheet("""
            QLabel {
                color: #87977E;
                font-size: 25px;
                background: transparent;
                border: none;
            }
        """)

        label = QLabel(message)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        label.setStyleSheet("""
            QLabel {
                color: #77796F;
                font-size: 13px;
                background: transparent;
                border: none;
            }
        """)

        layout.addWidget(symbol)
        layout.addWidget(label)

        self.task_layout.addWidget(container)

    def add_date_heading(self, due):
        label = QLabel(self.date_heading(due))
        label.setStyleSheet("""
            color: #55594F;
            font-size: 13px;
            font-weight: bold;
            padding: 7px 2px 2px 2px;
            background: transparent;
        """)
        self.task_layout.addWidget(label)

    # --------------------------------------------------
    # RENDER FILTER CONTENT
    # --------------------------------------------------

    def render_deadline_groups(self, tasks, today):
        self.add_section_header("Upcoming", len(tasks))

        if not tasks:
            self.add_empty_state(
                "Nothing coming up. You're all clear!",
                "✓",
            )
            return

        groups = {}
        for task in tasks:
            groups.setdefault(self.task_date(task), []).append(task)

        for due in sorted(groups):
            self.add_date_heading(due)

            for task in sorted(groups[due], key=self.priority_key):
                is_today = due == today
                self.add_task_card(
                    task,
                    detail=(
                        "Due today"
                        if is_today
                        else f"Due: {due.strftime('%d %b · %A')}"
                    ),
                    detail_color="#47734B" if is_today else TEXT_SECONDARY,
                    today=is_today,
                )

    def render_overdue(self, tasks, today):
        self.add_section_header("Pending", len(tasks))

        if not tasks:
            self.add_empty_state(
                "You're all caught up. Nothing is overdue!",
                "✓",
            )
            return

        groups = {}
        for task in tasks:
            groups.setdefault(self.task_date(task), []).append(task)

        # Most recently missed deadline first.
        for due in sorted(groups, reverse=True):
            self.add_date_heading(due)

            for task in sorted(groups[due], key=self.priority_key):
                days = (today - due).days
                duration = (
                    "1 day overdue"
                    if days == 1
                    else f"{days} days overdue"
                )

                self.add_task_card(
                    task,
                    detail=f"{duration}  ·  Due: {due.strftime('%d %b')}",
                    detail_color="#A44339",
                )

    def render_completed(self, tasks):
        self.add_section_header("Completed", len(tasks))

        if not tasks:
            self.add_empty_state(
                "No completed tasks yet. Your achievements will appear here.",
                "★",
            )
            return

        tasks.sort(
            key=lambda task: (
                self.task_date(task) is None,
                self.task_date(task) or date.max,
                self.priority_key(task),
            )
        )

        for task in tasks:
            due = self.task_date(task)
            detail = (
                f"Due: {due.strftime('%d %b · %A')}"
                if due else "No due date"
            )
            self.add_task_card(task, detail=detail)

    # --------------------------------------------------
    # TASK CARD AND DOUBLE-CLICK COMPLETION
    # --------------------------------------------------

    def add_task_card(
        self, task, detail="", detail_color=TEXT_SECONDARY,
        today=False,
    ):
        card = TaskCard(
            task,
            on_toggle=self.toggle_task,
            on_edit=self.edit_task,
            on_delete=self.delete_task,
            detail=detail,
            detail_color=detail_color,
            today=today,
        )
        self.task_layout.addWidget(card)

    def toggle_task(self, task_id, completed):
        task = self.task_service.get_task(task_id)
        if not task:
            return

        original_filter = self.current_filter

        success = self.task_service.set_task_completed(
            task_id, completed
        )

        if not success:
            return

        self.refresh_tasks()

        if completed:
            self.show_notification(
                task.get("title", "Task"),
                task_id,
                original_filter,
            )

    def show_notification(self, title, task_id, original_filter):
        self.notification_timer.stop()
        self.pending_undo_id = task_id
        self.pending_undo_original_filter = original_filter

        self.notification_label.setText(
            f"✓  {title} has been turned in."
        )
        self.notification.show()
        self.position_notification()
        self.notification.raise_()
        self.notification_timer.start(5000)

    def hide_notification(self):
        self.notification.hide()
        self.pending_undo_id = None
        self.pending_undo_original_filter = None

    def undo_completion(self):
        if self.pending_undo_id is None:
            return

        task_id = self.pending_undo_id
        self.notification_timer.stop()

        self.task_service.set_task_completed(task_id, False)

        original_filter = self.pending_undo_original_filter
        self.hide_notification()

        if original_filter in self.FILTERS:
            self.set_filter(original_filter)
        else:
            self.refresh_tasks()

    # --------------------------------------------------
    # CREATE, EDIT AND DELETE
    # --------------------------------------------------

    def add_task(self):
        dialog = TaskDialog(self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        try:
            self.task_service.create_task(**dialog.get_data())
            self.refresh_tasks()
        except Exception as error:
            QMessageBox.critical(
                self, "Could not create task", str(error)
            )

    def edit_task(self, task_id):
        task = self.task_service.get_task(task_id)
        if not task:
            return

        dialog = TaskDialog(self, task)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        try:
            self.task_service.update_task(
                task_id, **dialog.get_data()
            )
            self.refresh_tasks()
        except Exception as error:
            QMessageBox.critical(
                self, "Could not update task", str(error)
            )

    def delete_task(self, task_id):
        task = self.task_service.get_task(task_id)
        if not task:
            return

        dialog = DeleteConfirmationDialog(
            task.get("title", "this task"), self
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self.task_service.delete_task(task_id)
        self.refresh_tasks()


class DoubleClickCompletion(QLabel):
    """A completion control that only changes state on double-click."""

    def __init__(self, completed, callback, parent=None):
        super().__init__(parent)
        self.completed = completed
        self.callback = callback
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedSize(30, 34)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_display()

    def update_display(self):
        self.setText("✓" if self.completed else "○")
        self.setStyleSheet(f"""
            QLabel {{
                color: {"#47734B" if self.completed else "#A5A398"};
                background: transparent;
                font-size: 22px;
                font-weight: bold;
            }}
        """)

    def mouseDoubleClickEvent(self, event):
        self.completed = not self.completed
        self.update_display()
        self.callback(self.completed)
        event.accept()


class TaskCard(QFrame):
    def __init__(
        self, task, on_toggle, on_edit, on_delete,
        detail="", detail_color=TEXT_SECONDARY, today=False,
    ):
        super().__init__()

        self.task = task
        priority = task.get("priority", "Medium")
        colors = PRIORITY_COLORS.get(
            priority, PRIORITY_COLORS["Medium"]
        )

        self.setObjectName("TaskCard")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(13, 10, 13, 10)
        layout.setSpacing(11)

        completion = DoubleClickCompletion(
            bool(task["is_completed"]),
            lambda completed: on_toggle(task["id"], completed),
        )
        layout.addWidget(completion)

        details = QVBoxLayout()
        details.setSpacing(4)

        title = QLabel(task["title"])
        title.setWordWrap(True)
        title.setStyleSheet(f"""
            color: {"#85867D" if task["is_completed"] else "#292B28"};
            text-decoration: {"line-through" if task["is_completed"] else "none"};
            font-size: 14px;
            font-weight: bold;
            background: transparent;
        """)
        details.addWidget(title)

        if detail:
            info = QLabel(detail)
            info.setWordWrap(True)
            info.setStyleSheet(f"""
                color: {detail_color};
                font-size: 11px;
                background: transparent;
            """)
            details.addWidget(info)

        if today and not task["is_completed"]:
            today_label = QLabel("DUE TODAY")
            today_label.setStyleSheet("""
                color: #47734B;
                font-size: 9px;
                font-weight: bold;
                background: transparent;
            """)
            details.addWidget(today_label)

        layout.addLayout(details, 1)

        priority_label = QLabel(priority)
        priority_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        priority_label.setMinimumWidth(68)
        priority_label.setStyleSheet(f"""
            background-color: {colors['background']};
            color: {colors['foreground']};
            border-radius: 8px;
            padding: 6px 9px;
            font-size: 11px;
            font-weight: bold;
        """)
        layout.addWidget(priority_label)

        edit_button = QPushButton("Edit")
        edit_button.setObjectName("SmallButton")
        edit_button.clicked.connect(
            lambda: on_edit(task["id"])
        )

        delete_button = QPushButton("Delete")
        delete_button.setObjectName("DeleteButton")
        delete_button.clicked.connect(
            lambda: on_delete(task["id"])
        )

        layout.addWidget(edit_button)
        layout.addWidget(delete_button)

        self.setStyleSheet(f"""
            QFrame#TaskCard {{
                background-color: {CARD_BACKGROUND};
                border: 1px solid {CARD_BORDER};
                border-left: 4px solid {colors['edge']};
                border-radius: 11px;
            }}
            QPushButton#SmallButton {{
                background-color: #E9EDE5;
                color: #43553F;
                border: none;
                border-radius: 7px;
                padding: 7px 11px;
            }}
            QPushButton#DeleteButton {{
                background-color: #F4E6E1;
                color: #985347;
                border: none;
                border-radius: 7px;
                padding: 7px 11px;
            }}
            QPushButton#SmallButton:hover {{
                background-color: #DDE5D8;
            }}
            QPushButton#DeleteButton:hover {{
                background-color: #EBD5CE;
            }}
        """)


class DatePickerDialog(QDialog):
    """A styled calendar for selecting a task deadline."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Choose Due Date")
        self.setFixedWidth(350)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        heading = QLabel("Choose a due date")
        heading.setStyleSheet("""
            color: #292B28;
            font-size: 18px;
            font-weight: bold;
            background: transparent;
            border: none;
        """)

        subtitle = QLabel("Select today or a future date.")
        subtitle.setStyleSheet("""
            color: #77796F;
            font-size: 12px;
            background: transparent;
            border: none;
        """)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(False)
        self.calendar.setFirstDayOfWeek(Qt.DayOfWeek.Monday)

        today = QDate.currentDate()
        self.calendar.setMinimumDate(today)
        self.calendar.setSelectedDate(today)

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
                border-radius: 6px;
                padding: 7px;
                font-weight: bold;
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
                font-size: 12px;
            }

            QCalendarWidget QAbstractItemView:disabled {
                color: #C9C5BB;
                background-color: #F5F1E9;
            }
        """)

        self.calendar.clicked.connect(self.accept)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #E8E4DA;
                color: #45483F;
                border: none;
                border-radius: 8px;
                padding: 9px 16px;
            }
            QPushButton:hover {
                background-color: #DCDDD1;
            }
        """)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)

        layout.addWidget(heading)
        layout.addWidget(subtitle)
        layout.addWidget(self.calendar)
        layout.addLayout(button_layout)

        self.setStyleSheet("""
            QDialog {
                background-color: #F5F1E9;
            }
        """)

    def selected_date(self):
        return self.calendar.selectedDate()


class TaskDialog(QDialog):
    def __init__(self, parent=None, task=None):
        super().__init__(parent)

        self.setWindowTitle("Edit Task" if task else "Create New Task")
        self.setMinimumWidth(460)

        self.selected_due_date = None

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        form = QFormLayout()
        form.setSpacing(12)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("What needs to be done?")

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Add some details...")
        self.description_input.setMaximumHeight(90)

        self.priority_input = QComboBox()
        self.priority_input.addItems(["High", "Medium", "Low"])
        self.priority_input.setCurrentText("Medium")

        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText(
            "e.g. Study, Work, Personal"
        )

        # Due date is selected only through the calendar dialog.
        self.due_date_button = QPushButton("DD-MM-YYYY")
        self.due_date_button.setMinimumHeight(40)
        self.due_date_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.due_date_button.clicked.connect(self.open_date_picker)

        self.clear_date_button = QPushButton("Clear")
        self.clear_date_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_date_button.clicked.connect(self.clear_due_date)
        self.clear_date_button.setVisible(False)

        date_layout = QHBoxLayout()
        date_layout.setSpacing(8)
        date_layout.addWidget(self.due_date_button, 1)
        date_layout.addWidget(self.clear_date_button)

        date_container = QWidget()
        date_container.setLayout(date_layout)

        form.addRow("Title", self.title_input)
        form.addRow("Description", self.description_input)
        form.addRow("Priority", self.priority_input)
        form.addRow("Category", self.category_input)
        form.addRow("Due date", date_container)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if task:
            self.title_input.setText(task["title"])
            self.description_input.setPlainText(task.get("description") or "")
            self.priority_input.setCurrentText(
                task.get("priority", "Medium")
            )
            self.category_input.setText(task.get("category") or "General")

            if task.get("due_date"):
                parsed = QDate.fromString(
                    task["due_date"][:10], "yyyy-MM-dd"
                )
                if parsed.isValid():
                    self.selected_due_date = parsed
                    self.update_date_button()

        self.setStyleSheet("""
            QDialog {
                background-color: #F5F1E9;
            }

            QLabel {
                color: #292B28;
                background: transparent;
                border: none;
            }

            QLineEdit, QTextEdit, QComboBox {
                background-color: #FFFCF6;
                border: 1px solid #E2DCCF;
                border-radius: 8px;
                padding: 9px;
                color: #292B28;
            }

            QLineEdit:focus, QTextEdit:focus,
            QComboBox:focus {
                border: 1px solid #87977E;
            }

            QPushButton {
                background-color: #596B55;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 9px 16px;
            }

            QPushButton:hover {
                background-color: #465843;
            }

            QPushButton#ClearDate {
                background-color: #E8E4DA;
                color: #45483F;
            }
        """)

        self.clear_date_button.setObjectName("ClearDate")
        self.clear_date_button.style().unpolish(self.clear_date_button)
        self.clear_date_button.style().polish(self.clear_date_button)

    def open_date_picker(self):
        dialog = DatePickerDialog(self)

        if (
            self.selected_due_date
            and self.selected_due_date >= QDate.currentDate()
        ):
            dialog.calendar.setSelectedDate(self.selected_due_date)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.selected_due_date = dialog.selected_date()
            self.update_date_button()

    def update_date_button(self):
        if self.selected_due_date:
            self.due_date_button.setText(
                self.selected_due_date.toString("dd-MM-yyyy")
            )
            self.clear_date_button.setVisible(True)
        else:
            self.due_date_button.setText("DD-MM-YYYY")
            self.clear_date_button.setVisible(False)

    def clear_due_date(self):
        self.selected_due_date = None
        self.update_date_button()

    def validate_and_accept(self):
        if not self.title_input.text().strip():
            QMessageBox.warning(
                self,
                "Missing title",
                "Please enter a task title.",
            )
            return

        self.accept()

    def get_data(self):
        due_date = None
        if self.selected_due_date:
            due_date = self.selected_due_date.toString("yyyy-MM-dd")

        return {
            "title": self.title_input.text().strip(),
            "description": self.description_input.toPlainText(),
            "priority": self.priority_input.currentText(),
            "category": self.category_input.text().strip() or "General",
            "due_date": due_date,
        }


class DeleteConfirmationDialog(QDialog):
    def __init__(self, task_title, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Delete Task")
        self.setFixedWidth(390)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(23, 22, 23, 20)
        layout.setSpacing(13)

        heading = QLabel("Delete this task?")
        heading.setStyleSheet("""
            color: #292B28;
            font-size: 19px;
            font-weight: bold;
            background: transparent;
        """)

        message = QLabel(
            f'Are you sure you want to delete "{task_title}"?\n\n'
            "This action cannot be undone."
        )
        message.setWordWrap(True)
        message.setStyleSheet("""
            color: #77796F;
            font-size: 13px;
            background: transparent;
        """)

        layout.addWidget(heading)
        layout.addWidget(message)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        delete_button = QPushButton("Delete Task")
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #A65348;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 9px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #91453B;
            }
        """)

        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #E8E4DA;
                color: #45483F;
                border: none;
                border-radius: 8px;
                padding: 9px 15px;
            }
        """)

        delete_button.clicked.connect(self.accept)

        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(delete_button)
        layout.addLayout(buttons_layout)

        self.setStyleSheet("""
            QDialog {
                background-color: #F5F1E9;
            }
        """)
