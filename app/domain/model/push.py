from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Type, TypeVar


class Channel(str, Enum):
    다진마늘 = "다진마늘"
    책읽어또 = "책읽어또"


T = TypeVar("T")


@dataclass(frozen=True)
class AttendanceRecord:
    timestamp: str
    user: str

    @classmethod
    def from_records(cls: Type[T], records: List[Dict[str, Any]]) -> List[T]:
        return [cls(**record) for record in records]


@dataclass(frozen=True)
class MincedGarlicAttendanceRecord(AttendanceRecord):
    date: str
