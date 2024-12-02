import os
import re
import pendulum
from typing import List

from app.application.service.push.attendance.attendance_service import AttendanceService
from app.domain.model.push import Channel, MincedGarlicAttendanceRecord


class 다진마늘(AttendanceService):
    def __init__(self):
        super().__init__()
        self.sheet_title = Channel.다진마늘.value
        self.slack_channel_id = os.getenv("MINCED_GARLIC_CHANNEL_ID")

    def check(self):
        self.sheet.append_rows(self.get_missing_records())

    def get_missing_records(self):
        sheet_records = set(
            MincedGarlicAttendanceRecord.from_records(self.get_sheet_records())
        )
        slack_records = set(
            MincedGarlicAttendanceRecord.from_records(self.get_slack_records())
        )

        missing_records = list(slack_records - sheet_records)
        sorted_missing_records = sorted(missing_records, key=lambda x: x.timestamp)

        return [
            [record.date, record.timestamp, record.user]
            for record in sorted_missing_records
        ]

    def get_slack_records(self):
        bot_message_timestamps = self.get_bot_message_timestamps()
        messages = self.find_attendance_messages(bot_message_timestamps)
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

    def get_bot_message_timestamps(self):
        oldest = str(self.get_start_of_month().int_timestamp)
        latest = str(self.get_end_of_month().int_timestamp)

        messages = self.slack.get_all_conversation_histories(
            self.slack_channel_id, oldest=oldest, latest=latest
        )

        if not messages:
            raise ValueError("No messages found")

        return [
            message["thread_ts"]
            for message in messages
            if message["user"] == "USLACKBOT" and message.get("thread_ts")
        ]

    def find_attendance_messages(self, bot_message_timestamps: List[str]):
        keyword_pattern = re.compile(r"마늘|출근")
        time_pattern = re.compile(r"(?:0?[0-9]|1[0-9]|2[0-3]):(?:[0-5][0-9])")

        return [
            message
            for timestamp in bot_message_timestamps
            for message in self.slack.get_conversations_replies(
                os.getenv("MINCED_GARLIC_CHANNEL_ID"), timestamp
            )
            if message["type"] == "message"
            and message["user"] != "USLACKBOT"
            and keyword_pattern.search(message["text"])
            and time_pattern.search(message["text"])
        ]

    def get_start_of_month(self, now=None):
        _now = now or pendulum.now("Asia/Seoul")
        return _now.start_of("month")

    def get_end_of_month(self, now=None):
        _now = now or pendulum.now("Asia/Seoul")
        return _now.end_of("month")
