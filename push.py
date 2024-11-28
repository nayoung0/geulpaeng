import os
import gspread
import pendulum
from dotenv import load_dotenv
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


class Checker:
    def __init__(self):
        self.slack = SlackClient(os.getenv("GEULTTO_SLACK_TOKEN"))
        self.sheets = gc.open_by_key(os.getenv("SHEETS_ID"))

    def check(self):
        raise NotImplementedError


class 다진마늘(Checker):
    def check(self):
        sheet = self.sheets.worksheet(Channel.다진마늘)
        records = sheet.get_all_records()

        print(records)
        pass

    def get_start_of_month(self, now=None):
        _now = now or pendulum.now("Asia/Seoul")
        return _now.start_of("month")

    def get_end_of_month(self, now=None):
        _now = now or pendulum.now("Asia/Seoul")
        return _now.end_of("month")


class 책읽어또(Checker):
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
