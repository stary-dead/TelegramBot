import telebot
from telebot import types
from telebot.util import quick_markup
import requests
import re
import base64
from ._translateview import TranslateView
class UserRegistrationData:
    bot = None
    env = None
    host = None
    def __init__(self, bot, env):
        if self.bot is None:
            self.bot = bot
        if self.env is None:
            self.env = env
            self.host = env.get('API_HOST')

    def set_user_authorized(self, message):
        self.update_field(message, "is_authorized", "True")

    def set_user_language(self, message, lang = "en"):
        language = ""
        if lang != 'en' and lang != 'ru':
            language = 'en'
        else:
            language = lang
        print(language)
        self.update_field(message, "language", language)

    def check_user_language(self, message, telegram_id = None):
        response = None
        if telegram_id is None:
            response = self.check_user(message)
        else:
            response = self.check_user(message, telegram_id)
        if response.status_code == 200:
            result = response.json()
            language = result.get('language')
            return language
        else:
            return "en"
    def check_user(self, message, telegram_id = None):
        if telegram_id is None:
            telegram_id = message.from_user.id
        base_url = self.host+'/users/check/'
        payload = {'telegram_id': telegram_id}            
        return requests.post(base_url, data=payload)
    def get_all_users_id(self, message):
        telegram_id = message.from_user.id
        base_url = self.host+'/users/get/'
        payload = {'telegram_id': telegram_id}            
        response =  requests.post(base_url, data=payload)
        if response.status_code == 200:
            result = response.json()
            ids = result.get('telegram_ids')
            return None, ids
        else:
            return response.status_code, False
    def is_user_authorized(self, message = None, telegram_id = None):
        response = None
        if telegram_id is None:
            response = self.check_user(message)
        else:
            response = self.check_user(message, telegram_id)
        if response.status_code == 200:
            result = response.json()
            is_authorized = result.get('is_authorized')
            return None, is_authorized
        else:
            return response.status_code, False
    def is_user_admin(self, message = None, telegram_id = None):
        response = None
        if telegram_id is None:
            response = self.check_user(message)
        else:
            response = self.check_user(message, telegram_id)
        if response.status_code == 200:
            result = response.json()
            is_admin = result.get('admin')
            return None, is_admin
        else:
            return response.status_code, False

    def update_field(self, message, field, value):
            telegram_id = message.from_user.id
            base_url = self.host + f'/users/{telegram_id}/{field}/'
            new_name = {field: value}
            response = requests.patch(base_url, json=new_name)
            if response.status_code == 200:
                print(f"{field} успешно обновлено!")
                return response.status_code, True
            print(f"Ошибка  {response.status_code} ")
            return response.status_code, False

    def update_field_photo(self, message, field, value):
        telegram_id = message.from_user.id
        base_url = self.host + f'/users/{telegram_id}/{field}/'
        files = {'avatar': (str(telegram_id)+'.jpg', base64.b64decode(value), 'image/jpeg')}
        data = {
            'telegram_id': telegram_id,
            field: value,
        }

        response = requests.patch(base_url, data=data, files=files)
        if response.status_code == 200:
            return response.status_code, True
        return response.status_code, False

    def save_name(self, message, lang = None):
        if lang == None:
            lang = self.check_user_language(message)
        text = TranslateView.get("incorrect_name", lang)
        if message.text:
            name = message.text
            pattern = r"^(\w+)$"
            is_match = re.match(pattern, name)
            if not is_match:
                self.bot.send_message(message.chat.id, text=text)
                return False
            status_code, done = self.update_field(message, field="name", value=name)

            # if done:
            #     self.bot.send_message(message.chat.id, text = "Данные успешно обновлены!", reply_markup = types.ReplyKeyboardRemove())

            return True
        else:
            self.bot.send_message(message.chat.id, text=text)
            return False
    def save_gender(self, message, lang = None):
        if lang == None:
            lang = self.check_user_language(message)
        
        text = TranslateView.get("choose_gender", lang)
        if message.text:
            gender = ""
            if message.text != "Пропустить" or message.text != "Pass":
                gender = message.text
                pattern = r"^(\w+)$"
                is_match = re.match(pattern, gender)
                if not is_match:
                    self.bot.send_message(message.chat.id, text=text)
                    return False
            status_code, done = self.update_field(message, field="gender", value=gender)
            # if done:
            #     self.bot.send_message(message.chat.id, text = "Данные успешно обновлены!", reply_markup = types.ReplyKeyboardRemove())
                
            return True
        else:
            self.bot.send_message(message.chat.id, text = text)
            return False


    def save_avatar(self, message, lang = None):
        if message.text == "Пропустить" or message.text != "Pass":
            return True
        if message.photo:
            photo = message.photo[-1]  # Выбираем последнее (самое большое) изображение из списка
            file_info = self.bot.get_file(photo.file_id)
            downloaded_file = self.bot.download_file(file_info.file_path)

            # Кодирование данных в base64
            encoded_image = base64.b64encode(downloaded_file).decode('utf-8')

            status_code, done = self.update_field_photo(message, field="avatar", value=encoded_image)
            # if done:
            #     self.bot.send_message(message.chat.id, text="Данные успешно обновлены!", reply_markup=types.ReplyKeyboardRemove())

            return True
        else:
            self.bot.send_message(message.chat.id, "Пожалуйста, отправьте изображение вашего аватара.")
            return False

    def save_age(self, message, lang = None):
        if lang == None:
            lang = self.check_user_language(message)
        
        text = TranslateView.get("send_age", lang)
        pattern = r"^(1[8-9]|[2-9][0-9]|[1-9][0-9]{2}|1000)$"
        if message.text:
            age = message.text
            is_match = re.match(pattern, age)
            if is_match:
                self.age = age
                status_code, done = self.update_field(message, field="age", value=age)
                # if done:
                #     self.bot.send_message(message.chat.id, text = "Данные успешно обновлены!", reply_markup = types.ReplyKeyboardRemove())
                
                return True
        self.bot.send_message(message.chat.id, text = text)
        return False
    def save_email(self, message, lang = None):
        if lang == None:
            lang = self.check_user_language(message)
        
        text = TranslateView.get("send_email", lang)
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        email = ""
        if message.text:
            is_match = re.match(pattern, message.text)
            
            if is_match:
                email = message.text
            if message.text == "Пропустить" or message.text == "Pass" or  is_match:
                status_code, done = self.update_field(message, field="email", value=email)
                # if done:
                #     self.bot.send_message(message.chat.id, text = "Данные успешно обновлены!", reply_markup = types.ReplyKeyboardRemove())
                
                return True
        
        self.bot.send_message(message.chat.id, text)
        return False
    def save_country(self, message, lang = None):
        country = ""
        if lang == None:
            lang = self.check_user_language(message)
        
        text = TranslateView.get("send_country", lang)
        if message.text:
            pattern = r"^(\w+)$"
            is_match = re.match(pattern, message.text)

            if is_match:
                if message.text != "Пропустить" or message.text == "Pass":
                    country = message.text
                status_code, done = self.update_field(message, field="country", value=country)
                # if done:
                #     self.bot.send_message(message.chat.id, text = "Данные успешно обновлены!", reply_markup = types.ReplyKeyboardRemove())
                return True

            else:
                self.bot.send_message(message.chat.id, text=text)
                return False
            
        else:
            self.bot.send_message(message.chat.id, text)
            return False
