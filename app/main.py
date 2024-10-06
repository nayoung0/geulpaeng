import logging

from flask import Flask
from app.container import Container
from app.adapter.input.api.event import event_router


def create_app():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    app = Flask(__name__)

    container = Container()
    container.wire(modules=[__name__, "app.adapter.input.api.event"])
    app.container = container

    app.register_blueprint(event_router)

    logger.info("App has been created successfully.")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
