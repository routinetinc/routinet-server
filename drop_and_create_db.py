# django.setup() 依存先環境変数値の設定. 
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'KGAvengers.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'KGAvengers.settings')
# Django アプリケーションを初期化しロード
import django
django.setup()


#* ------------------------------------------------------------------- *#

from django.core.management import call_command
from django.db import connection
from supplyAuth.models import User
from routine.models import *

def drop_all_tables():
    """ 全テーブルを削除 """
    with connection.cursor() as cursor:
        cursor.execute("DROP SCHEMA public CASCADE")
        cursor.execute("CREATE SCHEMA public")
def create_all_tables():
    """ 全テーブルを作成 """
    call_command('makemigrations')
    call_command('migrate')

#* インサート関数
def insert_supplyAuth_users(users: list[dict]):
    instance = [User(username=user['username'], email=user['email']) for user in users]
    User.objects.bulk_create(instance)  
    return
def insert_routine_interests(interests: list[dict]):
    instance = [Interest(name=interest['name']) for interest in interests]
    Interest.objects.bulk_create(instance)
    return



#* インサートするインスタンスのパラメータを設定
users = [
    {'username': 'a', 'email': 'a'},
    {'username': 'b', 'email': 'b'},
    {'username': 'c', 'email': 'c'}
]

interests = [
    {'name': 'NULL'}
]

if __name__ == '__main__':
    drop_all_tables()                   #! 取扱注意
    create_all_tables()
    insert_supplyAuth_users(users)
    insert_routine_interests(interests)