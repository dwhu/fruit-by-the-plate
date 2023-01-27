import os
import mimetypes
import requests

from flask import Flask, request, render_template
from twilio.twiml.messaging_response import MessagingResponse
from logging.config import dictConfig
from urllib.parse import urlparse

REQUIRED_NUMBER = '+13145803913'

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


@app.route('/')
@app.route('/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)


@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    body = request.values.get('Body', None)

    message_sid = request.values.get('MessageSid', '')
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
        for (media_url, mime_type) in media_files:
            file_extension = mimetypes.guess_extension(mime_type)
            media_sid = os.path.basename(urlparse(media_url).path)
            file_name = '{sid}{ext}'.format(sid=media_sid, ext=file_extension)
            app.logger.info(media_url)

            resp.message("Uploaded")

    return str(resp)

