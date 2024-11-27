from enum import Enum
from typer import Typer


class Channel(str, Enum):
    다진마늘 = "다진마늘"
    책읽어또 = "책읽어또"


class Checker:
    def check(self):
        raise NotImplementedError


class 다진마늘(Checker):
    def check(self):
        pass


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
