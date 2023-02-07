import os

from instagram import Instagram
from flask import Flask, request, render_template, send_from_directory
from twilio.twiml.messaging_response import MessagingResponse
from logging.config import dictConfig

CREDS_FILE = "/data/creds"
REQUIRED_NUMBER = os.getenv('REQUIRED_NUMBER')
BASE_URL = os.getenv('BASE_URL')
if BASE_URL is None or BASE_URL == "":
    BASE_URL = "http://127.0.0.1"

app = Flask(__name__)
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://sys.stdout',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

instagram = Instagram(app.logger)


@app.route('/')
def hello():
    return render_template('hello.html')


@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)


@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy-policy.html')


@app.route("/auth/response")
def redirect_path():
    query_params = request.args
    if "error" in query_params or "code" not in query_params:
        return render_template('error.html')
    access_token = query_params.get("access_token")
    ig_account_id = instagram.get_instgram_account_id(access_token)
    with open(CREDS_FILE, "r+") as f:
        f.write(f"{ig_account_id},{access_token}")
    return render_template('success.html')


@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    from_number = request.values.get('From', '')
    num_media = int(request.values.get('NumMedia', 0))
    media_files = [(request.values.get("MediaUrl{}".format(i), ''),
                    request.values.get("MediaContentType{}".format(i), ''))
                   for i in range(0, num_media)]

    resp = MessagingResponse()
    if from_number != REQUIRED_NUMBER:
        resp = MessagingResponse()
        resp.message("Only accepting messages from %s", REQUIRED_NUMBER)
        return str(resp)
    else:
        with open(CREDS_FILE, "r") as f:
            creds = f.read()
            [ig_id, access_token] = creds.split(",")
            for (media_url, mime_type) in media_files:
                app.logger.info(media_url)
                instagram.post_image(ig_id, access_token, media_url, "Today's Post")

        resp.message("Uploaded")

    return str(resp)
