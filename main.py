import sys
from flask import (
    Flask,
    redirect,
    request,
    jsonify,
    url_for,
    render_template,
    Response
)
from services import Event

app = Flask(__name__, static_url_path='')


@app.route('/', methods=['GET'])
def index():
    return 'hello world!'

@app.route('/event', methods=['POST'])
def check_emoji():
    payload = request.get_json()

    if request.headers.get('X-Slack-Retry-Num'):
        print("=== SLACK IS RETRYING ===")
        return jsonify({
            "response_type": "ephemeral",
            "text": ""
        })

    typ = payload.get('type')
    if typ == 'url_verification':
        return {
            'challenge': payload.get('challenge')
        }

    event = Event(payload)

    if not event.is_valid():
        return jsonify({
            "response_type": "ephemeral",
            "text": "INVALID EVENT!"
        })

    event.check_who_did_not_react()
    event.post_remind_thread()

    return jsonify({
        "response_type": "ephemeral",
        "text": "곧 확인해드릴게요!"
    })


if __name__ == '__main__':
    if len(sys.argv) > 1:
        app.debug = True
        app.jinja_env.auto_reload = True
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        app.run(host='0.0.0.0', port=8080)
    else:
        app.run(host='0.0.0.0', port=8080)