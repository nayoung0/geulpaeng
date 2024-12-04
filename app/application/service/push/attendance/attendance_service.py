import os
from gspread import service_account_from_dict, Worksheet
from typing import Type, TypeVar
from dataclasses import fields
from abc import abstractmethod
from dotenv import load_dotenv

from app.adapter.output.slack import SlackClient

T = TypeVar("T")


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


class AttendanceService:
    def __init__(self) -> None:
        if not os.getenv("SHEETS_ID"):
            raise ValueError("SHEETS_ID is not set")
        if not os.getenv("GEULTTO_SLACK_TOKEN"):
            raise ValueError("GEULTTO_SLACK_TOKEN is not set")

        self.slack = SlackClient(os.getenv("GEULTTO_SLACK_TOKEN"))
        self.sheets = gc.open_by_key(os.getenv("SHEETS_ID"))

    @property
    def sheet(self) -> Worksheet:
        if not hasattr(self, "sheet_title") or self.sheet_title is None:
            raise ValueError("sheet_title is not set")
        return self.sheets.worksheet(self.sheet_title)

    @abstractmethod
    def check(self) -> None:
        pass

    @classmethod
    def convert_records_to_models(
        cls, records: list[dict[str, object]], model: Type[T]
    ) -> list[T]:
        return [
            model(
                **{
                    k: v
                    for k, v in record.items()
                    if k in {f.name for f in fields(model)}
                }
            )
            for record in records
        ]

    def get_sheet_records_to(self, model: Type[T]) -> list[T]:
        records = self.sheet.get_all_records()
        return self.convert_records_to_models(records, model)

    def update_members(self) -> None:
        if not hasattr(self, "slack_channel_id") or self.slack_channel_id is None:
            raise ValueError("slack_channel_id is not set")

        sheet = self.sheets.worksheet("참여자")

        sheet_records = {record["user"] for record in sheet.get_all_records()}
        slack_records = set(self.slack.get_conversation_members(self.slack_channel_id))

        missing_records = slack_records - sheet_records

        rows_to_append = [
            [user, self.slack.get_user_name(user)] for user in missing_records
        ]

        if rows_to_append:
            sheet.append_rows(rows_to_append)
