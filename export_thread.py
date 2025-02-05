from typer import Typer

from app.application.service.push.notice.coffee_chat_service import 커피챗


cli = Typer()


@cli.command()
def export_thread(url: str) -> None:
    service = 커피챗()
    messages = service.export_thread(url)


if __name__ == "__main__":
    cli()
