from typing import List
import telebot

class YooCartBot(telebot.TeleBot):
    """Custom TeleBot Class"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.middlewares = []

    def add_middleware(self, middleware):
        self.middlewares.append(middleware)

    ## OVERRIDE ##
    def _notify_command_handlers(self, handlers, new_messages, updates=None):
        for message in new_messages:
            # first, every message is processed by all the middlewares
            for middleware in self.middlewares:
                message = middleware.init(message)
            for message_handler in handlers:
                if self._test_message_handler(message_handler, message):
                    self._exec_task(message_handler['function'], message)
                    break