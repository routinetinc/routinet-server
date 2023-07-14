# django.setup() 依存先環境変数値の設定. 
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'KGAvengers.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'KGAvengers.settings')

# Django アプリケーションを初期化しロード
import django
django.setup()

from django.core.management import call_command
from django.db import connection

# 1. 全テーブルを削除
with connection.cursor() as cursor:
    cursor.execute("DROP SCHEMA public CASCADE")
    cursor.execute("CREATE SCHEMA public")

# 2. 全テーブルを作成
# call_command('makemigrations', 'your_app')
# call_command('migrate', 'your_app')