class CommandHandler:
    user_states = {}
    user_data = None
    user_language_cache = {}
    def check_user_language(self, message):
        chat_id = message.chat.id
        if chat_id in self.user_language_cache:
            return self.user_language_cache[chat_id]
        else:
            lang = self.user_data.check_user_language(message=message)
            self.user_language_cache[chat_id] = lang
            return lang
    def set_user_language(self, message, lang = 'en'):
        chat_id = message.chat.id
        self.user_language_cache[chat_id] = lang
        return self.user_data.set_user_language(message, lang)
    
    def is_user_processing(self, chat_id):
        return self.user_states.get(chat_id, False)
    
    def change_user_state(self, chat_id, state = False):
        try:
            self.user_states[chat_id] = state
            return True
        except KeyError as e:
            print("Пользователь не найден")
            print(e)
            return False

    def __init__(self, env, bot, db):
        self.bot = bot
        self.env = env
        if self.user_data is None:
            self.user_data = UserRegistrationData(self.bot, self.env)
    firstpage_unauthorized_ru = quick_markup({
        '🔐 Авторизация'     :{'callback_data': 'authorization'},
        '💳 Подписка'        :{'callback_data': 'subscription'},
        '⭐ Vip статус'      :{'callback_data': 'vip_status'},
        '🔤 Язык/Language'     :{'callback_data':'change_language'},
        "⏩"                :{'callback_data':'next_page'}
    }, row_width=1)

    firstpage_authorized_ru = quick_markup({
        '🏆 Мои достижения'  :{'callback_data': 'my_achievements'},
        '🔄 Изменить данные' :{'callback_data': 'edit_data'},
        '💳 Подписка'        :{'callback_data': 'subscription'},
        '⭐ Vip статус'      :{'callback_data': 'vip_status'},
        '🔤 Язык/Language'     :{'callback_data':'change_language'},
        '⏩'                :{'callback_data':'next_page'}
    }, row_width=1)

    lastpage_authorized_ru = quick_markup({
        '🌐 О проекте'               :{'callback_data': 'about_project'},
        '👫 Пригласить друга'        :{'callback_data': 'invite_friend'},
        '🎉 Фестиваль'               :{'callback_data': 'festival'},
        '🏔️ Путешествия в Тибет'     :{'callback_data': 'tibet_travels'},
        'Twitter'                   :{'url': 'https://twitter.com'},
        'Facebook'                   :{'url': 'https://facebook.com'},
        '⏪'                         :{'callback_data': 'previous_page'},
    }, row_width=1, )

    lastpage_unauthorized_ru = quick_markup({
        '🌐 О проекте'               :{'callback_data': 'about_project'},
        '🎉 Фестиваль'               :{'callback_data': 'festival'},
        '🏔️ Путешествия в Тибет'     :{'callback_data': 'tibet_travels'},
        'Twitter'                   :{'url': 'https://twitter.com'},
        'Facebook'                   :{'url': 'https://facebook.com'},
        '⏪'                         :{'callback_data': 'previous_page'},
    }, row_width=1)

    firstpage_unauthorized_en = quick_markup({
        '🔐 Authorization' : {'callback_data': 'authorization'},
        '💳 Subscription' : {'callback_data': 'subscription'},
        '⭐ Vip status'    : {'callback_data': 'vip_status'},
        '🔤 Language/Язык'     :{'callback_data':'change_language'},
        "⏩"              : {'callback_data':'next_page'}
    }, row_width=1)

    firstpage_authorized_en = quick_markup({
        '🏆 My achievements' : {'callback_data': 'my_achievements'},
        '🔄 Edit data'      : {'callback_data': 'edit_data'},
        '💳 Subscription'  : {'callback_data': 'subscription'},
        '⭐ Vip status'     : {'callback_data': 'vip_status'},
        '🔤 Language/Язык'     :{'callback_data':'change_language'},
        "⏩"               : {'callback_data':'next_page'}
    }, row_width=1)

    lastpage_authorized_en = quick_markup({
        '🌐 About project'        : {'callback_data': 'about_project'},
        '👫 Invite friend'        : {'callback_data': 'invite_friend'},
        '🎉 Festival'             : {'callback_data': 'festival'},
        '🏔️ Travels to Tibet'   : {'callback_data': 'tibet_travels'},
        'Twitter'                : {'url': 'https://twitter.com'},
        'Facebook'               : {'url': 'https://facebook.com'},
        '⏪'                      : {'callback_data': 'previous_page'},
    }, row_width=1)

    lastpage_unauthorized_en = quick_markup({
        '🌐 About project'        : {'callback_data': 'about_project'},
        '🎉 Festival'             : {'callback_data': 'festival'},
        '🏔️ Travels to Tibet'   : {'callback_data': 'tibet_travels'},
        'Twitter'                : {'url': 'https://twitter.com'},
        'Facebook'               : {'url': 'https://facebook.com'},
        '⏪'                      : {'callback_data': 'previous_page'},
    }, row_width=1)



    @staticmethod
    def create_keyboard_firstpage(is_authorized, lang='en'):
        if is_authorized:
            if lang == 'ru':
                CommandHandler.firstpage_authorized_ru.width = 6
                return CommandHandler.firstpage_authorized_ru
            else:
                return CommandHandler.firstpage_authorized_en
        else:
            if lang == 'ru':
                return CommandHandler.firstpage_unauthorized_ru
            else:
                return CommandHandler.firstpage_unauthorized_en

    @staticmethod
    def create_keyboard_lastpage(is_authorized, lang = 'en'):
        if is_authorized:
            if lang == 'ru':
                return CommandHandler.lastpage_authorized_ru
            else:
                return CommandHandler.lastpage_authorized_en
        else:
            if lang == 'ru':
                return CommandHandler.lastpage_unauthorized_ru
            else:
                return CommandHandler.lastpage_unauthorized_en

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
    
    def send_menu(self, message, page = 1):
        lang = self.check_user_language(message=message)
        text = TranslateView.get("menu", lang)
        errors, is_authorized = self.user_data.is_user_authorized(message)
        if errors is None:
            self.bot.send_message(message.chat.id, text = text, reply_markup = self.create_keyboard_firstpage(is_authorized, lang))
        else:
            self.bot.send_message(message.chat.id, text = f"Произошла ошибка {errors}, попробуйте позже", reply_markup = types.ReplyKeyboardRemove())
