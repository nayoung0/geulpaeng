from datetime import datetime
import os
import time
from gspread import service_account_from_dict
from dotenv import load_dotenv

from app.adapter.output.slack import SlackClient

load_dotenv()

gc = service_account_from_dict(
    {
        "type": "service_account",
        "project_id": os.getenv("PROJECT_ID"),
        "private_key_id": os.getenv("PRIVATE_KEY_ID"),
        "private_key": os.getenv("PRIVATE_KEY").replace("\\n", "\n"),
        "client_email": os.getenv("CLIENT_EMAIL"),
        "client_id": os.getenv("CLIENT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.getenv("CLIENT_X509_CERT_URL"),
        "universe_domain": "googleapis.com",
    }
)


class 커피챗:
    def __init__(self) -> None:
        if not os.getenv("SHEETS_ID"):
            raise ValueError("SHEETS_ID is not set")
        if not os.getenv("GEULTTO_SLACK_TOKEN"):
            raise ValueError("GEULTTO_SLACK_TOKEN is not set")
        if not os.getenv("SLACK_COFFEE_CHAT_CHANNEL_ID"):
            raise ValueError("SLACK_COFFEE_CHAT_CHANNEL_ID is not set")

        self.slack = SlackClient(os.getenv("GEULTTO_SLACK_TOKEN"))
        self.sheets = gc.open_by_key(os.getenv("SHEETS_COFFEECHAT_ID"))

    def notice(self) -> None:
        sheet = self.sheets.worksheet("export")

        records = sheet.get_all_records()

        user_ids = self.get_all_user_ids(records)
        self.slack.invite_users_to_channel(
            channel_id=os.getenv("SLACK_COFFEE_CHAT_CHANNEL_ID"),
            user_ids=user_ids,
        )

        formatted_records = self.format_records(records)

        for group_id, record in formatted_records:
            self.send_coffee_chat_message(record, group_id)
            time.sleep(2)

    def format_records(self, records: list[dict]) -> list[tuple[int, str]]:
        groups = {}

        for record in records:
            group_id = record["group"]
            if group_id not in groups:
                groups[group_id] = []
            groups[group_id].append(f"<@{record['id']}>")

        return [
            (group_id, ", ".join(members))
            for group_id, members in sorted(groups.items())
        ]

    def get_all_user_ids(self, records: list[dict]) -> list[str]:
        user_ids = [record["id"] for record in records]
        unique_user_ids = list(set(user_ids))
        return ",".join(unique_user_ids)

    def send_coffee_chat_message(self, record: str, team_number: int) -> None:
        response = self.slack.post(
            channel_id=os.getenv("SLACK_COFFEE_CHAT_CHANNEL_ID"),
            message=f"{team_number}팀 커피챗 멤버 공유드려요: {record}",
        )

        self.send_coffee_chat_instructions(response["ts"])

    def send_coffee_chat_instructions(self, thread_ts: str) -> None:
        self.slack.reply(
            channel_id=os.getenv("SLACK_COFFEE_CHAT_CHANNEL_ID"),
            timestamp=thread_ts,
            message=(
                "- 선호하는 위치, 일자를 3-4개 정도 말씀해주세요. (자세히 말씀해주실수록 좋습니다.)\n"
                "- 위 내용을 토대로 일정을 조율해주세요."
            ),
        )

    def export_thread(self, url: str) -> None:
        channel_id, thread_ts = self.parse_slack_url(url)

        messages = self.slack.get_conversations_replies(channel_id, thread_ts)

        for message in messages:
            user = message["user"]
            text = " ".join(message["text"].split())
            ts = self.format_timestamp(message["ts"])
            name = self.slack.get_user_name(user)

            print(f"{ts}|{name}|{user}|{text}")

        return messages

    def parse_slack_url(self, url: str) -> tuple[str, str]:
        parts = url.split("/")
        channel_id = parts[-2]
        timestamp = parts[-1]

        thread_ts = timestamp[1:]
        thread_ts = f"{thread_ts[:-6]}.{thread_ts[-6:]}"

        return channel_id, thread_ts

    def format_timestamp(self, ts: str) -> str:
        timestamp = float(ts)
        dt = datetime.fromtimestamp(timestamp)

        am_pm = "오후" if dt.hour >= 12 else "오전"
        hour = dt.hour if dt.hour <= 12 else dt.hour - 12

        return dt.strftime(f"%Y. %m. %d {am_pm} {hour}:%M:%S")
