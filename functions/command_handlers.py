import telebot
from telebot import types
from telebot.util import quick_markup
import requests
import re
class CommandHandler:
    """Handler for the /start command"""
    def __init__(self, env, bot, db):
        self.bot = bot

    @staticmethod
    def create_keyboard():
        markup = quick_markup({
        'Авторизация🔐': {'callback_data': 'authorization'},
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
        telegram_id = message.from_user.id
        api_url = 'http://127.0.0.1:8000/users/check/'
        payload = {'telegram_id': telegram_id}
        response = requests.post(api_url, data=payload)

        if response.status_code == 200:
            result = response.json()
            if result.get('exists'):
                self.bot.send_message(chat_id, "Hello! Welcome back to our bot.", reply_markup=self.create_keyboard())
        elif response.status_code == 201:
            self.bot.send_message(chat_id, "Hello! Welcome to our bot.", reply_markup=self.create_keyboard())
        else:
            self.bot.send_message(chat_id, f"Error {response.status_code} occurred while checking user existence.", reply_markup=self.create_keyboard())
            print(response.json())
class HelpCommandHandler(CommandHandler):
    @staticmethod
    def info():
        """Returns routing information for the start command"""
        return ("command", {"commands": ["help"]})

    def main(self, message):
        """Function to handle the /start command"""
        chat_id = message.chat.id
        self.bot.send_message(chat_id, "How i can help you?", reply_markup=self.create_keyboard())

class AuthorizationCommandHandler(CommandHandler):
    @staticmethod
    def info():
        """Returns routing information for the authorization command"""
        return ("callback_data", {"data": ["authorization"]})

    def main(self, call):
        chat_id = call.message.chat.id
        self.bot.send_message(chat_id, text="Введите имя")
        # Устанавливаем состояние, что ожидается имя от пользователя
        self.bot.register_next_step_handler(call.message, self.save_name)

    def save_name(self, message):
        if message.text:
            name = message.text
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            male_button = types.KeyboardButton("Мужской")
            female_button = types.KeyboardButton("Женский")
            pass_button = types.KeyboardButton("Пропустить")
            keyboard.add(male_button, female_button, pass_button)
            self.bot.send_message(message.chat.id, "Теперь выбери пол или введи свой", reply_markup = keyboard)
            self.bot.register_next_step_handler(message, self.save_gender)
        else:
            self.bot.send_message(message.chat.id, text="Пожалуйста, введите имя")
            self.bot.register_next_step_handler(message, self.save_name)

    def save_gender(self, message):
        if message.text:
            gender = ""
            if message.text !="Пропустить":
                gender = message.text
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            pass_button = types.KeyboardButton("Пропустить")
            keyboard.add(pass_button)
            self.bot.send_message(message.chat.id, "Пришли мне свой аватар", reply_markup = keyboard)
            self.bot.register_next_step_handler(message, self.save_avatar)
        else:
            self.bot.send_message(message.chat.id, "Пожалуйста, выбери пол")
            self.bot.register_next_step_handler(message, self.save_gender)

    def save_avatar(self, message):
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        if message.text == "Пропустить":
            self.bot.send_message(message.chat.id, "Сколько тебе лет?", reply_markup=types.ReplyKeyboardRemove())
            self.bot.register_next_step_handler(message, self.save_age)
            return
        if message.photo:
            photo = message.photo[-1]  # Выбираем последнее (самое большое) изображение из списка
            file_info = self.bot.get_file(photo.file_id)
            downloaded_file = self.bot.download_file(file_info.file_path)

            with open('avatar.jpg', 'wb') as new_file:
                new_file.write(downloaded_file)

            self.bot.register_next_step_handler(message, self.save_age)
            self.bot.send_message(message.chat.id, "Cколько тебе лет?", reply_markup=types.ReplyKeyboardRemove())
        else:
            self.bot.register_next_step_handler(message, self.save_avatar)
            self.bot.send_message(message.chat.id, "Пожалуйста, отправьте изображение вашего аватара.")

    def save_age(self, message):
        pattern = r"^(1[8-9]|[2-9][0-9]|[1-9][0-9]{2}|1000)$"
        if message.text:
            age = message.text
            is_match = re.match(pattern, age)
            if is_match:
                keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                pass_button = types.KeyboardButton("Пропустить")
                keyboard.add(pass_button)
                self.bot.register_next_step_handler(message, self.save_email)
                self.bot.send_message(message.chat.id, "Пожалуйста, пришлите ваш email.", reply_markup = keyboard)
                return
        self.bot.register_next_step_handler(message, self.save_age)
        self.bot.send_message(message.chat.id, "Пожалуйста, пришлите корректный возраст")

    def save_email(self, message):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if message.text:
            email = message.text
            is_match = re.match(pattern, email)
            if is_match or message.text == "Пропустить":
                self.bot.register_next_step_handler(message, self.save_country)
                self.bot.send_message(message.chat.id, "Из какой вы страны?")
                return

        self.bot.register_next_step_handler(message, self.save_age)
        self.bot.send_message(message.chat.id, "Пожалуйста, пришлите корректный возраст")
    
    def save_country(self, message):
        if message.text:
            country = message.text
            self.bot.send_message(message.chat.id, "Успешная регистрация!", reply_markup=types.ReplyKeyboardRemove())
            self.bot.send_message(message.chat.id, "Меню:", reply_markup=self.create_keyboard())


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