class NextPageCommandHandler(CommandHandler):
    @staticmethod
    def info():
        """Returns routing information for the 'Edit Data' command"""
        return ("callback_data", {"data": ["next_page"]})

    def main(self, call):
        chat_id = call.message.chat.id
        telegram_id = call.from_user.id
        lang = self.check_user_language(call.message)
        errors, is_authorized = self.user_data.is_user_authorized(call.message, telegram_id=telegram_id) # Здесь бот редактирует СВОЁ сообщение, поэтому нужно явно передать в функцию telegram_id пользователя
        if errors is None:
            self.bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=self.create_keyboard_lastpage(is_authorized, lang))
        else:
            self.bot.send_message(chat_id, text = f"Произошла ошибка {errors}, попробуйте позже", reply_markup = types.ReplyKeyboardRemove())
        self.bot.answer_callback_query(call.id)
class PreviousPageCommandHandler(CommandHandler):
    @staticmethod
    def info():
        """Returns routing information for the 'Edit Data' command"""
        return ("callback_data", {"data": ["previous_page"]})

    def main(self, call):
        chat_id = call.message.chat.id
        telegram_id = call.from_user.id
        lang = self.check_user_language(call.message)
        errors, is_authorized = self.user_data.is_user_authorized(call.message, telegram_id=telegram_id) # Здесь бот редактирует СВОЁ сообщение, поэтому нужно явно передать в функцию telegram_id пользователя
        if errors is None:
            self.bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=self.create_keyboard_firstpage(is_authorized, lang))
        else:
            self.bot.send_message(chat_id, text = f"Произошла ошибка {errors}, попробуйте позже", reply_markup = types.ReplyKeyboardRemove())
        self.bot.answer_callback_query(call.id)
