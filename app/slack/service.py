import re
from api import SlackClient, BOT_USERS


VALID_PAYLOAD_TYPE = ['url_verification', 'event_callback', 'message_action']
client = SlackClient()


class SlackService:
    """
    """
    def __init__(self):
        return

    def __set_parent_message(self) -> None:
        self.parent_message = client.get_message_info(
            self.channel_id,
            self.thread_ts
        )

    def __get_all_mentioned_user(self) -> list:
        self.__set_parent_message()

        # 메시지 속 태그된 유저를 정규식으로 뽑아냄
        # <!channel> / <@user_id>
        mentioned_user_gruop = re.findall(r'<!\w+>', self.parent_message)
        mentioned_users = re.findall(r'<@\w+>', self.parent_message)

        mentioned_user_group_formatted = list(map(lambda ug: ug[2:-1], mentioned_user_gruop))
        mentioned_users_formatted = list(map(lambda u: u[2:-1], mentioned_users))

        if mentioned_user_group_formatted:
            all_mentioned_users = client.get_member_id_by_channel(self.channel_id)
        else:
            all_mentioned_users = mentioned_users_formatted
        return all_mentioned_users

    def check_who_did_not_react(self) -> set:
        all_mentioned_users = self.__get_all_mentioned_user()
        react_members = client.get_reaction_members(self.channel_id, self.thread_ts)
        print(self.parent_user_id)
        self.not_reacted_users = set(all_mentioned_users) - set(react_members) - set(BOT_USERS) - set(
            [self.parent_user_id])
        print(self.not_reacted_users)

    def post_remind_thread(self) -> None:
        if self.not_reacted_users:
            client.send_remind_message(self.channel_id, self.thread_ts, self.not_reacted_users)
        else:
            client.alert_user(self.channel_id, self.user_id, self.thread_ts)
