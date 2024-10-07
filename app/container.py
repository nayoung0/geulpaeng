from dependency_injector import containers, providers
from app.application.service.event_service import EventService
from app.adapter.output.message.slack import SlackClient


class Container(containers.DeclarativeContainer):

    config = providers.Configuration()
    config.bot_users.from_env("BOT_USERS", "[]")
    config.slack_token.from_env("TOKEN")

    slack_client = providers.ThreadSafeSingleton(
        SlackClient,
        token=config.slack_token,
    )

    event_service = providers.Factory(
        EventService,
        slack_client=slack_client,
        bot_users=config.bot_users,
    )
