import os
import re
from typing import Any, Dict
from pendulum import from_timestamp

from app.application.service.push.base_service import Checker
from app.domain.model.push import BookReadRecord, Channel


class 책읽어또(Checker):
    def __init__(self):
        super().__init__()
        self.channel = Channel.책읽어또.value

    def check(self):
        self.sheet.append_rows(self.get_missing_records())

    def get_missing_records(self):
        sheet_records = set(BookReadRecord.from_records(self.get_sheet_records()))
        slack_records = set(BookReadRecord.from_records(self.get_slack_records()))

        missing_records = list(slack_records - sheet_records)
        sorted_missing_records = sorted(missing_records, key=lambda x: x.timestamp)

        return [
            [
                record.timestamp,
                record.user,
                record.title,
                record.days,
                record.content,
                record.text,
            ]
            for record in sorted_missing_records
        ]

    def get_slack_records(self):
        messages = self.slack.get_all_conversation_histories(
            os.getenv("BOOK_READ_CHANNEL_ID"),
        )

        valid_messages = [
            message
            for message in messages
            if message.get("text")
            and message.get("user")
            and message.get("thread_ts")
            and message.get("root")
        ]

        sorted_messages = sorted(valid_messages, key=lambda x: x["ts"])

        return [BookReadRecordParser.parse(message) for message in sorted_messages]


class BookReadRecordParser:
    @staticmethod
    def parse(message: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "timestamp": from_timestamp(float(message["ts"]))
            .in_timezone("Asia/Seoul")
            .format("YYYY-MM-DD HH:mm:ss"),
            "user": message["user"],
            "title": BookReadRecordParser._extract_title(message),
            "days": BookReadRecordParser._extract_days(message),
            "content": BookReadRecordParser._extract_content(message),
            "text": message["text"].replace("&lt;", "<").replace("&gt;", ">"),
        }

    @staticmethod
    def _extract_title(message: Dict[str, Any]) -> str:
        text = message["root"]["text"].replace("&lt;", "<").replace("&gt;", ">")

        # <URL|텍스트> 패턴 확인
        if match := re.search(r"<[^>]*\|([^>]+)>", text):
            return match.group(1).strip().replace("*", "")

        # <> 패턴 확인
        if match := re.search(r"<\s*([^>|]+?)\s*>", text):
            return match.group(1).strip().replace("*", "")

        # "읽을책" 또는 "읽은책" 패턴 확인
        pattern = r"[\[`\s]*(?:읽을책|읽은책)[\]\s`]*\s*(.*)"
        if match := re.search(pattern, text):
            return match.group(1).strip().replace("*", "").strip("[]`*- ")

        return ""

    @staticmethod
    def _extract_days(message: Dict[str, Any]) -> int:
        text = message["text"]
        if match := re.search(r"(\d+)일차", text):
            try:
                return int(match.group(1).strip())
            except ValueError:
                return 0
        return 0

    @staticmethod
    def _extract_content(message: Dict[str, Any]) -> str:
        text = message["text"].replace("&lt;", "<").replace("&gt;", ">")
        lines = text.split("\n")
        days_pattern = re.compile(r"(\d+)일차")

        for i, line in enumerate(lines):
            if days_pattern.search(line):
                return "\n".join(lines[i + 1 :]).strip()

        return ""
