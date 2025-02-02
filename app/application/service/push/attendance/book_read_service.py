import os
import re

from app.application.service.push.attendance.attendance_service import AttendanceService
from app.domain.model.attendance import BookReadRecord, Channel
from app.domain.util.datetime_helper import DatetimeHelper


class 책읽어또(AttendanceService):
    def __init__(self) -> None:
        super().__init__()
        self.sheet_title = Channel.책읽어또.value
        self.slack_channel_id = os.getenv("BOOK_READ_CHANNEL_ID")

    def check(self) -> None:
        self.sheet.append_rows(self.get_missing_records())

    def get_missing_records(self) -> list[list[str]]:
        sheet_records = self.get_sheet_records_to(BookReadRecord)
        slack_records = self.get_slack_records()

        missing_records = list(set(slack_records) - set(sheet_records))
        sorted_records = sorted(missing_records, key=lambda x: x.timestamp)

        return [
            [
                record.timestamp,
                record.user,
                record.title,
                record.days,
                record.content,
                record.text,
            ]
            for record in sorted_records
        ]

    def get_slack_records(self) -> list[BookReadRecord]:
        messages = self.slack.get_all_conversation_histories(self.slack_channel_id)

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
    def parse(message: dict[str, object]) -> BookReadRecord:
        timestamp = DatetimeHelper.from_timestamp(float(message["ts"]))
        formatted_timestamp = DatetimeHelper.format(timestamp)

        return BookReadRecord(
            timestamp=formatted_timestamp,
            user=message["user"],
            title=BookReadRecordParser._extract_title(message),
            days=BookReadRecordParser._extract_days(message),
            content=BookReadRecordParser._extract_content(message),
            text=message["text"].replace("&lt;", "<").replace("&gt;", ">"),
        )

    @staticmethod
    def _extract_title(message: dict[str, object]) -> str:
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
    def _extract_days(message: dict[str, object]) -> int:
        text = message["text"]
        days_pattern = re.compile(r"(\d+)일차|Day (\d+)")

        if match := days_pattern.search(text):
            if days := match.group(1) or match.group(2):
                return int(days.strip())

        return 0

    @staticmethod
    def _extract_content(message: dict[str, object]) -> str:
        # HTML 엔티티 디코딩
        text = (
            message["text"]
            .replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&amp;", "&")
        )

        # 코드 블록 마커 제거
        text = text.replace("```", "")

        # 인용 마커(> ) 제거
        # 1. 시작 부분의 '> ' 제거
        # 2. 줄바꿈 후의 '> ' 제거
        text = re.sub(r"^> ", "", text)  # 시작 부분
        text = re.sub(r"\n> ", "\n", text)  # 각 줄 시작 부분

        # 일차 패턴 찾기 및 내용 추출
        lines = text.split("\n")
        days_pattern = re.compile(r"(\d+)일차|Day (\d+)")

        for i, line in enumerate(lines):
            if days_pattern.search(line):
                return "\n".join(lines[i + 1 :]).strip()

        return ""
