import pytest

from app.main import create_app


@pytest.fixture
def app():
    app = create_app()
    app.testing = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_slack_retry_middleware(client):
    headers = {"X-Slack-Retry-Num": "1"}
    response = client.post("/event/", headers=headers)

    assert response.status_code == 200
    assert response.json == {"response_type": "ephemeral", "text": "Retrying"}
