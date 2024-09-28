class Event:
    """
    """
    __VALID_EVENT_TYPE = ['app_mention']
    __VALID_REQUEST = [
        {'type': 'check_emoji', 'description': '누가 해당 글에 이모지를 달았는지 확인합니다.',
         'howto': '@매니저를 멘션하고 이모지 라는 단어를 포함시켜주시면 됩니다.', 'trigger_word': ['이모지', '확인', '체크']},
        {'type': 'check_reply', 'description': '누가 해당 글에 쓰레드를 달았는지 확인합니다.',
         'howto': '@매니저를 멘션하고 출석 이라는 단어를 포함시켜주시면 됩니다.', 'trigger_word': ['쓰레드', '댓글']},
        {'type': 'help', 'description': '명령어를 소개합니다.', 'howto': '@매니저를 멘션하고 help 단어를 포함시켜주세요.',
         'trigger_word': ['help']},
    ]

    TYPE = 'event_callback'
    event_id: str = None
    event_type: str = None
    event_text: str = None
    user_id: str = None
    channel_id: str = None
    created_at: str = None

    thread_ts: str = None  # optional
    parent_user_id: str = None
    parent_message: str = None

    not_reacted_users: set = None

    def __init__(self, payload: dict) -> None:
        event = payload.get('event', {})

        self.event_id = payload['event_id']
        self.event_type = event.get('type')
        self.event_text = event.get('text')
        self.user_id = event.get('user')
        self.channel_id = event.get('channel')
        self.created_at = event.get('event_ts')

        self.thread_ts = event.get('thread_ts')
        self.parent_user_id = event.get('parent_user_id')
        self.parent_message = None

    def is_valid(self) -> bool:
        if not self.event_type in self.__VALID_EVENT_TYPE:
            return False

        for word in self.__VALID_REQUEST[0]['trigger_word']:
            if word in self.event_text:
                return True

        return False
