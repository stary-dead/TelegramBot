"""Bot start file"""
import os
from env import ENV as env
from core import Bot
from functions._translateview import TranslateView


try:
    from db import DB_CONNECTION
except ImportError:
    DB_CONNECTION = None
if __name__ == "__main__":
    TranslateView.initialize(env=env)
    bot = Bot(env=env, db=DB_CONNECTION)
    bot.run()
