import os
import sys
import re
import crawler

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, ImageSendMessage
)

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
server_root = os.getenv('SERVER_ROOT', None)

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)
if server_root is None:
    print('Specify SERVER_ROOT as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


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


command_pattern = re.compile(r'heh\s(.+)')


@handler.add(MessageEvent, message=TextMessage)
def command_handler(event):
    match = command_pattern.fullmatch(event.message.text)
    if not match:
        return

    line_bot_api.reply_message(
        event.reply_token,
        [ImageSendMessage(server_root + '/' + original, server_root + '/' + preview)
         for original, preview in crawler.get_image_pairs_urls(crawler.get_paths(match.group(1)))]
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0')

