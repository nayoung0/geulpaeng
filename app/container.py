from dependency_injector import containers, providers
from app.event.application.service.event_service import EventService
from app.event.domain.model.event import EventProcessor


class Container(containers.DeclarativeContainer):

    event_processor = providers.Factory(EventProcessor)
    event_service = providers.Factory(EventService, event_processor=event_processor)
