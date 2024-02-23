from os import path
from dotenv import load_dotenv
from env import ENV as env
import telebot
DOTENV_PATH = path.join(path.dirname(__file__),'.' , '.env')
load_dotenv(DOTENV_PATH)
print(env.get("BOT_TOKEN"))
bot = telebot.TeleBot(env.get("BOT_TOKEN"))
# Ответ на команду /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот, который отвечает на приветствия.")

# Ответ на сообщение "привет"
@bot.message_handler(func=lambda message: message.text.lower() == 'привет')
def send_hello(message):
    bot.reply_to(message, "Привет! Как дела?")

# Запускаем бота
bot.polling()