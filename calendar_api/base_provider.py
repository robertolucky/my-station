
from abc import ABC, abstractmethod
import typing
from typing import NamedTuple

class CalendarEvent(NamedTuple):
    event_id: str
    summary: str
    start: any
    end: any
    all_day_event: bool
    event_organizer: str

class BaseCalendarProvider(ABC):

    @abstractmethod
    def get_calendar_events(self) -> list[CalendarEvent]:
        """
        Implement this method.
        Return a list of `CalendarEvent` which contains summary, start date, end date, and all day event
        """
        pass


