from notion_client import Client
import json
import os

class TranslateView:
    __data = []
    __token = None
    __url = None
    __ID = None
    __path = None
    __client = None

    @staticmethod
    def initialize(env):
        TranslateView.__token = env.get("TRANSLATES_TOKEN")
        TranslateView.__ID = env.get("TRANSLATES_ID")
        TranslateView.__path = env.get("TRANSLATES_PATH")
        TranslateView.__url = env.get("TRANSLATES_URL")
        TranslateView.__client = Client(auth=TranslateView.__token)
        TranslateView.update_translations()
    @staticmethod
    def update_translations():
        if not TranslateView.__client:
            return

        # Получаем базу данных (коллекцию) по ее ID
        database = TranslateView.__client.databases.query(database_id=TranslateView.__ID)

        TranslateView.__data = []

        # Получаем записи (строки) из базы данных и преобразуем их в словарь
        for row in database['results']:
            TranslateView.__data.append({
                'key': row['properties']['key']['title'][0]['text']['content'],
                'en': row['properties']['en']['rich_text'][0]['text']['content'],
                'ru': row['properties']['ru']['rich_text'][0]['text']['content']
                # Добавьте другие поля, которые вам нужны
            })

        # Сохраняем загруженные данные в кэш
        with open(TranslateView.__path, 'w', encoding='utf-8') as f:
            json.dump(TranslateView.__data, f, ensure_ascii=False, indent=4)



    @staticmethod
    def get(key, language):
        for row in TranslateView.__data:
            if row['key'] == key:
                return row[language]
        return None
