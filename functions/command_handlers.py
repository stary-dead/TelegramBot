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
        'Авторизация🔐': {'callback_data': 'autorization'},
        'Мои достижения🏆': {'callback_data': 'my_achievements'},
        'Изменить данные🔄': {'callback_data': 'edit_data'},
        'Подписка💳': {'callback_data': 'subscription'},
        'Vip статус⭐': {'callback_data': 'vip_status'},
        'О проекте🌐': {'callback_data': 'about_project'},
        'Пригласить друга👫': {'callback_data': 'invite_friend'},
        'Фестиваль🎉': {'callback_data': 'festival'},
        'Путешествия в Тибет🏔️': {'callback_data': 'tibet_travels'},
        'Twitter': {'url': 'https://twitter.com'},
        'Facebook': {'url': 'https://facebook.com'},
        'Back': {'callback_data': 'back'},
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

class AutorizationCommandHandler(CommandHandler):
    @staticmethod
    def info():
        """Returns routing information for the start command"""
        return ("callback_data", {"data": ["autorization"]})

    def main(self, call):
        chat_id = call.message.chat.id
        self.bot.send_message(chat_id, text="Вы нажали кнопку 'Авторизация.")
class MyAchievementsCommandHandler(CommandHandler):
    @staticmethod
    def info():
        """Returns routing information for the 'My Achievements' command"""
        return ("callback_data", {"data": ["my_achievements"]})

    def main(self, call):
        chat_id = call.message.chat.id
        self.bot.send_message(chat_id, text="Вы нажали кнопку 'Мои достижения'.")
        

class EditDataCommandHandler(CommandHandler):
    @staticmethod
    def info():
        """Returns routing information for the 'Edit Data' command"""
        return ("callback_data", {"data": ["edit_data"]})

    def main(self, call):
        chat_id = call.message.chat.id
        self.bot.send_message(chat_id, text="Вы нажали кнопку 'Изменить данные'.")
        

class SubscriptionCommandHandler(CommandHandler):
    @staticmethod
    def info():
        """Returns routing information for the 'Subscription' command"""
        return ("callback_data", {"data": ["subscription"]})

    def main(self, call):
        chat_id = call.message.chat.id
        self.bot.send_message(chat_id, text="Вы нажали кнопку 'Подписка'.")
        

class VipStatusCommandHandler(CommandHandler):
    @staticmethod
    def info():
        """Returns routing information for the 'Vip Status' command"""
        return ("callback_data", {"data": ["vip_status"]})

    def main(self, call):
        chat_id = call.message.chat.id
        self.bot.send_message(chat_id, text="Вы нажали кнопку 'Vip статус'.")
        

class AboutProjectCommandHandler(CommandHandler):
    @staticmethod
    def info():
        """Returns routing information for the 'About Project' command"""
        return ("callback_data", {"data": ["about_project"]})

    def main(self, call):
        chat_id = call.message.chat.id
        self.bot.send_message(chat_id, text="Вы нажали кнопку 'О проекте'.")
        

class InviteFriendCommandHandler(CommandHandler):
    @staticmethod
    def info():
        """Returns routing information for the 'Invite Friend' command"""
        return ("callback_data", {"data": ["invite_friend"]})

    def main(self, call):
        chat_id = call.message.chat.id
        self.bot.send_message(chat_id, text="Вы нажали кнопку 'Пригласить друга'.")
        

class FestivalCommandHandler(CommandHandler):
    @staticmethod
    def info():
        """Returns routing information for the 'Festival' command"""
        return ("callback_data", {"data": ["festival"]})

    def main(self, call):
        chat_id = call.message.chat.id
        self.bot.send_message(chat_id, text="Вы нажали кнопку 'Фестиваль'.")
        

class TibetTravelsCommandHandler(CommandHandler):
    @staticmethod
    def info():
        """Returns routing information for the 'Tibet Travels' command"""
        return ("callback_data", {"data": ["tibet_travels"]})

    def main(self, call):
        chat_id = call.message.chat.id
        self.bot.send_message(chat_id, text="Вы нажали кнопку 'Путешествия в Тибет'.")