class StartCommandHandler(CommandHandler):

    @staticmethod
    def info():
        """Returns routing information for the start command"""
        return ("command", {"commands": ["start"]})

    def main(self, message):
        """Function to handle the /start command"""
        chat_id = message.chat.id
        response = self.user_data.check_user(message)
        if response.status_code == 200:
            result = response.json()
            if result.get('exists'):
                user_language = self.check_user_language(message=message)
                self.bot.send_message(chat_id, text = TranslateView.get("welcome_back_text", user_language))
                self.send_menu(message)
        elif response.status_code == 201:
            user_language = message.from_user.language_code
            self.user_data.set_user_language(message=message, lang = user_language)
            self.user_language_cache[message.chat.id] = user_language
            self.bot.send_message(chat_id, TranslateView.get("welcome_text", user_language))
            self.send_menu(message)
        else:
            self.bot.send_message(chat_id, f"Error {response.status_code} occurred while checking user existence.")
            self.send_menu(message)
            print(response.json())
class AdminBroadcastCommandHandler(CommandHandler):

    @staticmethod
    def info():
        """Returns routing information for the start command"""
        return ("command", {"commands": ["broadcast"]})

    def main(self, message):
        """Function to handle the /start command"""
        chat_id = message.from_user.id
        errors, is_admin = self.user_data.is_user_admin(message=message, telegram_id=message.from_user.id)
        if (errors is None) and is_admin:
            lang = self.check_user_language(message)
            text = TranslateView.get("broadcast", lang)
            self.bot.register_next_step_handler(message, self.broadcast)
            self.change_user_state(chat_id, True)
            self.bot.send_message(chat_id, text)
    def broadcast(self, message):
        errors, telegram_ids = self.user_data.get_all_users_id(message=message)
        copied_message = message.text if message.text else None

        media = []
        if message.photo:
            fileID = message.photo[-1].file_id   
            media.append(telebot.types.InputMediaPhoto(fileID, caption=message.caption))
        if message.video:
            media.append(telebot.types.InputMediaVideo(media=message.video.file_id, caption=message.caption))
        if message.voice:
            media.append(telebot.types.InputMediaAudio(media=message.voice.file_id, caption=message.caption))
            
        if message.video_note:
                media.append(telebot.types.InputMediaVideo(media=message.video_note.file_id, caption=message.caption))
        
        
        # Отправляем все медиафайлы пользователю одним сообщением
        if message.text:
            for id in telegram_ids:
                try:   
                    self.bot.send_message(id, message.text)
                except Exception as e:
                    print(e)
                    print(f"id Пользователя {id}")
                finally:
                    continue
        if(media != []):
            for id in telegram_ids:  
                try: 
                    self.bot.send_media_group(id, media) 
                except Exception as e:
                    print(e)
                    print(f"id пользователя {id}")
                finally:
                    continue   # 
        self.change_user_state(message.chat.id, False)
        # Копируем текст сообщения
        # copied_message = message.text if message.text else None
        # if copied_message:
        # # Отправляем скопированное сообщение пользователю
        #     self.bot.send_message(message.chat.id, copied_message)
