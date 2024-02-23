from customTeleBot import YooCartBot
import functions
import middlewares
import sys

class Bot:
    """Bot class"""
    def __init__(self, env, db):
        token = env.get("BOT_TOKEN")

        self.env = env
        self.bot = YooCartBot(token)
        self.db = db

        self.functions = []
        self.middlewares = []

    def run(self):
        """run the bot"""
        self._register_actions()
        self._register_middlewares()
        self.bot.polling()

    def _discover_middlewares(self):
        for middleware in dir(middlewares):
            if str(middleware).startswith('_'):
                break
            obj = getattr(middlewares, middleware)
            self.middlewares.append(obj)

    def _discover_functions(self):
        for func in dir(functions):
            if str(func).startswith('_'):
                break
            obj = getattr(functions, func)
            self.functions.append(obj)

    def _register_middlewares(self):
        self._discover_middlewares()

        for middleware in self.middlewares:
            self.bot.add_middleware(middleware) 

    def _register_actions(self):
        self._discover_functions()
        for func_handler in self.functions:
            routing_info = func_handler.info()

            trigger_info = routing_info[0]
            handler_info = routing_info[1]
            if trigger_info == "command":  # Проверяем, если это команда
                for command in handler_info['commands']:
                    m_handler = self.bot.message_handler(commands=[command])
                    m_handler(func_handler.init(env=self.env, bot=self.bot, db=self.db))          
            elif trigger_info == "callback_data":  # Проверяем, если это callback_data
                for callback_data in handler_info['data']:
                    c_handler = self.bot.callback_query_handler(func=lambda call: call.data == callback_data)
                    c_handler(func_handler.init(env=self.env, bot=self.bot, db=self.db))


    
    