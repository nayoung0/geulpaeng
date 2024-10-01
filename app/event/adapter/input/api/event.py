from flask import request, jsonify, Blueprint
from dependency_injector.wiring import inject, Provide
from app.container import Container
from app.event.application.service.event_service import EventService


event_router = Blueprint("event", __name__, url_prefix="/event")


@event_router.route("/", methods=["POST"])
@inject
def handle_event(event_service: EventService = Provide[Container.event_service]):
    event_data = request.json

    if not event_data or "event" not in event_data:
        return jsonify({"error": "Invalid event data"}), 400

    processed_event = event_service.handle_event(event_data)
    return jsonify({"text": processed_event.text}), 200
