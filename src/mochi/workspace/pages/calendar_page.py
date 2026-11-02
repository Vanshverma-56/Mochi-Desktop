
from .section_page import SectionPage


class CalendarPage(SectionPage):
    def __init__(self):
        super().__init__(
            "Calendar",
            "Manage your schedule, events and reminders.",
            "▦",
        )
