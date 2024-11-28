import os
import re
import gspread
import pendulum
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Any, Dict, List, Type, TypeVar
from abc import abstractmethod
from enum import Enum
from typer import Typer

from app.adapter.output.slack import SlackClient


load_dotenv()

gc = gspread.service_account_from_dict(
    {
        "type": "service_account",
        "project_id": os.getenv("project_id"),
        "private_key_id": os.getenv("private_key_id"),
        "private_key": os.getenv("private_key").replace("\\n", "\n"),
        "client_email": os.getenv("client_email"),
        "client_id": os.getenv("client_id"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.getenv("client_x509_cert_url"),
        "universe_domain": "googleapis.com",
    }
)


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


class Checker:
    def __init__(self):
        self.slack = SlackClient(os.getenv("GEULTTO_SLACK_TOKEN"))

    @abstractmethod
    def check(self):
        pass

    def get_sheet_records(self):
        if not os.getenv("SHEETS_ID"):
            raise ValueError("SHEETS_ID is not set")

        if not self.channel:
            raise ValueError("channel is not set")

        sheets = gc.open_by_key(os.getenv("SHEETS_ID"))
        sheet = sheets.worksheet(self.channel)
        return sheet.get_all_records()


class 다진마늘(Checker):
    def __init__(self):
        super().__init__()
        self.channel = Channel.다진마늘.value

    def check(self):
        sheet_records = set(
            GarlicAttendanceRecord.from_records(self.get_sheet_records())
        )
        slack_records = set(
            GarlicAttendanceRecord.from_records(self.get_slack_records())
        )

        missing_records = list(slack_records - sheet_records)
        sorted_missing_records = sorted(missing_records, key=lambda x: x.timestamp)

        return [
            [record.date, record.timestamp, record.user]
            for record in sorted_missing_records
        ]

    def get_slack_records(self):
        oldest = str(self.get_start_of_month().int_timestamp)
        latest = str(self.get_end_of_month().int_timestamp)

        messages = self.slack.get_all_conversation_histories(
            os.getenv("GARLIC_CHANNEL_ID"), oldest=oldest, latest=latest
        )

        if not messages:
            raise ValueError("No messages found")

        bot_message_timestamps = [
            message["thread_ts"]
            for message in messages
            if message["user"] == "USLACKBOT" and message.get("thread_ts")
        ]

        keyword_pattern = re.compile(r"마늘|출근")
        time_pattern = re.compile(r"(?:0?[0-9]|1[0-9]|2[0-3]):(?:[0-5][0-9])")

        messages = [
            message
            for timestamp in bot_message_timestamps
            for message in self.slack.conversations_replies(
                os.getenv("GARLIC_CHANNEL_ID"), timestamp
            )
            if message["type"] == "message"
            and message["user"] != "USLACKBOT"
            and keyword_pattern.search(message["text"])
            and time_pattern.search(message["text"])
        ]

        sorted_messages = sorted(messages, key=lambda x: x["ts"])

        return [
            {
                "date": pendulum.from_timestamp(float(message["thread_ts"]))
                .in_timezone("Asia/Seoul")
                .start_of("day")
                .format("MM/DD"),
                "timestamp": pendulum.from_timestamp(float(message["ts"]))
                .in_timezone("Asia/Seoul")
                .format("YYYY-MM-DD HH:mm:ss"),
                "user": message["user"],
            }
            for message in sorted_messages
        ]

    def get_start_of_month(self, now=None):
        _now = now or pendulum.now("Asia/Seoul")
        return _now.start_of("month")

    def get_end_of_month(self, now=None):
        _now = now or pendulum.now("Asia/Seoul")
        return _now.end_of("month")


class 책읽어또(Checker):
    def __init__(self):
        super().__init__()
        self.channel = Channel.책읽어또.value

    def check(self):
        pass


cli = Typer()


@cli.command()
def check(channel: Channel):
    match channel:
        case Channel.다진마늘:
            checker = 다진마늘()
        case Channel.책읽어또:
            checker = 책읽어또()

    checker.check()


if __name__ == "__main__":
    cli()
