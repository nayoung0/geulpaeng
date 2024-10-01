from dataclasses import dataclass


@dataclass
class Event:
    text: str


class EventProcessor:
    def process_event(self, event_data: dict) -> Event:
        event_text = event_data.get("event", {}).get("text", "")
        return Event(text=event_text)