class MenuCommandHandler(CommandHandler):

    @staticmethod
    def info():
        """Returns routing information for the start command"""
        return ("command", {"commands": ["menu"]})

    def main(self, message):
        chat_id = message.chat.id
        self.bot.clear_step_handler_by_chat_id(chat_id)
        self.change_user_state(chat_id)
        self.send_menu(message)
        # self.bot.edit_message_reply_markup(chat_id=chat_id, message_id=last_message.message_id, reply_markup=self.create_keyboard_firstpage())      
class HelpCommandHandler(CommandHandler):
    @staticmethod
    def info():
        """Returns routing information for the start command"""
        return ("command", {"commands": ["help"]})

    def main(self, message):
        """Function to handle the /start command"""
        chat_id = message.chat.id
        lang = self.check_user_language(message)
        text = TranslateView.get("help", lang)
        self.bot.send_message(chat_id, text)
class ChangeLanguageCommandHandler(CommandHandler):
    @staticmethod
    def info():
        """Returns routing information for the start command"""
        return ("callback_data", {"data": ["change_language"]})

    def main(self, call):
        message = call.message
        chat_id = message.chat.id
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        ru_button = types.KeyboardButton("Русский")
        en_button = types.KeyboardButton("English")
        keyboard.add(ru_button, en_button)
        self.bot.clear_step_handler_by_chat_id(chat_id)
        self.bot.answer_callback_query(call.id)
        self.bot.register_next_step_handler(message, self.choose_language)
        self.change_user_state(chat_id, True)
        self.bot.send_message(chat_id, "Выбери язык/Choose a language", reply_markup=keyboard)
    
    def choose_language(self, message):
        chat_id = message.chat.id
        if message.text:
            text = message.text
            if text == "Русский":
                self.set_user_language(message=message, lang='ru')
                self.change_user_state(chat_id, False)
                self.bot.send_message(chat_id, TranslateView.get('change_language', 'ru'), reply_markup = types.ReplyKeyboardRemove())
                self.send_menu(message)
                return
            elif text == 'English':
                self.set_user_language(message=message, lang='en')
                self.change_user_state(chat_id, False)
                self.bot.send_message(chat_id, TranslateView.get('change_language', 'en'), reply_markup = types.ReplyKeyboardRemove())
                self.send_menu(message)
                return
        self.bot.register_next_step_handler(message, self.choose_language)
        self.bot.send_message(chat_id, "Выбери язык/Choose a language") 
