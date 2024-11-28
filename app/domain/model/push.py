from dataclasses import dataclass, fields
from enum import Enum
from typing import Any, Dict, List, Type, TypeVar


class Channel(str, Enum):
    다진마늘 = "다진마늘"
    책읽어또 = "책읽어또"


T = TypeVar("T")


@dataclass(frozen=True, eq=False)
class AttendanceRecord:
    timestamp: str
    user: str

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.timestamp == other.timestamp and self.user == other.user

    def __hash__(self) -> int:
        return hash((self.timestamp, self.user))

    @classmethod
    def from_records(cls: Type[T], records: List[Dict[str, Any]]) -> List[T]:
        return [cls(**record) for record in records]


@dataclass(frozen=True, eq=False)
class MincedGarlicAttendanceRecord(AttendanceRecord):
    date: str


@dataclass(frozen=True, eq=False)
class BookReadRecord(AttendanceRecord):
    title: str
    days: int
    content: str
    text: str

    @classmethod
    def from_records(cls: Type[T], records: List[Dict[str, Any]]) -> List[T]:
        return [
            cls(
                **{
                    k: v
                    for k, v in record.items()
                    if k in {f.name for f in fields(cls)}
                }
            )
            for record in records
        ]
