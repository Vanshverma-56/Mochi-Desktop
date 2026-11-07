from PySide6.QtCore import QSettings
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QFrame,
)


class SettingsPage(QWidget):
    """Application preferences for Mochi."""

    def __init__(self, pomodoro):
        super().__init__()

        self.pomodoro = pomodoro
        self.settings = QSettings("Mochi", "Mochi")

        self.build_interface()

    def build_interface(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(10, 10, 10, 10)
        main.setSpacing(16)

        heading = QLabel("Settings")
        heading.setStyleSheet("""
            font-size: 29px;
            font-weight: bold;
            color: #292B28;
            background: transparent;
        """)

        subtitle = QLabel(
            "Personalise Mochi and manage your application preferences."
        )
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #77796F;
            background: transparent;
        """)

        main.addWidget(heading)
        main.addWidget(subtitle)

        sound_card = QFrame()
        sound_card.setObjectName("SettingsCard")

        card_layout = QVBoxLayout(sound_card)
        card_layout.setContentsMargins(22, 20, 22, 20)
        card_layout.setSpacing(13)

        sound_heading = QLabel("Focus completion sound")
        sound_heading.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #292B28;
            background: transparent;
        """)

        description = QLabel(
            "Choose the sound Mochi plays when a focus or break "
            "session finishes."
        )
        description.setWordWrap(True)
        description.setStyleSheet("""
            font-size: 13px;
            color: #77796F;
            background: transparent;
        """)

        sound_row = QHBoxLayout()

        self.sound_combo = QComboBox()
        self.sound_combo.addItems([
            "Default",
            "Chime",
            "Alert",
            "Gentle",
        ])

        saved_sound = self.settings.value(
            "focus/completion_sound",
            "Default",
        )

        if saved_sound not in [
            "Default", "Chime", "Alert", "Gentle"
        ]:
            saved_sound = "Default"

        self.sound_combo.setCurrentText(saved_sound)
        self.sound_combo.currentTextChanged.connect(
            self.save_sound
        )

        preview_button = QPushButton("Preview sound")
        preview_button.setObjectName("PrimaryButton")
        preview_button.clicked.connect(self.preview_sound)

        sound_row.addWidget(self.sound_combo, 1)
        sound_row.addWidget(preview_button)

        card_layout.addWidget(sound_heading)
        card_layout.addWidget(description)
        card_layout.addLayout(sound_row)

        main.addWidget(sound_card)
        main.addStretch()

        self.setStyleSheet("""
            QFrame#SettingsCard {
                background-color: #FFFCF6;
                border: 1px solid #E9E2D6;
                border-radius: 16px;
            }

            QComboBox {
                background: #FFFCF6;
                color: #292B28;
                border: 1px solid #E9E2D6;
                border-radius: 8px;
                padding: 9px;
                min-width: 120px;
            }

            QComboBox QAbstractItemView {
                background-color: #FFFCF6;
                color: #292B28;
                selection-background-color: #596B55;
                selection-color: white;
                border: 1px solid #E9E2D6;
                outline: 0;
                padding: 4px;
            }

            QComboBox QAbstractItemView::item {
                min-height: 30px;
                padding: 6px 9px;
            }

            QPushButton {
                background-color: #EAE5DA;
                color: #454940;
                border: 1px solid #E4DED2;
                border-radius: 9px;
                padding: 10px 16px;
            }

            QPushButton#PrimaryButton {
                background-color: #596B55;
                color: white;
                border: none;
                font-weight: bold;
            }

            QPushButton#PrimaryButton:hover {
                background-color: #465843;
            }
        """)

    def save_sound(self, sound):
        self.settings.setValue(
            "focus/completion_sound",
            sound,
        )

    def preview_sound(self):
        self.pomodoro.preview_sound(
            self.sound_combo.currentText()
        )
