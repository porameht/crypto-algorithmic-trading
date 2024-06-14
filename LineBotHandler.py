import os
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage
from linebot.exceptions import InvalidSignatureError

class LineBotHandler:
    def __init__(self, config):
        self.config = config
        self.user_id = config['line_user_id']
        self.channel_access_token = config['line_channel_access_token']
        self.line_bot_api = LineBotApi(self.channel_access_token)

    def send_message(self, message):
        self.line_bot_api.push_message(self.user_id, TextSendMessage(text=message))
