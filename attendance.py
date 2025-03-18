from typer import Typer
from typing import Type

from app.domain.model.attendance import Channel
from app.application.service.push.attendance.attendance_service import AttendanceService
from app.application.service.push.attendance.book_read_service import 책읽어또
from app.application.service.push.attendance.minced_garlic_service import 다진마늘
from app.application.service.push.attendance.rising_service import 일어났또

cli = Typer()

CHANNEL_SERVICES: dict[Channel, Type[AttendanceService]] = {
    Channel.다진마늘: 다진마늘,
    Channel.책읽어또: 책읽어또,
    Channel.일어났또: 일어났또,
}


@cli.command()
def check_attendance(channel: Channel) -> None:
    service_class = CHANNEL_SERVICES.get(channel)

    if not service_class:
        raise ValueError(f"Unsupported channel: {channel}")

    service = service_class()
    service.update_members()
    service.check()


if __name__ == "__main__":
    cli()
