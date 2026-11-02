
from .section_page import SectionPage


class NotesPage(SectionPage):
    def __init__(self):
        super().__init__(
            "Notes",
            "Capture quick thoughts and organise your saved notes.",
            "✎",
        )
