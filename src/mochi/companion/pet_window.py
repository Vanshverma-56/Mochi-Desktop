from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QPoint


class PetWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.drag_position = QPoint()

        self.setWindowTitle("Mochi Companion")
        self.setFixedSize(120, 120)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )

        layout = QVBoxLayout(self)

        character = QLabel("🐱")
        character.setAlignment(Qt.AlignmentFlag.AlignCenter)
        character.setStyleSheet("font-size: 64px;")

        layout.addWidget(character)

        self.setStyleSheet(
            "background-color: #E9DCCB;"
            "border-radius: 24px;"
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.move(
                event.globalPosition().toPoint()
                - self.drag_position
            )