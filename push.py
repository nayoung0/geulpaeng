from typer import Typer


cli = Typer()


@cli.command()
def check(channel: Channel):
    print(channel)


if __name__ == "__main__":
    cli()
