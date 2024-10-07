from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class Authorization:
    enterprise_id: Optional[str]
    team_id: str
    user_id: str
    is_bot: bool
    is_enterprise_install: bool


@dataclass
class Event:
    client_msg_id: str
    type: str
    text: Optional[str]
    user: str
    ts: str
    team: str
    thread_ts: Optional[str]
    parent_user_id: Optional[str]
    channel: str
    event_ts: str
    blocks: Optional[List[Dict]] = field(default_factory=list)


@dataclass
class SlackEvent:
    token: str
    team_id: str
    api_app_id: str
    event: Event
    type: str
    event_id: str
    event_time: int
    authorizations: List[Authorization]
    is_ext_shared_channel: bool
    event_context: str
    challenge: Optional[str] = None

    def is_url_verification(self) -> bool:
        return self.type == "url_verification"

    def is_emoji_check(self) -> bool:
        for word in self.__VALID_REAUEST[0]["trigger_word"]:
            if word in self.event_text:
                return True

        return False


@dataclass
class EventType:
    challenge = "url_verification"
    app_mention = "event_callback"
    app_home_opened = "app_home_opened"
    channel_created = "channel_created"
    channel_deleted = "channel_deleted"


class EventTriggerWord:
    remind_users_did_not_react = ["체크", "이모지"]
