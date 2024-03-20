import telebot
from telebot import types
from telebot.util import quick_markup
import requests
import re
import base64
from datetime import datetime, date, timedelta
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

    def check_promo_request(self, message):
        promo = message.text
        base_url = self.host+'/users/promo/'
        payload = {'promo': promo.lower()}            
        return requests.post(base_url, data=payload)

    
    def check_promo(self, message):
        response = self.check_promo_request(message)
        return response.status_code
    def check_user_invitation_link(self, telegram_id):
        base_url = self.host+'/users/getlink/'
        payload = {'telegram_id': telegram_id}            
        return requests.post(base_url, data=payload)
    
    def get_user_invitation_link(self, message):
        telegram_id = message.chat.id   ##############################################################################
        response = self.check_user_invitation_link(telegram_id)
        try:
            
            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                link = result.get("invitation_link")
                return False, link
            else:
                return True, "Вы превысили число приглашенных"
        except Exception as e:
            print(f"-----{e}-----")
            return False, f"Непредвиденная ошибка: {e}"
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
            response = self.check_and_create_user_request(message)
        else:
            response = self.check_and_create_user_request(message, telegram_id)
        if response.status_code == 200:
            result = response.json()
            language = result.get('language')
            return language
        else:
            return "en"
    def check_and_create_user_request(self, message, telegram_id = None):
        if telegram_id is None:
            telegram_id = message.from_user.id
        base_url = self.host+'/users/check/'
        payload = {'telegram_id': telegram_id}            
        return requests.post(base_url, data=payload)
    
    def get_all_users_id_request(self, message):
        telegram_id = message.from_user.id
        base_url = self.host+'/users/get/'
        payload = {'telegram_id': telegram_id}            
        return requests.post(base_url, data=payload)
    
    def get_all_users_id(self, message, vip = False):
        response =  self.get_all_users_id_request(message)
        if response.status_code == 200:
            result = response.json()
            if vip:
                vip_users_ids = []
                print(result)
                for user in result:
                    if user['is_vip_active']:
                        vip_users_ids.append(user['telegram_id'])
                print(vip_users_ids)
                return None, vip_users_ids
            else:
                # Return all user IDs
                all_users_ids = [user['telegram_id'] for user in result]
                print(all_users_ids)
                return None, all_users_ids
        else:
            return response.status_code, None
    def is_user_authorized(self, message = None, telegram_id = None):
        response = None
        if telegram_id is None:
            response = self.check_and_create_user_request(message)
        else:
            response = self.check_and_create_user_request(message, telegram_id)
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            is_authorized = result.get('is_authorized')
            return None, is_authorized
        else:
            return response.status_code, False
    def is_user_admin(self, message = None, telegram_id = None):
        response = None
        if telegram_id is None:
            response = self.check_and_create_user_request(message)
        else:
            response = self.check_and_create_user_request(message, telegram_id)
        if response.status_code == 200:
            result = response.json()
            is_admin = result.get('admin')
            return None, is_admin
        else:
            return response.status_code, False
    def update_field_request(self, message, field, value):
        telegram_id = message.from_user.id
        base_url = self.host + f'/users/{telegram_id}/{field}/'
        new_name = {field: value}
        return requests.patch(base_url, json=new_name)
    
    def update_field(self, message, field, value):
            response = self.update_field_request(message, field, value)
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
    
    def check_user_subscription(self, message):
        telegram_id = message.chat.id
        base_url = self.host+'/users/subscription/'
        payload = {'telegram_id': telegram_id}            
        response =  requests.post(base_url, data=payload)
        if response.status_code == 200:
            result = response.json()
            sub_start = result.get('subscription_start_date')
            if sub_start is None:
                print(result)
                return None, None
            else:
                sub_end = result.get('subscription_end_date')
                vip_start = result.get('vip_start_date')
                vip_end = result.get('vip_end_date')
                return None, ({'vip_start': vip_start, 'sub_start':sub_start, 'vip_end':vip_end, 'sub_end':sub_end})
        else:
            return response.status_code, False
    
    def extend_subscription(self, message, promo = None):
        telegram_id = message.chat.id
        base_url = self.host+'/users/subscription/extend'
        payload = {'telegram_id': telegram_id}    
        if promo:
            payload['promo'] = promo.lower()        
        response =  requests.post(base_url, data=payload)

        if response.status_code == 200 or response.status_code == 201:
            result = response.json()

            sub_start = result.get('subscription_start_date')
            sub_end = result.get('subscription_end_date')
            vip_start = result.get('vip_start_date')
            vip_end = result.get('vip_end_date')

            return None, ({'vip_start': vip_start, 'sub_start':sub_start, 'vip_end':vip_end, 'sub_end':sub_end})
        else:
            return response.status_code, None
        

    def save_name(self, message, lang = None):
        if lang == None:
            lang = self.check_user_language(message)
        text = TranslateView.get("incorrect_name", lang)
        if message.text:
            name = message.text
            pattern = r"^\w[\w\s-]{0,49}$"
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
        incorrect_text = TranslateView.get("incorrect_gender", lang)
        if message.text:
            gender = ""
            if message.text != "Пропустить" or message.text != "user_pass":
                gender = message.text
                pattern = r"^\w[\w\s-]{0,49}$"
                is_match = re.match(pattern, gender)
                if not is_match:
                    self.bot.send_message(message.chat.id, text=incorrect_text)
                    return False
            status_code, done = self.update_field(message, field="gender", value=gender)
            # if done:
            #     self.bot.send_message(message.chat.id, text = "Данные успешно обновлены!", reply_markup = types.ReplyKeyboardRemove())
                
            return True
        else:
            
            self.bot.send_message(message.chat.id, text = incorrect_text)
            return False


    def save_avatar(self, message, lang = None):
        if message.text == "Пропустить" or message.text == "user_pass":
            return True
        elif message.text is not None:
            self.bot.send_message(message.chat.id, "Пожалуйста, отправьте изображение вашего аватара.")
            return False
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
        pattern = r"^(1[6-9]|[2-9][0-9]|[1-9][0-9]{2}|110)$"
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
            if message.text == "Пропустить" or message.text == "user_pass" or  is_match:
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
                if message.text != "Пропустить" or message.text == "user_pass":
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
        'Авторизация'     :{'callback_data': 'authorization'},
        'Подписка'        :{'callback_data': 'subscription'},
        'Vip статус'      :{'callback_data': 'vip_status'},
        'Язык/Language'     :{'callback_data':'change_language'},
        "Следующая страница"                :{'callback_data':'next_page'}
    }, row_width=1)

    firstpage_authorized_ru = quick_markup({
        'Мои достижения'  :{'callback_data': 'my_achievements'},
        'Изменить данные' :{'callback_data': 'edit_data'},
        'Подписка'        :{'callback_data': 'subscription'},
        'Vip статус'      :{'callback_data': 'vip_status'},
        'Язык/Language'     :{'callback_data':'change_language'},
        'Следующая страница'                :{'callback_data':'next_page'}
    }, row_width=1)

    lastpage_authorized_ru = quick_markup({
        'О проекте'               :{'callback_data': 'about_project'},
        'Пригласить друга'        :{'callback_data': 'invite_friend'},
        'Фестиваль'               :{'callback_data': 'festival'},
        'Путешествия в Тибет'     :{'callback_data': 'tibet_travels'},
        'Twitter'                   :{'url': 'https://twitter.com'},
        'Facebook'                   :{'url': 'https://facebook.com'},
        'Предыдущая страница'                         :{'callback_data': 'previous_page'},
    }, row_width=1, )

    lastpage_unauthorized_ru = quick_markup({
        'О проекте'               :{'callback_data': 'about_project'},
        'Фестиваль'               :{'callback_data': 'festival'},
        'Путешествия в Тибет'     :{'callback_data': 'tibet_travels'},
        'Twitter'                   :{'url': 'https://twitter.com'},
        'Facebook'                   :{'url': 'https://facebook.com'},
        'Предыдущая страница'                         :{'callback_data': 'previous_page'},
    }, row_width=1)

    firstpage_unauthorized_en = quick_markup({
        'Authorization' : {'callback_data': 'authorization'},
        'Subscription' : {'callback_data': 'subscription'},
        'Vip status'    : {'callback_data': 'vip_status'},
        'Language/Язык'     :{'callback_data':'change_language'},
        "Next page"              : {'callback_data':'next_page'}
    }, row_width=1)

    firstpage_authorized_en = quick_markup({
        'My achievements' : {'callback_data': 'my_achievements'},
        'Edit data'      : {'callback_data': 'edit_data'},
        'Subscription'  : {'callback_data': 'subscription'},
        'Vip status'     : {'callback_data': 'vip_status'},
        'Language/Язык'     :{'callback_data':'change_language'},
        "Next page"               : {'callback_data':'next_page'}
    }, row_width=1)

    lastpage_authorized_en = quick_markup({
        'About project'        : {'callback_data': 'about_project'},
        'Invite friend'        : {'callback_data': 'invite_friend'},
        'Festival'             : {'callback_data': 'festival'},
        'Travels to Tibet'   : {'callback_data': 'tibet_travels'},
        'Twitter'                : {'url': 'https://twitter.com'},
        'Facebook'               : {'url': 'https://facebook.com'},
        'Previous page'                      : {'callback_data': 'previous_page'},
    }, row_width=1)

    lastpage_unauthorized_en = quick_markup({
        'About project'        : {'callback_data': 'about_project'},
        'Festival'             : {'callback_data': 'festival'},
        'Travels to Tibet'   : {'callback_data': 'tibet_travels'},
        'Twitter'                : {'url': 'https://twitter.com'},
        'Facebook'               : {'url': 'https://facebook.com'},
        'Previous page'                      : {'callback_data': 'previous_page'},
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

    def send_menu(self, message):
        pass
        # raise NotImplementedError
        # lang = self.check_user_language(message=message)
        # text = TranslateView.get("menu", lang)
        # errors, is_authorized = self.user_data.is_user_authorized(message)
        # if errors is None:
        #     self.bot.send_message(message.chat.id, text = text, reply_markup = self.create_keyboard_firstpage(is_authorized, lang))
        # else:
        #     self.bot.send_message(message.chat.id, text = f"Произошла ошибка {errors}, попробуйте позже", reply_markup = types.ReplyKeyboardRemove())
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
        response = self.user_data.check_and_create_user_request(message)
        self.change_user_state(chat_id, True)
        self.bot.clear_step_handler_by_chat_id(chat_id)
        if response.status_code == 200:
            result = response.json()
            if result.get('exists'):
                user_language = self.check_user_language(message=message)
                self.bot.send_message(chat_id, text = TranslateView.get("welcome_back_text", user_language))

        elif response.status_code == 201:
            user_language = message.from_user.language_code
            self.user_data.set_user_language(message=message, lang = user_language)
            self.user_language_cache[message.chat.id] = user_language
            self.bot.send_message(chat_id, TranslateView.get("welcome_text", user_language))

            # self.send_menu(message)
        else:
            self.bot.send_message(chat_id, f"Error {response.status_code} occurred while checking user existence.")
            print(response.json())
            return
        
        self.send_menu(message)

    def send_menu(self, message):
        chat_id = message.chat.id
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        ru_button = types.KeyboardButton("Русский")
        en_button = types.KeyboardButton("English")
        keyboard.add(ru_button, en_button)
        self.bot.register_next_step_handler(message, self.choose_language)
        self.bot.send_message(chat_id, "Выбери язык/Choose a language", reply_markup=keyboard)

    def choose_language(self, message):
        chat_id = message.chat.id
        lang = ""
        if message.text:
            text = message.text
            if text == "Русский":
                self.set_user_language(message=message, lang='ru')
                self.change_user_state(chat_id, False)
                lang = "ru"

            elif text == 'English':
                self.set_user_language(message=message, lang='en')
                self.change_user_state(chat_id, False)
                lang = "en"

            self.bot.send_message(chat_id, TranslateView.get('change_language', lang), reply_markup = types.ReplyKeyboardRemove())
            self.bot.send_message(chat_id, TranslateView.get('about_project', lang))


            self.send_subscribe_menu(message)
            return
        self.bot.register_next_step_handler(message, self.choose_language)
        self.bot.send_message(chat_id, "Выбери язык/Choose a language") 

    def send_subscribe_menu(self, message):
        err, subscription = self.user_data.check_user_subscription(message)
        lang = self.user_data.check_user_language(message)
        chat_id = message.chat.id
        if not err:
            keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            yes_button = types.KeyboardButton(TranslateView.get("user_yes", lang))
            no_button = types.KeyboardButton(TranslateView.get("user_no", lang))
            promo_button = types.KeyboardButton(TranslateView.get("user_have_promo", lang))
            keyboard.add(yes_button, no_button, promo_button)
            if not subscription:               
                self.bot.send_message(chat_id, text=TranslateView.get("havenot_subscribe", lang), reply_markup = keyboard)
            else:
                date_string = subscription['sub_end']
                sub_end_date = datetime.strptime(date_string, '%Y-%m-%d').date()
                today = date.today()
                difference = (sub_end_date - today).days
                if difference>0:
                    text = TranslateView.get("subscribe_active_days", lang)
                    text = text.replace('\\n', '\n')
                    text = text.replace("{difference}", str(difference))
                    self.bot.send_message(chat_id, text=text, reply_markup = keyboard)
                elif difference<0:
                    text = TranslateView.get("subscribe_expired_date", lang)
                    text = text.replace('\\n', '\n')
                    text = text.replace("{sub_end_date}", date_string)
                    self.bot.send_message(chat_id, text=text, reply_markup = keyboard)
                else:
                    text = TranslateView.get("subscribe_expire_today", lang)
                    text = text.replace('\\n', '\n')
                    self.bot.send_message(chat_id, text=text, reply_markup = keyboard)
            self.bot.register_next_step_handler(message, self.user_choise)
        else:
            self.bot.send_message(chat_id, text="Ошибка. Попробуйте позже")

    def user_choise(self, message):       
        if message.text:
            item = message.text
            chat_id = message.chat.id
            lang = self.check_user_language(message)
            match item:
                case "Yes":
                    self.bot.send_message(chat_id, text="<---Оплата подписки-->", reply_markup = types.ReplyKeyboardRemove())
                    self.change_user_state(chat_id, False)
                    return
                case "Да":
                    self.bot.send_message(chat_id, text="<---Оплата подписки-->", reply_markup = types.ReplyKeyboardRemove())
                    self.change_user_state(chat_id, False)
                    return
                case "No":
                    self.bot.send_message(chat_id, text="Ok", reply_markup = types.ReplyKeyboardRemove())
                    self.change_user_state(chat_id, False)
                    return               
                case "Нет":
                    self.bot.send_message(chat_id, text="Ok", reply_markup = types.ReplyKeyboardRemove())
                    self.change_user_state(chat_id, False)
                    return
                case "I have a promo code":
                    back_button = types.KeyboardButton(TranslateView.get("user_back", lang))
                    keyboard.add(back_button)
                    self.bot.send_message(chat_id, text=TranslateView.get('enter_promo', lang), reply_markup = keyboard)
                    self.bot.register_next_step_handler(message, self.promo_activate)
                    return               
                case "У меня есть промокод":
                    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                    back_button = types.KeyboardButton(TranslateView.get("user_back", lang))
                    keyboard.add(back_button)
                    self.bot.send_message(chat_id, text=TranslateView.get('enter_promo', lang), reply_markup = keyboard)
                    self.bot.register_next_step_handler(message, self.promo_activate)

                    return
                case _:
                    text = TranslateView.get("choose_one", lang)
                    self.bot.send_message(chat_id, text=text)
                    self.bot.register_next_step_handler(message, self.user_choise)
                    return

    def promo_activate(self, message):
        if message.text:
            chat_id = message.chat.id
            lang = self.check_user_language(message)

            if message.text == TranslateView.get("user_back", lang):
                self.send_subscribe_menu(message)
                return
            
            code = message.text
            status_code = self.user_data.check_promo(message)

            if status_code == 200:
                err, subscription = self.user_data.extend_subscription(message, code)
                if err is None:
                    # print(subscription)
                    # date_string = subscription['sub_end']
                    # sub_end_date = datetime.strptime(date_string, '%Y-%m-%d').date()
                    # today = date.today()
                    # difference = (sub_end_date - today).days

                    # text = TranslateView.get("subscribe_active_days", lang)
                    # text = text.replace('\\n', '\n')
                    # text = text.replace("{difference}", str(difference))
                    # self.bot.send_message(chat_id, text=text)

                    self.bot.send_message(chat_id, text = TranslateView.get("promo_activated", lang))
                else:
                    self.bot.send_message(chat_id, text = TranslateView.get("error_occurred", lang))
            elif status_code == 302:
                self.bot.send_message(chat_id, text = TranslateView.get("promo_unactive", lang))
                self.send_subscribe_menu(message)
            elif status_code == 404:
                self.bot.send_message(chat_id, text = TranslateView.get("promo_notfound", lang))
                self.send_subscribe_menu(message)
            else:
                self.bot.send_message(chat_id, text = TranslateView.get("error_occurred", lang))

            self.change_user_state(chat_id, False)          
class AdminBroadcastVipCommandHandler(CommandHandler):

    @staticmethod
    def info():
        """Returns routing information for the start command"""
        return ("command", {"commands": ["broadcast_vip"]})

    def main(self, message):
        """Function to handle the /start command"""
        chat_id = message.from_user.id
        errors, is_admin = self.user_data.is_user_admin(message=message, telegram_id=message.chat.id)
        if (errors is None) and is_admin:
            lang = self.check_user_language(message)
            text = TranslateView.get("broadcast", lang)
            self.bot.register_next_step_handler(message, self.broadcast)
            self.change_user_state(chat_id, True)
            self.bot.send_message(chat_id, text)
    def broadcast(self, message):
        errors, telegram_ids = self.user_data.get_all_users_id(message=message, vip=True)

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
    def __init__(self, env, bot, db):
        super().__init__(env, bot, db)
        self.main = self.bot.message_handler(func=lambda message: message.text == '/change_language')(self.main)

    @staticmethod
    def info():
        """Returns routing information for the start command"""
        return ("callback_data", {"data": ["change_language"]})

    def main(self, call):
        if isinstance(call, types.CallbackQuery):
            message = call.message
            self.bot.answer_callback_query(call.id)
        else:
            message = call

        self.send_menu(message)

    def send_menu(self, message):
        chat_id = message.chat.id
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        ru_button = types.KeyboardButton("Русский")
        en_button = types.KeyboardButton("English")
        keyboard.add(ru_button, en_button)
        self.bot.clear_step_handler_by_chat_id(chat_id)
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
    def __init__(self, env, bot, db):
        super().__init__(env, bot, db)
        self.main = self.bot.message_handler(func=lambda message: message.text == '/authorization')(self.main)

    @staticmethod
    def info():
        """Returns routing information for the authorization command"""
        return ("callback_data", {"data": ["authorization"]})

    def main(self, call):
        chat_id = None
        if isinstance(call, types.CallbackQuery):
            self.bot.answer_callback_query(call.id)
            message = call.message
            chat_id = message.chat.id
        else:
            message = call
            chat_id = message.chat.id
        self.bot.clear_step_handler_by_chat_id(chat_id)
        self.request_name(message)
        self.change_user_state(chat_id, True)
        


    def request_name(self, message):
        lang = self.check_user_language(message)
        chat_id = message.chat.id
        self.bot.send_message(chat_id, text=TranslateView.get('send_name', lang))
        self.bot.register_next_step_handler(message, self.request_gender)

    def request_gender(self, message):
        if self.user_data.save_name(message):
            lang = self.check_user_language(message)
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            male_button = types.KeyboardButton(TranslateView.get('user_male', lang))
            female_button = types.KeyboardButton(TranslateView.get('user_female', lang))
            helicopter_button = types.KeyboardButton(TranslateView.get('user_other', lang))
            pass_button = types.KeyboardButton(TranslateView.get('user_pass', lang))
            keyboard.add(male_button, female_button, helicopter_button, pass_button)
            self.bot.send_message(message.chat.id, "Теперь выбери пол или укажи свой", reply_markup=keyboard)
            self.bot.register_next_step_handler(message, self.request_avatar)
        else:
            self.bot.register_next_step_handler(message, self.request_gender)

    def request_avatar(self, message):
        lang = self.check_user_language(message)
        if self.user_data.save_gender(message):
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            pass_button = types.KeyboardButton("Пропустить")
            keyboard.add(pass_button)
            self.bot.send_message(message.chat.id, "Пришли мне свой аватар", reply_markup=keyboard)
            self.bot.register_next_step_handler(message, self.request_age)
        else:
            self.bot.register_next_step_handler(message, self.request_avatar)

    def request_age(self, message):
        lang = self.check_user_language(message)
        if self.user_data.save_avatar(message):
            self.bot.register_next_step_handler(message, self.request_email)
            self.bot.send_message(message.chat.id, "Пожалуйста, пришлите ваш возраст.", reply_markup = types.ReplyKeyboardRemove())
        else:
            self.bot.register_next_step_handler(message, self.request_age)

    def request_email(self, message):
        lang = self.check_user_language(message)
        if self.user_data.save_age(message):
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            pass_button = types.KeyboardButton("Пропустить")
            keyboard.add(pass_button)
            self.bot.send_message(message.chat.id, "Пришли мне свой email", reply_markup=keyboard)
            self.bot.register_next_step_handler(message, self.request_country)
        else:
            self.bot.register_next_step_handler(message, self.request_email)

    def request_country(self, message):
        lang = self.check_user_language(message)
        if self.user_data.save_email:
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            pass_button = types.KeyboardButton("Пропустить")
            keyboard.add(pass_button)
            self.bot.send_message(message.chat.id, "Пришли мне свою страну проживания", reply_markup=keyboard)
            self.bot.register_next_step_handler(message, self.cancel_registration)
        else:
            self.bot.register_next_step_handler(message, self.request_country)
    
    def cancel_registration(self, message):
        lang = self.check_user_language(message)
        if self.user_data.save_country:
            self.bot.send_message(message.chat.id, "Успешная регистрация!", reply_markup=types.ReplyKeyboardRemove())
            self.user_data.set_user_authorized(message)
            self.change_user_state(message.chat.id)
            self.send_menu(message)
        else:
            self.bot.register_next_step_handler(message, self.cancel_registration)
class MyAchievementsCommandHandler(CommandHandler):

    def __init__(self, env, bot, db):
        super().__init__(env, bot, db)
        self.main = self.bot.message_handler(func=lambda message: message.text == '/my_achievements')(self.main)

    @staticmethod
    def info():
        """Returns routing information for the 'My Achievements' command"""
        return ("callback_data", {"data": ["my_achievements"]})
    def main(self, call):
        chat_id = None
        if isinstance(call, types.CallbackQuery):
            chat_id = call.message.chat.id
            self.bot.answer_callback_query(call.id)
        else:
            chat_id = call.chat.id

        self.bot.clear_step_handler_by_chat_id(chat_id)
        self.bot.send_message(chat_id, text="Вы нажали кнопку 'Мои достижения'.")
class EditDataCommandHandler(CommandHandler):
    def __init__(self, env, bot, db):
        super().__init__(env, bot, db)
        self.main = self.bot.message_handler(func=lambda message: message.text == '/edit_data')(self.main)

    @staticmethod
    def info():
        """Returns routing information for the 'Edit Data' command"""
        return ("callback_data", {"data": ["edit_data"]})
    def main(self, call):
        chat_id = None
        if isinstance(call, types.CallbackQuery):
            message = call.message
            chat_id = message.chat.id     
            self.bot.answer_callback_query(call.id)

        else:
            message = call
            chat_id = message.chat.id
        lang = self.check_user_language(message)
        self.bot.clear_step_handler_by_chat_id(chat_id)   
        self.change_user_state(chat_id, True)
        text = TranslateView.get("ask_changes", language=lang)
        self.bot.send_message(chat_id, text=text)
        keyboard = types.ReplyKeyboardMarkup(row_width=6, resize_keyboard=True)
        buttons = []
        for i in range(1,7):
            buttons.append(types.KeyboardButton(str(i)))
        keyboard.add(*buttons)
        text = TranslateView.get("list_changes", language=lang)
        text = text.replace('\\n', '\n')
        self.bot.send_message(chat_id, text=text , reply_markup = keyboard)
        self.bot.register_next_step_handler(message, self.choise_items)
 

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
                    male_text = TranslateView.get("user_male", lang)
                    female_text = TranslateView.get("user_female", lang)
                    pass_text = TranslateView.get("user_pass", lang)
                    male_button = types.KeyboardButton(male_text)
                    female_button = types.KeyboardButton(female_text)
                    helicopter_button = types.KeyboardButton(TranslateView.get('user_other', lang))
                    pass_button = types.KeyboardButton(pass_text)
                    keyboard.add(male_button, female_button,helicopter_button, pass_button)
                    text = TranslateView.get("choose_gender", lang)
                    self.bot.send_message(message.chat.id, text=text, reply_markup = keyboard)
                    self.bot.register_next_step_handler(message, self.handle_gender_edit)
                case "3":
                    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                    pass_text = TranslateView.get("user_pass", lang)
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
                    pass_text = TranslateView.get("user_pass", lang)
                    pass_button = types.KeyboardButton(pass_text)
                    keyboard.add(pass_button)
                    text = TranslateView.get("send_email", lang)
                    self.bot.send_message(message.chat.id, text=text, reply_markup = keyboard)
                    self.bot.register_next_step_handler(message, self.handle_email_edit)
                case "6":
                    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                    pass_text = TranslateView.get("user_pass", lang)
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
    def __init__(self, env, bot, db):
        super().__init__(env, bot, db)
        self.main = self.bot.message_handler(func=lambda message: message.text == '/subscription')(self.main)
    
    @staticmethod
    def info():
        """Returns routing information for the 'Subscription' command"""
        return ("callback_data", {"data": ["subscription"]})

    def main(self, call):
        if isinstance(call, types.CallbackQuery):
            message = call.message
            chat_id = message.chat.id
            self.bot.answer_callback_query(call.id)
        else:
            message = call
            chat_id = message.chat.id
        self.bot.clear_step_handler_by_chat_id(chat_id)
    
    # def send_menu(self, message):
    #     err, subscription = self.user_data.check_user_subscription(message)
    #     lang = self.user_data.check_user_language(message)
    #     chat_id = message.chat.id
    #     if not err:
    #         self.user_states[chat_id] = True
    #         if not subscription:               
    #             keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    #             yes_button = types.KeyboardButton(TranslateView.get("user_yes", lang))
    #             no_button = types.KeyboardButton(TranslateView.get("user_no", lang))
    #             promo_button = types.KeyboardButton(TranslateView.get("user_have_promo", lang))
    #             keyboard.add(yes_button, no_button, promo_button)
    #             self.bot.send_message(chat_id, text=TranslateView.get("havenot_subscribe", lang), reply_markup = keyboard)
    #         else:
    #             date_string = subscription['sub_end']
    #             sub_end_date = datetime.strptime(date_string, '%Y-%m-%d').date()
    #             today = date.today()
    #             difference = (sub_end_date - today).days
    #             if difference>0:
    #                 text = TranslateView.get("subscribe_active_days", lang)
    #                 text = text.replace('\\n', '\n')
    #                 text = text.replace("{difference}", str(difference))
    #                 self.bot.send_message(chat_id, text=text)
    #             elif difference<0:
    #                 text = TranslateView.get("subscribe_expired_date", lang)
    #                 text = text.replace('\\n', '\n')
    #                 text = text.replace("{sub_end_date}", date_string)
    #                 self.bot.send_message(chat_id, text=text)
    #             else:
    #                 text = TranslateView.get("subscribe_expire_today", lang)
    #                 text = text.replace('\\n', '\n')
    #                 self.bot.send_message(chat_id, text=text)
    #         self.bot.register_next_step_handler(message, self.user_choise)
    #     else:
    #         self.bot.send_message(chat_id, text="Ошибка. Попробуйте позже")

    # def user_choise(self, message):       
    #     if message.text:
    #         item = message.text
    #         chat_id = message.chat.id
    #         lang = self.check_user_language(message)
    #         match item:
    #             case TranslateView.get("user_yes", lang):
    #                 self.bot.send_message(chat_id, text="<---Оплата подписки-->", reply_markup = types.ReplyKeyboardRemove())
    #                 self.change_user_state(chat_id, True)
    #                 return
    #             case TranslateView.get("user_no", lang):
    #                 self.bot.send_message(chat_id, text="Ok", reply_markup = types.ReplyKeyboardRemove())
    #                 self.change_user_state(chat_id, True)
    #                 return
    #             case TranslateView.get("user_have_promo", lang):
    #                 keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    #                 back_button = types.KeyboardButton(TranslateView.get("user_back", lang))
    #                 keyboard.add(back_button)

    #                 self.bot.send_message(message.chat.id, text=TranslateView.get("enter_promo"), reply_markup = keyboard)
    #                 self.bot.register_next_step_handler(message, self.promo_activate)
    #                 return
                
    # def promo_activate(self, message):
    #     if message.text:
    #         chat_id = message.chat.id
    #         lang = self.check_user_language(message)

    #         if message.text == TranslateView.get("back", lang):
    #             self.send_menu(message)
    #             return
    #         code = str(self.user_data.check_promo(message))
    #         self.bot.send_message(chat_id, text = code)
    #         self.bot.register_next_step_handler(message, self.promo_activate)


    # def activate_trial(self, message):
    #     chat_id = message.chat.id
    #     if (message.text) and (message.text == "Да" or message.text == "Нет"):
    #         if message.text == "Да":
    #             err, subscription = self.user_data.start_trial_subscription(message)
    #             if err is None:
    #                 self.bot.send_message(chat_id, text=f"Ваша подписка истекает через 30 дней", reply_markup = types.ReplyKeyboardRemove())
    #             else:
    #                 self.bot.send_message(chat_id, text=f"Произошла ошибка. Попробуйте позже", reply_markup = types.ReplyKeyboardRemove())
                    
    #         self.change_user_state(chat_id, False)

    #     else:
    #         self.bot.register_next_step_handler(message, self.activate_trial)
    #         self.bot.send_message(chat_id, text=f"Пожалуйста, выберите вариант ответа")

class VipStatusCommandHandler(CommandHandler):
    def __init__(self, env, bot, db):
        super().__init__(env, bot, db)
        self.main = self.bot.message_handler(func=lambda message: message.text == '/vip_status')(self.main)
       
    @staticmethod
    def info():
        """Returns routing information for the 'Vip Status' command"""
        return ("callback_data", {"data": ["vip_status"]})

    def main(self, call):
        if isinstance(call, types.CallbackQuery):
            chat_id = call.message.chat.id
            self.bot.answer_callback_query(call.id)
        else:
            chat_id = call.chat.id
        self.bot.clear_step_handler_by_chat_id(chat_id)
        self.bot.send_message(chat_id, text="Вы нажали кнопку 'Vip статус'.")
        
class AboutProjectCommandHandler(CommandHandler):
    def __init__(self, env, bot, db):
        super().__init__(env, bot, db)
        self.main = self.bot.message_handler(func=lambda message: message.text == '/about_project')(self.main)
     
    @staticmethod
    def info():
        """Returns routing information for the 'About Project' command"""
        return ("callback_data", {"data": ["about_project"]})

    def main(self, call):
        if isinstance(call, types.CallbackQuery):
            chat_id = call.message.chat.id
            self.bot.answer_callback_query(call.id)
        else:
            chat_id = call.chat.id
        self.bot.clear_step_handler_by_chat_id(chat_id)
        self.bot.send_message(chat_id, text="Вы нажали кнопку 'О проекте'.")
        
class InviteFriendCommandHandler(CommandHandler):
    def __init__(self, env, bot, db):
        super().__init__(env, bot, db)
        self.main = self.bot.message_handler(func=lambda message: message.text == '/invite_friend')(self.main)
    
    @staticmethod
    def info():
        """Returns routing information for the 'Invite Friend' command"""
        return ("callback_data", {"data": ["invite_friend"]})

    def main(self, call):
        if isinstance(call, types.CallbackQuery):
            message = call.message
            chat_id = message.chat.id
            
            self.bot.answer_callback_query(call.id)
        else:
            message = call
            chat_id = message.chat.id
        errors, link = self.user_data.get_user_invitation_link(message)
        if not errors:
            self.bot.send_message(chat_id, text=f"Ваша пригласительная ссылка :\n{link}")
        self.bot.clear_step_handler_by_chat_id(chat_id)
class FestivalCommandHandler(CommandHandler):
    def __init__(self, env, bot, db):
        super().__init__(env, bot, db)
        self.main = self.bot.message_handler(func=lambda message: message.text == '/festival')(self.main)
     
    @staticmethod
    def info():
        """Returns routing information for the 'Festival' command"""
        return ("callback_data", {"data": ["festival"]})

    def main(self, call):
        if isinstance(call, types.CallbackQuery):
            chat_id = call.message.chat.id
            self.bot.answer_callback_query(call.id)
        else:
            chat_id = call.chat.id
        self.bot.clear_step_handler_by_chat_id(chat_id)
        self.bot.send_message(chat_id, text="Вы нажали кнопку 'Фестиваль'.")
        
class TibetTravelsCommandHandler(CommandHandler):
    def __init__(self, env, bot, db):
        super().__init__(env, bot, db)
        self.main = self.bot.message_handler(func=lambda message: message.text == '/tibet_travels')(self.main)
     
    @staticmethod
    def info():
        """Returns routing information for the 'Tibet Travels' command"""
        return ("callback_data", {"data": ["tibet_travels"]})

    def main(self, call):
        if isinstance(call, types.CallbackQuery):
            chat_id = call.message.chat.id
            self.bot.answer_callback_query(call.id)
        else:
            chat_id = call.chat.id
        self.bot.clear_step_handler_by_chat_id(chat_id)
        self.bot.send_message(chat_id, text="Вы нажали кнопку 'Путешествия в Тибет'.")
        