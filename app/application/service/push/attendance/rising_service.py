import os
import re
from datetime import datetime

from app.application.service.push.attendance.attendance_service import AttendanceService
from app.domain.model.attendance import Channel, RisingAttendanceRecord
from app.domain.util.datetime_helper import KST, DatetimeHelper


class 일어났또(AttendanceService):
    def __init__(self) -> None:
        super().__init__()
        self.sheet_title = Channel.일어났또.value
        self.slack_channel_id = os.getenv("RISING_CHANNEL_ID")

    def check(self) -> None:
        self.sheet.append_rows(self.get_missing_records())

    def get_missing_records(self) -> list[list[str]]:
        sheet_records = self.get_sheet_records_to(RisingAttendanceRecord)
        slack_records = self.get_slack_records()

        missing_records = list(set(slack_records) - set(sheet_records))
        sorted_records = sorted(missing_records, key=lambda x: x.timestamp)

        return [
            [record.date, record.timestamp, record.user] for record in sorted_records
        ]

    def get_slack_records(self) -> list[RisingAttendanceRecord]:
        bot_message_timestamps = self.get_bot_message_timestamps()
        messages = self.find_attendance_messages(bot_message_timestamps)
        sorted_messages = sorted(messages, key=lambda x: x["ts"])

        return [
            RisingAttendanceRecord(
                date=DatetimeHelper.format(
                    DatetimeHelper.from_timestamp(float(message["thread_ts"])),
                    "%m/%d",
                ),
                timestamp=DatetimeHelper.format(
                    DatetimeHelper.from_timestamp(float(message["ts"]))
                ),
                user=message["user"],
            )
            for message in sorted_messages
        ]

    def get_bot_message_timestamps(self) -> list[str]:
        oldest = str(int(self.rising_service_period_start().timestamp()))

        messages = self.slack.get_all_conversation_histories(
            self.slack_channel_id, oldest=oldest
        )

        if not messages:
            raise ValueError("No messages found")

        return [
            message["thread_ts"]
            for message in messages
            if message["user"] == "USLACKBOT" and message.get("thread_ts")
        ]

    def find_attendance_messages(
        self, bot_message_timestamps: list[str]
    ) -> list[dict[str, object]]:
        keyword_pattern = re.compile(r"출석")
        time_pattern = re.compile(r"(?:0?[0-9]|1[0-9]|2[0-3]):(?:[0-5][0-9])")

        return [
            message
            for timestamp in bot_message_timestamps
            for message in self.slack.get_conversations_replies(
                os.getenv("RISING_CHANNEL_ID"), timestamp
            )
            if message["type"] == "message"
            and message["user"] != "USLACKBOT"
            and (
                keyword_pattern.search(message["text"])
                and time_pattern.search(message["text"])
            )
        ]

    def rising_service_period_start(self) -> datetime:
        dt = DatetimeHelper.now().astimezone(KST)
        return dt.replace(month=1, day=6, hour=0, minute=0, second=0, microsecond=0)
