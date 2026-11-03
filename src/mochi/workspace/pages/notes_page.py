
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QFrame,
    QComboBox,
    QScrollArea,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QSizePolicy,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter


BACKGROUND = "#F5F1E9"
CARD_BACKGROUND = "#FFFCF6"
CARD_BORDER = "#E9E2D6"
TEXT_PRIMARY = "#292B28"
TEXT_SECONDARY = "#77796F"
FOREST_GREEN = "#596B55"

NOTE_CARD_HEIGHT = 190


class MochiMessageDialog(QDialog):
    """Custom Mochi-styled message and confirmation dialog."""

    def __init__(
        self,
        parent,
        title,
        message,
        confirm_text="OK",
        cancel_text=None,
        danger=False,
    ):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(390)
        self.setMaximumWidth(460)

        self.setStyleSheet("""
            QDialog {
                background-color: #F5F1E9;
                border: 1px solid #E9E2D6;
                border-radius: 14px;
            }
            QLabel {
                background: transparent;
                color: #292B28;
            }
            QPushButton {
                background-color: #EAE5DA;
                color: #292B28;
                border: none;
                border-radius: 8px;
                padding: 9px 18px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #DDD7CA;
            }
            QPushButton#ConfirmButton {
                background-color: #596B55;
                color: white;
                font-weight: bold;
            }
            QPushButton#ConfirmButton:hover {
                background-color: #465943;
            }
            QPushButton#DangerButton {
                background-color: #A6534D;
                color: white;
                font-weight: bold;
            }
            QPushButton#DangerButton:hover {
                background-color: #8D403B;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 23, 25, 22)
        layout.setSpacing(15)

        heading = QLabel(title)
        heading.setStyleSheet("""
            font-size: 19px;
            font-weight: bold;
            color: #292B28;
        """)

        body = QLabel(message)
        body.setWordWrap(True)
        body.setStyleSheet("""
            font-size: 13px;
            color: #77796F;
        """)

        layout.addWidget(heading)
        layout.addWidget(body)

        buttons = QHBoxLayout()
        buttons.addStretch()

        if cancel_text:
            cancel_button = QPushButton(cancel_text)
            cancel_button.clicked.connect(self.reject)
            buttons.addWidget(cancel_button)

        confirm_button = QPushButton(confirm_text)
        confirm_button.setObjectName(
            "DangerButton" if danger else "ConfirmButton"
        )
        confirm_button.clicked.connect(self.accept)
        buttons.addWidget(confirm_button)

        layout.addLayout(buttons)

    @staticmethod
    def show_warning(parent, title, message):
        dialog = MochiMessageDialog(
            parent,
            title,
            message,
            confirm_text="Got it",
        )
        dialog.exec()

    @staticmethod
    def ask_confirmation(parent, title, message):
        dialog = MochiMessageDialog(
            parent,
            title,
            message,
            confirm_text="Delete",
            cancel_text="Cancel",
            danger=True,
        )
        return dialog.exec() == QDialog.DialogCode.Accepted


class NoteEditorDialog(QDialog):
    """Dialog for creating and editing notes."""

    CATEGORIES = ["Personal", "Study"]

    def __init__(self, parent=None, note=None):
        super().__init__(parent)

        self.note = note
        self.setWindowTitle("Edit Note" if note else "New Note")
        self.setMinimumSize(520, 480)
        self.setModal(True)

        self.setStyleSheet("""
            QDialog {
                background-color: #F5F1E9;
            }
            QLabel {
                color: #292B28;
                background: transparent;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #FFFCF6;
                color: #292B28;
                border: 1px solid #E9E2D6;
                border-radius: 9px;
                padding: 9px;
                font-size: 13px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 1px solid #81917B;
            }
            QPushButton {
                background-color: #EAE5DA;
                color: #292B28;
                border: none;
                border-radius: 8px;
                padding: 9px 17px;
            }
            QPushButton:hover {
                background-color: #DDD7CA;
            }
            QPushButton#SaveButton {
                background-color: #596B55;
                color: white;
                font-weight: bold;
            }
            QPushButton#SaveButton:hover {
                background-color: #465943;
            }
        """)

        self.build_interface()

    def build_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(15)

        heading = QLabel(
            "Edit your note" if self.note else "Create a new note"
        )
        heading.setStyleSheet(
            "font-size: 23px; font-weight: bold;"
        )
        layout.addWidget(heading)

        form = QFormLayout()
        form.setSpacing(12)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Give your note a title")

        self.category_input = QComboBox()
        self.category_input.addItems(self.CATEGORIES)

        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText(
            "Start writing your thoughts..."
        )
        self.content_input.setMinimumHeight(230)

        form.addRow("Title", self.title_input)
        form.addRow("Category", self.category_input)
        form.addRow("Content", self.content_input)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel
        )

        self.save_button = QPushButton("Save Note")
        self.save_button.setObjectName("SaveButton")
        self.save_button.clicked.connect(self.validate_and_accept)

        buttons.addButton(
            self.save_button,
            QDialogButtonBox.ButtonRole.AcceptRole,
        )
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

        if self.note:
            self.title_input.setText(self.note["title"])

            existing_category = self.note["category"] or "Personal"
            category_index = self.category_input.findText(
                existing_category
            )

            if category_index >= 0:
                self.category_input.setCurrentIndex(category_index)
            else:
                self.category_input.setCurrentIndex(0)

            self.content_input.setPlainText(
                self.note["content"] or ""
            )

        self.title_input.setFocus()

    def validate_and_accept(self):
        if not self.title_input.text().strip():
            MochiMessageDialog.show_warning(
                self,
                "Title required",
                "Please enter a title for your note.",
            )
            self.title_input.setFocus()
            return

        self.accept()

    def get_note_data(self):
        return {
            "title": self.title_input.text().strip(),
            "content": self.content_input.toPlainText(),
            "category": self.category_input.currentText(),
        }


class NotesPage(QWidget):
    """Mochi notes library."""

    def __init__(self, note_service):
        super().__init__()

        self.note_service = note_service
        self.current_category = "All Notes"

        self.build_interface()
        self.refresh_notes()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(BACKGROUND))

    def build_interface(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(10, 10, 10, 10)
        main.setSpacing(14)

        heading = QLabel("✎  Notes")
        heading.setStyleSheet("""
            font-size: 29px;
            font-weight: bold;
            color: #292B28;
            background: transparent;
        """)

        subtitle = QLabel(
            "Capture quick thoughts and organise your saved notes."
        )
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #77796F;
            background: transparent;
        """)

        main.addWidget(heading)
        main.addWidget(subtitle)

        # Search and create
        action = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search notes by title...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setMinimumHeight(42)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #FFFCF6;
                color: #292B28;
                selection-background-color: #596B55;
                selection-color: white;
                border: 1px solid #DCD5C8;
                border-radius: 10px;
                padding: 9px 13px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #81917B;
                background-color: #FFFFFF;
            }
            QLineEdit::placeholder {
                color: #858579;
            }
        """)
        self.search_input.textChanged.connect(self.refresh_notes)

        self.new_button = QPushButton("+  New Note")
        self.new_button.setObjectName("AddButton")
        self.new_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.new_button.clicked.connect(self.add_note)

        action.addWidget(self.search_input, 1)
        action.addWidget(self.new_button)

        main.addLayout(action)

        # Category filters
        filters = QHBoxLayout()
        filters.setSpacing(9)

        self.filter_buttons = {}

        for category in ["All Notes", "Personal", "Study"]:
            button = QPushButton(category)
            button.setCheckable(True)
            button.setChecked(category == self.current_category)
            button.setCursor(Qt.CursorShape.PointingHandCursor)

            button.clicked.connect(
                lambda checked=False, value=category:
                    self.set_category(value)
            )

            self.filter_buttons[category] = button
            filters.addWidget(button)

        filters.addStretch()
        main.addLayout(filters)

        # Note count
        self.count_label = QLabel("")
        self.count_label.setStyleSheet(
            "color: #77796F; font-size: 12px;"
        )
        main.addWidget(self.count_label)

        # Scrollable notes area
        self.notes_container = QWidget()
        self.notes_container.setStyleSheet(
            "background: transparent;"
        )

        self.notes_layout = QGridLayout(self.notes_container)
        self.notes_layout.setContentsMargins(2, 3, 2, 3)
        self.notes_layout.setHorizontalSpacing(13)
        self.notes_layout.setVerticalSpacing(13)
        self.notes_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )

        self.notes_layout.setColumnStretch(0, 1)
        self.notes_layout.setColumnStretch(1, 1)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.scroll.setWidget(self.notes_container)

        self.scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
            QScrollBar:vertical {
                background: #EDE7DC;
                width: 8px;
                margin: 3px 1px 3px 4px;
                border: none;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #B5B9AA;
                min-height: 35px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #899681;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
                border: none;
                background: none;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)

        self.scroll.viewport().setStyleSheet(
            "background: transparent;"
        )

        main.addWidget(self.scroll, 1)

        self.setStyleSheet("""
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
            QPushButton:checked {
                background-color: #596B55;
                color: white;
                border-color: #596B55;
                font-weight: bold;
            }
            QPushButton#AddButton {
                background-color: #596B55;
                color: white;
                border: none;
                font-weight: bold;
                padding: 10px 18px;
            }
            QPushButton#AddButton:hover {
                background-color: #465943;
            }
        """)

    def set_category(self, category):
        self.current_category = category

        for name, button in self.filter_buttons.items():
            button.setChecked(name == category)

        self.refresh_notes()

    def clear_note_cards(self):
        while self.notes_layout.count():
            item = self.notes_layout.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

    def refresh_notes(self):
        self.clear_note_cards()

        query = self.search_input.text().strip().casefold()
        notes = self.note_service.get_all_notes()

        if query:
            search_words = query.split()

            notes = [
                note for note in notes
                if all(
                    word in (note["title"] or "").casefold()
                    for word in search_words
                )
            ]

        if self.current_category != "All Notes":
            notes = [
                note for note in notes
                if (note["category"] or "Personal")
                == self.current_category
            ]

        self.count_label.setText(
            f"{len(notes)} note{'s' if len(notes) != 1 else ''}"
        )

        if not notes:
            empty = QLabel(
                "No notes found.\nCreate a new note to get started."
            )
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("""
                color: #77796F;
                font-size: 16px;
                padding: 45px;
                background: transparent;
            """)

            self.notes_layout.addWidget(empty, 0, 0, 1, 2)
            return

        for index, note in enumerate(notes):
            row = index // 2
            column = index % 2

            card = self.create_note_card(note)
            self.notes_layout.addWidget(card, row, column)

    def create_note_card(self, note):
        card = QFrame()
        card.setObjectName("NoteCard")
        card.setFixedHeight(NOTE_CARD_HEIGHT)
        card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        card.setStyleSheet("""
            QFrame#NoteCard {
                background-color: #FFFCF6;
                border: 1px solid #E9E2D6;
                border-radius: 15px;
            }
            QLabel {
                background: transparent;
                border: none;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(17, 15, 17, 14)
        layout.setSpacing(8)

        title = QLabel(note["title"])
        title.setWordWrap(True)
        title.setMaximumHeight(42)
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #292B28;
        """)

        category = QLabel(
            f"●  {note['category'] or 'Personal'}"
        )
        category.setStyleSheet("""
            font-size: 11px;
            color: #596B55;
        """)

        content_text = note["content"] or "No content yet."
        if len(content_text) > 145:
            content_text = content_text[:145].rstrip() + "..."

        content = QLabel(content_text)
        content.setWordWrap(True)
        content.setMaximumHeight(48)
        content.setStyleSheet("""
            font-size: 12px;
            color: #77796F;
        """)

        updated = QLabel(
            self.format_updated(note["updated_at"])
        )
        updated.setStyleSheet("""
            font-size: 10px;
            color: #99988F;
        """)

        actions = QHBoxLayout()

        edit_button = QPushButton("Edit")
        delete_button = QPushButton("Delete")

        edit_button.clicked.connect(
            lambda checked=False, item=note:
                self.edit_note(item)
        )
        delete_button.clicked.connect(
            lambda checked=False, item=note:
                self.delete_note(item)
        )

        actions.addWidget(updated)
        actions.addStretch()
        actions.addWidget(edit_button)
        actions.addWidget(delete_button)

        layout.addWidget(title)
        layout.addWidget(category)
        layout.addWidget(content, 1)
        layout.addLayout(actions)

        return card

    @staticmethod
    def format_updated(timestamp):
        try:
            value = datetime.fromisoformat(timestamp)
            return "Updated " + value.strftime("%d %b %Y, %I:%M %p")
        except (TypeError, ValueError):
            return "Saved note"

    def add_note(self):
        dialog = NoteEditorDialog(self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        data = dialog.get_note_data()

        try:
            self.note_service.create_note(**data)
        except ValueError as error:
            MochiMessageDialog.show_warning(
                self,
                "Unable to save note",
                str(error),
            )
            return

        self.set_category("All Notes")
        self.search_input.clear()
        self.refresh_notes()

    def edit_note(self, note):
        dialog = NoteEditorDialog(self, note)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        data = dialog.get_note_data()

        try:
            updated = self.note_service.update_note(
                note["id"],
                **data,
            )
        except ValueError as error:
            MochiMessageDialog.show_warning(
                self,
                "Unable to update note",
                str(error),
            )
            return

        if updated is not None:
            self.refresh_notes()

    def delete_note(self, note):
        confirmed = MochiMessageDialog.ask_confirmation(
            self,
            "Delete note?",
            f'Are you sure you want to delete "{note["title"]}"? '
            "This action cannot be undone.",
        )

        if not confirmed:
            return

        self.note_service.delete_note(note["id"])
        self.refresh_notes()