class AuthorizationCommandHandler(CommandHandler):
    @staticmethod
    def info():
        """Returns routing information for the authorization command"""
        return ("callback_data", {"data": ["authorization"]})

    def main(self, call):
        chat_id = call.message.chat.id
        self.bot.clear_step_handler_by_chat_id(chat_id)
        self.request_name(call.message)
        self.change_user_state(chat_id, True)
        self.bot.answer_callback_query(call.id)


    def request_name(self, message):
        chat_id = message.chat.id
        self.bot.send_message(chat_id, text="Введите имя")
        self.bot.register_next_step_handler(message, self.request_gender)

    def request_gender(self, message):
        if self.user_data.save_name(message):
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            male_button = types.KeyboardButton("Мужской")
            female_button = types.KeyboardButton("Женский")
            pass_button = types.KeyboardButton("Пропустить")
            keyboard.add(male_button, female_button, pass_button)
            self.bot.send_message(message.chat.id, "Теперь выбери пол или укажи свой", reply_markup=keyboard)
            self.bot.register_next_step_handler(message, self.request_avatar)
        else:
            self.bot.register_next_step_handler(message, self.request_gender)

    def request_avatar(self, message):
        if self.user_data.save_gender(message):
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            pass_button = types.KeyboardButton("Пропустить")
            keyboard.add(pass_button)
            self.bot.send_message(message.chat.id, "Пришли мне свой аватар", reply_markup=keyboard)
            self.bot.register_next_step_handler(message, self.request_age)
        else:
            self.bot.register_next_step_handler(message, self.request_avatar)

    def request_age(self, message):
        if self.user_data.save_avatar(message):
            self.bot.register_next_step_handler(message, self.request_email)
            self.bot.send_message(message.chat.id, "Пожалуйста, пришлите ваш возраст.", reply_markup = types.ReplyKeyboardRemove())
        else:
            self.bot.register_next_step_handler(message, self.request_age)

    def request_email(self, message):
        if self.user_data.save_age(message):
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            pass_button = types.KeyboardButton("Пропустить")
            keyboard.add(pass_button)
            self.bot.send_message(message.chat.id, "Пришли мне свой email", reply_markup=keyboard)
            self.bot.register_next_step_handler(message, self.request_country)
        else:
            self.bot.register_next_step_handler(message, self.request_email)

    def request_country(self, message):
        if self.user_data.save_email:
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            pass_button = types.KeyboardButton("Пропустить")
            keyboard.add(pass_button)
            self.bot.send_message(message.chat.id, "Пришли мне свою страну проживания", reply_markup=keyboard)
            self.bot.register_next_step_handler(message, self.cancel_registration)
        else:
            self.bot.register_next_step_handler(message, self.request_country)
    
    def cancel_registration(self, message):
        if self.user_data.save_country:
            self.bot.send_message(message.chat.id, "Успешная регистрация!", reply_markup=types.ReplyKeyboardRemove())
            self.user_data.set_user_authorized(message)
            self.change_user_state(message.chat.id)
            self.send_menu(message)
        else:
            self.bot.register_next_step_handler(message, self.cancel_registration)
class MyAchievementsCommandHandler(CommandHandler):
    @staticmethod
    def info():
        """Returns routing information for the 'My Achievements' command"""
        return ("callback_data", {"data": ["my_achievements"]})

    def main(self, call):
        chat_id = call.message.chat.id
        self.bot.clear_step_handler_by_chat_id(chat_id)
        self.bot.send_message(chat_id, text="Вы нажали кнопку 'Мои достижения'.")
        self.bot.answer_callback_query(call.id)
