import os

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# U061KKYNMFX 는 dev 환경
BOT_USERS = set(
    ['U066GTQMFS8', 'U066N3G33L2', 'U066QUVFD8A', 'U067CSZN472', 'U066T0Q8J01', 'U06790T7S2E', 'U061KKYNMFX'])


class SlackClient:
    def __init__(self):
        self.client = WebClient(os.environ['TOKEN'])

    def __get_response(self, response):
        if not response['ok']:
            raise SlackApiError(response['error'])
        return response

    def get_member_id_by_channel(self, channel_id, cursor=None):
        response = self.client.conversations_members(
            channel=channel_id,
            cursor=cursor
        )
        response = self.__get_response(response)
        member_id = response['members']

        next_cursor = response['response_metadata']['next_cursor']
        if next_cursor:
            member_id += self.get_member_id_by_channel(channel_id, next_cursor)
        return member_id

    def get_member_from_reactions(self, reactions):
        if not reactions:
            return

        user_id = set(list())
        for reaction in reactions:
            user_id.update(reaction['users'])
        return list(user_id)

    def get_reaction_members(self, channel_id, timestamp):
        response = self.client.reactions_get(
            channel=channel_id,
            timestamp=timestamp
        )
        response = self.__get_response(response)

        if not 'reactions' in response['message'].keys():
            return []
        reactions = response['message']['reactions']

        user_id = self.get_member_from_reactions(reactions)
        return user_id

    def __formating_user_id(self, users):
        user_list = ''
        for user in users:
            user_list += '<@' + user + '> '
        return user_list

    def send_remind_message(self, channel_id, timestamp, users):
        user_list = self.__formating_user_id(users)
        response = self.client.chat_postMessage(
            channel=channel_id,
            text=user_list + '혹시 .. 메시지를 확인하셨나요? 이모지를 남겨주세요',
            thread_ts=timestamp
        )
        response = self.__get_response(response)
        return

    def send_message(self, channel_id, message):
        response = self.client.chat_postMessage(
            channel=channel_id,
            text=message
        )
        response = self.__get_response(response)
        return

    def alert_user(self, channel_id, user, timestamp):
        response = self.client.chat_postMessage(
            channel=channel_id,
            text='모든 유저가 이 공지를 확인했어요!',
            user=user,
            thread_ts=timestamp,
            link_names=True
        )
        response = self.__get_response(response)
        return

    def get_bot_user(self):
        response = self.client.bots_info()
        self.__get_response(response)
        return

    def get_message_info(self, channel_id, timestamp):
        response = self.client.conversations_history(
            channel=channel_id,
            oldest=timestamp,
            limit=1,
            inclusive=True
        )
        response = self.__get_response(response)
        return response['messages'][0]['text']