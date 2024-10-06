import logging

from flask import request, jsonify, Blueprint
from dependency_injector.wiring import inject, Provide
from app.container import Container
from app.application.service.event_service import EventService
from app.domain.model.event import SlackEvent, EventType


logger = logging.getLogger(__name__)
event_router = Blueprint("event", __name__, url_prefix="/event")


@event_router.route("/", methods=["POST"])
@inject
def handle_event(event_service: EventService = Provide[Container.event_service]):
    event_data = request.json
    event = SlackEvent(**event_data)

    if event.type == EventType.challenge:
        return jsonify({"challenge": event.challenge}), 200

    elif event.type == EventType.app_mention:
        response = event_service.handle_event(event)
        return jsonify(response), 200

    elif event.type == EventType.app_home_opened:
        logging.info("User opened app home...")
        return jsonify({"type": EventType.app_home_opened}), 200

    else:
        return jsonify({"type": "invalid"}), 400


# TODO: split middlewares
@event_router.before_request
def handle_retry():
    if request.headers.get("X-Slack-Retry-Num"):
        logging.info("Slack is retrying...")
        return jsonify({"response_type": "ephemeral", "text": "Retrying"}), 200
