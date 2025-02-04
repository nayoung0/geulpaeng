import logging

from typing import TypeVar
from slack_sdk.web.client import WebClient
from slack_sdk.errors import SlackApiError


T = TypeVar("T")


class SlackClient:
    def __init__(self, token: str) -> None:
        self.client = WebClient(token)

    def __get_response(self, response: T) -> T:
        if not response["ok"]:
            raise SlackApiError(response["error"])
        return response

    def get_member_id_by_channel(
        self, channel_id: str, cursor: None | str = None
    ) -> list[str]:
        response = self.client.conversations_members(channel=channel_id, cursor=cursor)
        response = self.__get_response(response)

        logging.info(f"Slack response: {response}")

        member_id = response["members"]

        next_cursor = response["response_metadata"]["next_cursor"]
        if next_cursor:
            member_id += self.get_member_id_by_channel(channel_id, next_cursor)
        return member_id

    def get_reaction_members(self, channel_id: str, timestamp: str) -> set[str]:
        response = self.client.reactions_get(channel=channel_id, timestamp=timestamp)
        response = self.__get_response(response)

        if "reactions" not in response["message"].keys():
            return ()
        reactions = response["message"]["reactions"]

        if not reactions:
            return ()

        user_id = set()
        for reaction in reactions:
            user_id.update(reaction["users"])
        return user_id

    def post_remind_message(
        self, channel_id: str, timestamp: str, users: list[str]
    ) -> None:
        user_list = ""
        for user in users:
            user_list += "<@" + user + "> "

        response = self.client.chat_postMessage(
            channel=channel_id,
            text=user_list + "혹시 .. 메시지를 확인하셨나요? 이모지를 남겨주세요",
            thread_ts=timestamp,
        )
        response = self.__get_response(response)
        return

    def post(self, channel_id: str, message: str) -> dict:
        response = self.client.chat_postMessage(channel=channel_id, text=message)
        return self.__get_response(response)

    def post_message(
        self, channel_id: str, user: str, timestamp: str, message: str
    ) -> None:
        response = self.client.chat_postMessage(
            channel=channel_id,
            text=message,
            user=user,
            thread_ts=timestamp,
            link_names=True,
        )
        response = self.__get_response(response)
        return

    def reply(self, channel_id: str, timestamp: str, message: str) -> dict:
        response = self.client.chat_postMessage(
            channel=channel_id, text=message, thread_ts=timestamp
        )
        return self.__get_response(response)

    def is_bot_user(self, user: str) -> bool:
        response = self.client.users_info(user=user)
        response = self.__get_response(response)
        return response["user"].get("is_bot")

    def get_message_info(self, channel_id: str, timestamp: str) -> str:
        response = self.client.conversations_history(
            channel=channel_id, oldest=timestamp, limit=1, inclusive=True
        )
        response = self.__get_response(response)
        return response["messages"][0]["text"]

    def get_conversation_history(
        self,
        channel_id: str,
        *,
        limit: int = 200,
        oldest: None | str = None,
        latest: None | str = None,
    ) -> list[dict]:
        response = self.client.conversations_history(
            channel=channel_id, limit=limit, oldest=oldest, latest=latest
        )
        return self.__get_response(response)

    def get_all_conversation_histories(
        self,
        channel_id: str,
        *,
        limit: int = 200,
        oldest: None | str = None,
        latest: None | str = None,
    ) -> list[dict]:
        all_messages = []
        cursor: None | str = None

        while True:
            response = self.client.conversations_history(
                channel=channel_id,
                limit=limit,
                oldest=oldest,
                latest=latest,
                cursor=cursor,
            )

            all_messages.extend(response["messages"])

            if not (cursor := response.get("response_metadata", {}).get("next_cursor")):
                break

        return all_messages

    def get_conversations_replies(self, channel_id: str, timestamp: str) -> list[dict]:
        response = self.client.conversations_replies(channel=channel_id, ts=timestamp)
        response = self.__get_response(response)
        return response["messages"]

    def get_conversation_members(self, channel_id: str) -> list[str]:
        response = self.client.conversations_members(channel=channel_id, limit=1000)
        response = self.__get_response(response)
        return response["members"]

    def get_user_name(self, user_id: str) -> str:
        response = self.client.users_info(user=user_id)
        response = self.__get_response(response)
        return response["user"]["real_name"]

    def invite_users_to_channel(self, channel_id: str, user_ids: str) -> None:
        response = self.client.conversations_invite(channel=channel_id, users=user_ids)
        response = self.__get_response(response)
        return response
