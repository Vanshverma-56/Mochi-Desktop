
from .section_page import SectionPage


class LogbookPage(SectionPage):
    def __init__(self):
        super().__init__(
            "Daily Logbook",
            "Record your days, accomplishments and reflections.",
            "▤",
        )
