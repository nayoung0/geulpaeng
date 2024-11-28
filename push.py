from typer import Typer

from app.application.service.push.book_read_service import 책읽어또
from app.application.service.push.minced_garlic_service import 다진마늘
from app.domain.model.push import Channel


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
