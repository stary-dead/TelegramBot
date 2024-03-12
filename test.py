import os
from notion_client import Client

notion = Client(auth="secret_cHpcUjLXoQcn6asmesmQCLY77jGCHAth3pq69sSPAfm")

# Получение страницы по ID
print(notion.databases.list())

# Теперь вы можете работать с этой страницей
