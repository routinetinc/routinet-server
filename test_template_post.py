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

class TestRoutineCreation(unittest.TestCase):

    def setUp(self):
        # Set up the test database environment
        drop_all_tables()
        create_all_tables()
        users = [{'username': f'user{i}', 'email': f'user{i}@example.com'} for i in range(10)]
        insert_supply_auth_users(users)  # Assuming 'users' is defined somewhere

    def test_routine_creation(self):
        # Data to be sent to the API
        routine_data = {
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
        response = requests.post('http://127.0.0.1:8000/routine/routine/', json=routine_data)

        # Check if the API responded with a success status
        self.assertEqual(response.status_code, 200)

        # Extract the routine ID from the API response
        routine_id_from_api = response.json().get('data', {}).get('routine_id')

        print("routine_id_from_api : ", routine_id_from_api);

        # Query the database to check if the routine exists with the expected attributes
        try:
            routine_in_db = Routine.objects.get(id=routine_id_from_api)
            print("routine_in_db : ", routine_in_db);
            self.assertIsNotNone(routine_in_db)  # Check if the routine exists

            # Extract expected values from routine_data
            expected_dow = routine_data['data']['dow']
            expected_start_time = routine_data['data']['start_time']
            expected_end_time = routine_data['data']['end_time']
            expected_title = routine_data['data']['title']
            expected_subtitle = routine_data['data']['subtitle']
            expected_is_published = routine_data['data']['is_published']
            expected_is_notified = routine_data['data']['is_notified']
            expected_icon = routine_data['data']['icon']
            expected_interest_ids = routine_data['data']['interest_ids']

            # Compare the attributes of routine_in_db with expected values
            self.assertListEqual(routine_in_db.dow, expected_dow, "Routine days of the week don't match!")
            self.assertEqual(routine_in_db.start_time, expected_start_time, "Routine start time doesn't match!")
            self.assertEqual(routine_in_db.end_time, expected_end_time, "Routine end time doesn't match!")
            self.assertEqual(routine_in_db.title, expected_title, "Routine title doesn't match!")
            self.assertEqual(routine_in_db.subtitle, expected_subtitle, "Routine subtitle doesn't match!")
            self.assertEqual(routine_in_db.is_published, expected_is_published, "Routine publication status doesn't match!")
            self.assertEqual(routine_in_db.is_notified, expected_is_notified, "Routine notification status doesn't match!")
            self.assertEqual(routine_in_db.icon, expected_icon, "Routine icon doesn't match!")
            self.assertListEqual(routine_in_db.interest_ids, expected_interest_ids, "Routine interest IDs don't match!")

        except Routine.DoesNotExist:
            self.fail("The routine was not created in the database!")


if __name__ == "__main__":
    unittest.main(verbosity=2)
