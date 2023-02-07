import json
from flask import Flask, request, abort, jsonify
from azure_openai import ask_azure_gpt

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import os

# Use dotenv to load environment variables
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)


line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# Route / with GET method return Welcome message
@app.route("/", methods=['GET'])
def index():
    return "Welcome to OpenAI Line Bot"

# Route /message with GET method and q parameter
@app.route("/message", methods=['GET'])
def message():
    # Get query parameter
    query = request.args.get('q')
    answer = ask_azure_gpt(query)

    # return answer as json​
    return jsonify({"question": query, "answer": answer})

@app.route("/direct", methods=['POST'])
def direct():
    body = request.get_data(as_text=True)
    answer = ask_azure_gpt(body)
    return json.loads(answer)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    answer = ask_azure_gpt(event.message.text)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=answer))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print("Starting Flask OpenAI app")

    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)


