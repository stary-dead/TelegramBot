import telebot
from telebot.util import quick_markup
class CommandHandler:
    """Handler for the /start command"""
    def __init__(self, env, bot, db):
        self.bot = bot

    @staticmethod
    def create_keyboard():
        keyboard = telebot.types.InlineKeyboardMarkup()
        # start_button = telebot.types.InlineKeyboardMarkup()
        # help_button = telebot.types.InlineKeyboardMarkup("Help")

        markup = quick_markup({
        'Twitter': {'url': 'https://twitter.com'},
        'Facebook': {'url': 'https://facebook.com'},
        'Back': {'callback_data': 'back'}
    }, row_width=2)

        return markup

    @staticmethod
    def info():
        """Returns routing information for the start command"""
        raise NotImplementedError
    @classmethod
    def init(self, env, bot, db):
        """Returns the function passed to the handler"""
        instance = self(env, bot, db)
        return instance.main

    def main(self, message):
        """Function to handle the /start command"""
        raise NotImplementedError
    
class StartCommandHandler(CommandHandler):
    @staticmethod
    def info():
        """Returns routing information for the start command"""
        return ("command", {"commands": ["start"]})

    def main(self, message):
        """Function to handle the /start command"""
        chat_id = message.chat.id
        self.bot.send_message(chat_id, "Hello! Welcome to our bot.", reply_markup=self.create_keyboard())

class HelpCommandHandler(CommandHandler):
    @staticmethod
    def info():
        """Returns routing information for the start command"""
        return ("command", {"commands": ["help"]})

    def main(self, message):
        """Function to handle the /start command"""
        chat_id = message.chat.id
        self.bot.send_message(chat_id, "How i can help you?", reply_markup=self.create_keyboard())

class CallbackCommandHandler(CommandHandler):
    @staticmethod
    def info():
        """Returns routing information for the start command"""
        return ("callback_data", {"data": ["back"]})

    def main(self, call):
        call_id = call.id
        self.bot.answer_callback_query(call_id, text="You pressed 'Back' button.")

