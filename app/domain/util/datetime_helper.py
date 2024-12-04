from datetime import datetime
import calendar
from zoneinfo import ZoneInfo


KST = ZoneInfo("Asia/Seoul")


class DatetimeHelper:
    @staticmethod
    def now() -> datetime:
        return datetime.now(tz=KST)

    @staticmethod
    def from_timestamp(timestamp: int) -> datetime:
        return datetime.fromtimestamp(timestamp, tz=KST)

    @staticmethod
    def format(dt: datetime, format: str = "%Y-%m-%d %H:%M:%S") -> str:
        dt = dt.astimezone(KST)
        return dt.strftime(format)

    @staticmethod
    def start_of_day(dt: datetime) -> datetime:
        dt = dt.astimezone(KST)
        return dt.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

    @staticmethod
    def start_of_month(dt: datetime) -> datetime:
        dt = dt.astimezone(KST)
        return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def end_of_month(dt: datetime) -> datetime:
        dt = dt.astimezone(KST)
        _, last_day = calendar.monthrange(dt.year, dt.month)

        return dt.replace(
            day=last_day,
            hour=23,
            minute=59,
            second=59,
            microsecond=999999,
        )