class EditDataCommandHandler(CommandHandler):
    @staticmethod
    def info():
        """Returns routing information for the 'Edit Data' command"""
        return ("callback_data", {"data": ["edit_data"]})
    def main(self, call):
        chat_id = call.message.chat.id     
        lang = self.check_user_language(call.message)
        self.bot.clear_step_handler_by_chat_id(chat_id)   
        self.change_user_state(chat_id, True)
        text = TranslateView.get("ask_changes", language=lang)
        self.bot.send_message(chat_id, text=text)
        keyboard = types.ReplyKeyboardMarkup(row_width=6, resize_keyboard=True)
        first_button = types.KeyboardButton("1")
        second_button = types.KeyboardButton("2")
        third_button = types.KeyboardButton("3")
        fourth_button = types.KeyboardButton("4")
        fifth_button = types.KeyboardButton("5")
        sixth_button = types.KeyboardButton("6")
        keyboard.add(first_button, second_button, third_button, fourth_button, fifth_button, sixth_button)
        text = TranslateView.get("list_changes", language=lang)
        text = text.replace('\\n', '\n')
        self.bot.send_message(chat_id, text=text , reply_markup = keyboard)
        self.bot.register_next_step_handler(call.message, self.choise_items)
        self.bot.answer_callback_query(call.id)

    def choise_items(self, message):
        if message.text:
            item = message.text
            lang = self.check_user_language(message)
            match item:
                case "1":
                    text = TranslateView.get("send_name", lang)
                    self.bot.send_message(message.chat.id, text=text, reply_markup = types.ReplyKeyboardRemove())
                    self.bot.register_next_step_handler(message, self.handle_name_edit)
                case "2":
                    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                    male_text = TranslateView.get("male", lang)
                    female_text = TranslateView.get("female", lang)
                    pass_text = TranslateView.get("pass", lang)
                    male_button = types.KeyboardButton(male_text)
                    female_button = types.KeyboardButton(female_text)
                    pass_button = types.KeyboardButton(pass_text)
                    keyboard.add(male_button, female_button, pass_button)
                    text = TranslateView.get("choose_gender", lang)
                    self.bot.send_message(message.chat.id, text=text, reply_markup = keyboard)
                    self.bot.register_next_step_handler(message, self.handle_gender_edit)
                case "3":
                    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                    pass_text = TranslateView.get("pass", lang)
                    pass_button = types.KeyboardButton(pass_text)
                    keyboard.add(pass_button)

                    text = TranslateView.get("send_avatar", lang)
                    self.bot.send_message(message.chat.id, text=text, reply_markup = keyboard)
                    self.bot.register_next_step_handler(message, self.handle_avatar_edit)
                case "4":
                    text = TranslateView.get("send_age", lang)
                    self.bot.send_message(message.chat.id, text=text, reply_markup = types.ReplyKeyboardRemove())
                    self.bot.register_next_step_handler(message, self.handle_age_edit)
                case "5":
                    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                    pass_text = TranslateView.get("pass", lang)
                    pass_button = types.KeyboardButton(pass_text)
                    keyboard.add(pass_button)
                    text = TranslateView.get("send_email", lang)
                    self.bot.send_message(message.chat.id, text=text, reply_markup = keyboard)
                    self.bot.register_next_step_handler(message, self.handle_email_edit)
                case "6":
                    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                    pass_text = TranslateView.get("pass", lang)
                    pass_button = types.KeyboardButton(pass_text)
                    keyboard.add(pass_button)
                    text = TranslateView.get("send_country", lang)
                    self.bot.send_message(message.chat.id, text=text, reply_markup = keyboard)
                    self.bot.register_next_step_handler(message, self.handle_country_edit)
                case _:
                    text = TranslateView.get("choose_one", lang)
                    self.bot.send_message(message.chat.id, text=text)
                    self.bot.register_next_step_handler(message, self.choise_items)

    def handle_name_edit(self, message):
        if self.user_data.save_name(message):
            self.change_user_state(message.chat.id)
            self.bot.send_message(message.chat.id, text = "Данные успешно обновлены!", reply_markup = types.ReplyKeyboardRemove())
            self.send_menu(message)
        else:
            self.bot.register_next_step_handler(message, self.handle_name_edit)

    def handle_gender_edit(self, message):
        if self.user_data.save_gender(message):
            self.change_user_state(message.chat.id)
            self.bot.send_message(message.chat.id, text = "Данные успешно обновлены!", reply_markup = types.ReplyKeyboardRemove())
            self.send_menu(message)
        else:
            self.bot.register_next_step_handler(message, self.handle_gender_edit)
    def handle_avatar_edit(self, message):
        if self.user_data.save_avatar(message):
            self.change_user_state(message.chat.id)
            self.bot.send_message(message.chat.id, text = "Данные успешно обновлены!", reply_markup = types.ReplyKeyboardRemove())
            self.send_menu(message)
        else:
            self.bot.register_next_step_handler(message, self.handle_avatar_edit)
    def handle_age_edit(self, message):
        if self.user_data.save_age(message):
            self.change_user_state(message.chat.id)
            self.bot.send_message(message.chat.id, text = "Данные успешно обновлены!", reply_markup = types.ReplyKeyboardRemove())
            self.send_menu(message)
        else:
            self.bot.register_next_step_handler(message, self.handle_age_edit)
    def handle_email_edit(self, message):
        if self.user_data.save_email(message):
            self.change_user_state(message.chat.id)
            self.bot.send_message(message.chat.id, text = "Данные успешно обновлены!", reply_markup = types.ReplyKeyboardRemove())
            self.send_menu(message)
        else:
            self.bot.register_next_step_handler(message, self.handle_email_edit)
    def handle_country_edit(self, message):
        if self.user_data.save_country(message):
            self.change_user_state(message.chat.id)
            self.bot.send_message(message.chat.id, text = "Данные успешно обновлены!", reply_markup = types.ReplyKeyboardRemove())
            self.send_menu(message)
        else:
            self.bot.register_next_step_handler(message, self.handle_country_edit)
