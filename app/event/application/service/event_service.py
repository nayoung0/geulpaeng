from app.event.domain.model.event import EventProcessor, Event


class EventService:

    def __init__(self, event_processor: EventProcessor):
        self.event_processor = event_processor

    def handle_event(self, event_data: dict) -> Event:
        return self.event_processor.process_event(event_data)
