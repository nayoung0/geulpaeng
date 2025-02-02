from typer import Typer

from app.application.service.push.notice.coffeechat_service import 커피챗


cli = Typer()


@cli.command()
def notice_coffee_chat() -> None:
    service = 커피챗()
    service.push()


if __name__ == "__main__":
    cli()
