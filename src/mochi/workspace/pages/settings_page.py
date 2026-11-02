
from .section_page import SectionPage


class SettingsPage(SectionPage):
    def __init__(self):
        super().__init__(
            "Settings",
            "Personalise Mochi and manage your application preferences.",
            "⚙",
        )
