
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFrame,
)
from PySide6.QtCore import Qt


class SectionPage(QWidget):
    def __init__(self, title, description, icon):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(18)

        heading = QLabel(f"{icon}  {title}")
        heading.setStyleSheet("""
            font-size: 29px;
            font-weight: bold;
            color: #292B28;
        """)

        subtitle = QLabel(description)
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #77796F;
        """)

        placeholder = QFrame()
        placeholder.setStyleSheet("""
            QFrame {
                background-color: #FFFCF6;
                border: 1px solid #E9E2D6;
                border-radius: 18px;
            }
        """)

        placeholder_layout = QVBoxLayout(placeholder)
        placeholder_layout.setContentsMargins(25, 25, 25, 25)

        message = QLabel(
            f"Your {title.lower()} space is being prepared."
        )
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setStyleSheet("""
            font-size: 17px;
            color: #77796F;
        """)

        placeholder_layout.addWidget(message)

        layout.addWidget(heading)
        layout.addWidget(subtitle)
        layout.addWidget(placeholder, 1)
