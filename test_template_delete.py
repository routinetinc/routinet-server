from django.urls import reverse
import requests

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
from supply_auth.models import User
from routine.models import *
from feed.models import *
import random
from datetime import timedelta
from django.utils import timezone
BLUE = '\033[36m'
END = '\033[0m'

def drop_all_tables():
    ''' 全テーブルを削除 '''
    with connection.cursor() as cursor:
        cursor.execute('DROP SCHEMA public CASCADE')
        cursor.execute('CREATE SCHEMA public')
def create_all_tables():
    ''' 全テーブルを作成 '''
    call_command('makemigrations')
    call_command('migrate')

# 乱数
def random_dow():
    original_list = [f'{i}' for i in range(6)]
    num_elements_to_pick = random.randint(1, 6)
    random_elements = random.sample(original_list, num_elements_to_pick)
    return random_elements
def random_dt():
    current_datetime = timezone.now()
    n = 2
    n_week_ago = current_datetime - timedelta(weeks=n)
    random_timedelta = random.uniform(0, (current_datetime - n_week_ago).total_seconds())
    random_datetime = n_week_ago + timedelta(seconds=random_timedelta)
    return random_datetime

#* インサート関数
def insert_supply_auth_users(users: list[dict]):
    instance = [User(username=user['username'], email=user['email']) for user in users]
    User.objects.bulk_create(instance)  
    return

from django.test import TestCase
import unittest
from routine.models import Routine

class TestRoutineDeletion(unittest.TestCase):

    def setUp(self):
        # Set up the test database environment
        drop_all_tables()
        create_all_tables()
        users = [{'username': f'user{i}', 'email': f'user{i}@example.com'} for i in range(10)]
        insert_supply_auth_users(users)  # Assuming 'users' is defined somewhere

        # Insert a routine for testing deletion
        self.routine_data = {
            "data": {
                "dow": ["0", "1", "2"],       # 月曜を "0" とし連番で定義。
                "start_time": "121212+0900",  # "HHMMSSTZ"
                "end_time": "121212+0900",    # "HHMMSSTZ"
                "title": "foo", 
                "subtitle": "bar",  
                "is_published": True,
                "is_notified": True,
                "icon": "👍",
                "interest_ids":[0,1,2]
            }
        }

        # Call the API to create the routine
        response = requests.post('http://127.0.0.1:8000/routine/routine/', json=self.routine_data)
        print(response)
        self.routine_id_from_api = response.json().get('data', {}).get('routine_id')
        print(self.routine_id_from_api)

    def test_routine_deletion(self):

        json_data = {
            "data": {
                "routine_id": "1"
            }
        }

        # Call the API to delete the routine
        delete_response = requests.delete(f'http://127.0.0.1:8000/routine/routine/', json=json_data)
        
        # Check if the API responded with a success status
        self.assertEqual(delete_response.status_code, 200, f"Delete failed with response: {delete_response.content}")

        # Try to retrieve the deleted routine
        try:
            routine_in_db = Routine.objects.get(id=self.routine_id_from_api)
            self.fail(f"The routine with id {self.routine_id_from_api} was not deleted. Found: {routine_in_db}")
        except Routine.DoesNotExist:
            pass  # This is the expected behavior

    def tearDown(self):
        # Cleanup after tests if necessary
        pass

if __name__ == "__main__":
    unittest.main()
