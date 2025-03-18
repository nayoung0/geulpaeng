from typer import Typer

from app.application.service.push.notice.coffee_chat_service import 커피챗


cli = Typer()


@cli.command()
def notice_coffee_chat() -> None:
    service = 커피챗()
    service.notice()


if __name__ == "__main__":
    cli()
