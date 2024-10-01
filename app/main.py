from flask import Flask
from app.container import Container
from app.event.adapter.input.api.event import event_router


def create_app():
    app = Flask(__name__)

    container = Container()
    container.wire(modules=[__name__, "app.event.adapter.input.api.event"])
    app.container = container

    app.register_blueprint(event_router)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