class SubscriptionCommandHandler(CommandHandler):
    @staticmethod
    def info():
        """Returns routing information for the 'Subscription' command"""
        return ("callback_data", {"data": ["subscription"]})

    def main(self, call):
        chat_id = call.message.chat.id
        self.bot.clear_step_handler_by_chat_id(chat_id)
        self.bot.send_message(chat_id, text="Вы нажали кнопку 'Подписка'.")
        self.bot.answer_callback_query(call.id)
class VipStatusCommandHandler(CommandHandler):
    @staticmethod
    def info():
        """Returns routing information for the 'Vip Status' command"""
        return ("callback_data", {"data": ["vip_status"]})

    def main(self, call):
        chat_id = call.message.chat.id
        self.bot.clear_step_handler_by_chat_id(chat_id)
        self.bot.send_message(chat_id, text="Вы нажали кнопку 'Vip статус'.")
        self.bot.answer_callback_query(call.id)
class AboutProjectCommandHandler(CommandHandler):
    @staticmethod
    def info():
        """Returns routing information for the 'About Project' command"""
        return ("callback_data", {"data": ["about_project"]})

    def main(self, call):
        chat_id = call.message.chat.id
        self.bot.clear_step_handler_by_chat_id(chat_id)
        self.bot.send_message(chat_id, text="Вы нажали кнопку 'О проекте'.")
        self.bot.answer_callback_query(call.id)
class InviteFriendCommandHandler(CommandHandler):
    @staticmethod
    def info():
        """Returns routing information for the 'Invite Friend' command"""
        return ("callback_data", {"data": ["invite_friend"]})

    def main(self, call):
        chat_id = call.message.chat.id
        self.bot.clear_step_handler_by_chat_id(chat_id)
        self.bot.send_message(chat_id, text="Вы нажали кнопку 'Пригласить друга'.")
        self.bot.answer_callback_query(call.id)
class FestivalCommandHandler(CommandHandler):
    @staticmethod
    def info():
        """Returns routing information for the 'Festival' command"""
        return ("callback_data", {"data": ["festival"]})

    def main(self, call):
        chat_id = call.message.chat.id
        self.bot.clear_step_handler_by_chat_id(chat_id)
        self.bot.send_message(chat_id, text="Вы нажали кнопку 'Фестиваль'.")
        self.bot.answer_callback_query(call.id)
class TibetTravelsCommandHandler(CommandHandler):
    @staticmethod
    def info():
        """Returns routing information for the 'Tibet Travels' command"""
        return ("callback_data", {"data": ["tibet_travels"]})

    def main(self, call):
        chat_id = call.message.chat.id
        self.bot.clear_step_handler_by_chat_id(chat_id)
        self.bot.send_message(chat_id, text="Вы нажали кнопку 'Путешествия в Тибет'.")
        self.bot.answer_callback_query(call.id)