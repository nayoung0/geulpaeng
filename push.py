from enum import Enum
from typer import Typer


class Channel(str, Enum):
    다진마늘 = "다진마늘"
    책읽어또 = "책읽어또"


cli = Typer()


@cli.command()
def check(channel: Channel):
    print(channel)


if __name__ == "__main__":
    cli()
