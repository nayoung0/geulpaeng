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

    def push(self) -> None:
        sheet = self.sheets.worksheet("export")

        records = sheet.get_all_records()
        formatted_records = self.format_records(records)

        for index, record in enumerate(formatted_records, 1):
            self.send_coffee_chat_message(record, index)
            time.sleep(2)

    def format_records(self, records: list[dict]) -> list[str]:
        groups = {}

        for record in records:
            group_id = record["group"]
            if group_id not in groups:
                groups[group_id] = []
            groups[group_id].append(f"<@{record['id']}>")

        return [", ".join(members) for _, members in sorted(groups.items())]

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
