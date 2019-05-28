import cmd_handler

from config import Config
from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage
)

app = Flask(__name__, static_url_path='', static_folder='')
app.config.from_object(Config)
db = SQLAlchemy(app)


line_bot_api = LineBotApi(app.config['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(app.config['CHANNEL_SECRET'])


@app.route('/', methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info('Request body: ' + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def command_handler(event):
    response = cmd_handler.handle(event)
    if response:
        line_bot_api.reply_message(event.reply_token, response)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
