
from .section_page import SectionPage


class FocusPage(SectionPage):
    def __init__(self):
        super().__init__(
            "Focus",
            "Make time for focused work and productive breaks.",
            "◷",
        )
