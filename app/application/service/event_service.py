import re
import json
import logging

from app.domain.model.event import SlackEvent, EventTriggerWord
from app.adapter.output.slack import SlackClient


class EventService:
    def __init__(self, slack_client: SlackClient, bot_users: str):
        self.client = slack_client
        self.bot_users = json.loads(bot_users)

        logging.info(f"Setting bot users: {self.bot_users}")

    def get_all_mentioned_user(
        self,
        slack_event: SlackEvent,
        parent_message: str,
    ) -> list:

        # TODO: change to use block's user id
        mentioned_user_gruop = re.findall(r"<!\w+>", parent_message)
        mentioned_users = re.findall(r"<@\w+>", parent_message)

        mentioned_user_group_formatted = list(
            map(lambda ug: ug[2:-1], mentioned_user_gruop)
        )
        mentioned_users_formatted = list(map(lambda u: u[2:-1], mentioned_users))

        if mentioned_user_group_formatted:
            all_mentioned_users = self.client.get_member_id_by_channel(
                channel_id=slack_event.event.get("channel"),
            )
        else:
            all_mentioned_users = mentioned_users_formatted

        return all_mentioned_users

    def check_who_did_not_react(
        self,
        slack_event: SlackEvent,
        parent_message: str,
    ) -> set:

        all_mentioned_users = self.get_all_mentioned_user(
            slack_event=slack_event,
            parent_message=parent_message,
        )
        react_members = self.client.get_reaction_members(
            channel_id=slack_event.event.get("channel"),
            timestamp=slack_event.event.get("thread_ts"),
        )
        logging.info(f"thread owner: {slack_event.event.get("parent_user_id")}")

        not_react_users = (
            set(all_mentioned_users)
            - set(react_members)
            - set(self.bot_users)
            - set([slack_event.event.get("parent_user_id")])
        )
        logging.info(f"users did not react: {not_react_users}")

        return not_react_users

    def handle_event(self, slack_event: SlackEvent) -> dict:

        for trigger_word in EventTriggerWord.remind_users_did_not_react:
            if trigger_word in slack_event.event.get("text"):
                parent_message = self.client.get_message_info(
                    channel_id=slack_event.event.get("channel"),
                    timestamp=slack_event.event.get("thread_ts"),
                )

                users = self.check_who_did_not_react(
                    slack_event=slack_event,
                    parent_message=parent_message,
                )

                if users:
                    self.client.post_remind_message(
                        channel_id=slack_event.event.get("channel"),
                        timestamp=slack_event.event.get("thread_ts"),
                        users=users,
                    )
                else:
                    self.client.post_message(
                        channel_id=slack_event.event.get("channel"),
                        user=slack_event.event.get("user"),
                        timestamp=slack_event.event.get("thread_ts"),
                        message="모든 유저가 이 공지를 확인했어요!",
                    )

        return {"text": "response"}
