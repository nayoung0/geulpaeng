import os
import gspread
from abc import abstractmethod
from functools import cached_property
from dotenv import load_dotenv

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


class Checker:
    def __init__(self):
        if not os.getenv("SHEETS_ID"):
            raise ValueError("SHEETS_ID is not set")
        if not os.getenv("GEULTTO_SLACK_TOKEN"):
            raise ValueError("GEULTTO_SLACK_TOKEN is not set")

        self.slack = SlackClient(os.getenv("GEULTTO_SLACK_TOKEN"))
        self.sheets = gc.open_by_key(os.getenv("SHEETS_ID"))

    @abstractmethod
    def check(self):
        pass

    @property
    def sheet(self):
        if not hasattr(self, "sheet_title") or self.sheet_title is None:
            raise ValueError("sheet_title is not set")
        return self.sheets.worksheet(self.sheet_title)

    def get_sheet_records(self):
        return self.sheet.get_all_records()
