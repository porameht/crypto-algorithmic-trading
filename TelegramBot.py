import telebot

class TelegramBot:
    def __init__(self, config):
        self.config = config
        self.user_id = config['telegram_user_id']
        self.group_id = config['telegram_group_id']
        self.bot_token = config['telegram_bot_token']
        self.bot = telebot.TeleBot(self.bot_token, parse_mode=None) # You can set parse_mode by default. HTML or MARKDOWN

    def send_message(self, message):
        self.bot.send_message(chat_id=self.user_id, text=message)
        
    def send_message_group(self, message):
        self.bot.send_message(chat_id=self.group_id, text=message)
    
# https://api.telegram.org/bot7300328807:AAGhdyXF3hCNG0fUsyLTmBmPhFmZB3igqf4/getMe
# https://api.telegram.org/bot7300328807:AAECRGfasgaIcK0BRiX2wEKcY1xBam2JyWQ/getUpdates
# Hello User(first_name='แถม', id=6504116081, is_bot=False, language_code='en')
