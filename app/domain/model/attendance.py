from dataclasses import dataclass
from enum import Enum
from typing import TypeVar


class Channel(str, Enum):
    다진마늘 = "다진마늘"
    책읽어또 = "책읽어또"
    일어났또 = "일어났또"


T = TypeVar("T")


@dataclass(frozen=True, eq=False)
class AttendanceRecord:
    timestamp: str
    user: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.timestamp == other.timestamp and self.user == other.user

    def __hash__(self) -> int:
        return hash((self.timestamp, self.user))


@dataclass(frozen=True, eq=False)
class MincedGarlicAttendanceRecord(AttendanceRecord):
    date: str


@dataclass(frozen=True, eq=False)
class BookReadRecord(AttendanceRecord):
    title: str
    days: int
    content: str
    text: str


@dataclass(frozen=True, eq=False)
class RisingAttendanceRecord(AttendanceRecord):
    date: str
