# django.setup() 依存先環境変数値の設定. 
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'KGAvengers.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'KGAvengers.settings')
# Django アプリケーションを初期化しロード
import django
django.setup()
import unittest

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

import requests
import json
import random
from random import randint, choice
# from drop_and_create_db import random_dow, random_dt, insert_routine_routines, insert_routine_tasks, insert_routine_task_records, insert_routine_task_comments
from routine.models import *
from datetime import timedelta

def drop_all_tables():
    ''' 全テーブルを削除 '''
    with connection.cursor() as cursor:
        cursor.execute('DROP SCHEMA public CASCADE')
        cursor.execute('CREATE SCHEMA public')
def create_all_tables():
    ''' 全テーブルを作成 '''
    call_command('makemigrations')
    call_command('migrate')

def random_dow():
    original_list = [f'{i}' for i in range(6)]
    num_elements_to_pick = random.randint(1, 6)
    random_elements = random.sample(original_list, num_elements_to_pick)
    return random_elements
def dow_to_string(dow):
    mapping = {
        '0': 'mon',
        '1': 'tue',
        '2': 'wed',
        '3': 'thu',
        '4': 'fri',
        '5': 'sat',
        '6': 'sun'
    }
    return mapping.get(str(dow), None)
def random_dt():
    current_datetime = timezone.now()
    n = 2
    n_week_ago = current_datetime - timedelta(weeks=n)
    random_timedelta = random.uniform(0, (current_datetime - n_week_ago).total_seconds())
    random_datetime = n_week_ago + timedelta(seconds=random_timedelta)
    return random_datetime
def insert_supply_auth_users(users: list[dict]):
    default_tags_value = []  # This could be an empty list, a list of tag ids, or another appropriate default value
    instance = [User(username=user['username'], email=user['email'], tag_ids=user.get('tag_ids', default_tags_value)) for user in users]
    User.objects.bulk_create(instance)  
    return
def insert_routine_routines(routines: list[dict]):
    user = User.objects.get(id=1)
    routine_list = []
    for routine in routines:
        instance = Routine.objects.create(
            user_id=user,
            dow=routine['dow'], 
            start_time='000000+0900', 
            end_time='010000+0900',
            title=routine['title'],
            subtitle='a',
            icon='🥺',
            is_published=choice([True, False]),
            is_notified=choice([True, False]),
            interest_ids=[randint(0, 5)]
        )

        consecutive_days = instance.calculate_consecutive_days()

        
        # Include the ID and additional keys in the returned dictionary
        routine_with_id = routine.copy()
        routine_with_id['id'] = instance.id
        routine_with_id['start_time'] = instance.start_time
        routine_with_id['end_time'] = instance.end_time
        routine_with_id['subtitle'] = instance.subtitle
        routine_with_id['is_published'] = instance.is_published
        routine_with_id['is_notified'] = instance.is_notified
        routine_with_id['is_real_time'] = instance.is_real_time
        routine_with_id['consecutive_days'] = consecutive_days
        

        routine_list.append(routine_with_id)

    # print(routine_list)
    return routine_list
def insert_routine_tasks(tasks: list[dict]):
    task_list = []
    for task in tasks:
        instance = Task.objects.create(
            routine_id=Routine.objects.get(id=task["routine_id"]),
            title=task['title'],
            detail='a',
            icon='🥹',
            required_time=random.randint(0, 100),
            is_notified=True
        )
        
        # Include the ID and additional keys in the returned dictionary
        task_with_id = task.copy()
        task_with_id['id'] = instance.id
        task_with_id['detail'] = instance.detail
        task_with_id['icon'] = instance.icon
        task_with_id['required_time'] = instance.required_time
        task_with_id['is_notified'] = instance.is_notified

        task_list.append(task_with_id)

    return task_list
def insert_routine_task_finishes(task_records: list[dict]):
    routine_qs = RoutineFinish.objects.all()
    if not routine_qs.exists():
        print("No RoutineFinish instances available.")
        return

    routine_instance = routine_qs[0]  # Or some other logic to select the right instance

    instances = [TaskFinish(
                     task_id=Task.objects.get(id=tr['task_id']),
                     is_achieved=True,
                     done_time=random.randint(0, 100),
                     when=tr['when'],
                     routine_finish_id=routine_instance
                 ) for tr in task_records]
    
    TaskFinish.objects.bulk_create(instances)
    return

class APITestCase(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        users = [{'username': chr(i), 'email': chr(i)} for i in range(ord('a'), ord('z') + 1)]
        drop_all_tables()                   #! 取扱注意
        create_all_tables()
        insert_supply_auth_users(users)
        # Initialize an empty expected_routines dictionary
        self.expected_routines = {
            'mon': [],
            'tue': [],
            'wed': [],
            'thu': [],
            'fri': [],
            'sat': [],
            'sun': [],
            'routines': {}
        }
        
        # Create and insert routines and update the expected_routines dictionary
        self.routines_data = insert_routine_routines([
            {'dow': [random.choice(range(7))], 'title': f'{i}'} for i in range(3)
        ])
        
        # Sort routines by the first dow element and then by start_time
        self.routines_data = sorted(self.routines_data, key=lambda x: (x['dow'][0], x['start_time']))
        
        for routine in self.routines_data:
            routine_id = str(routine.get('id', None))
            for dow in routine['dow']:
                string_dow = dow_to_string(dow)
                if string_dow:
                    self.expected_routines[string_dow].append(str(routine['id']))

        
            # Initialize the routine_id key with its respective structure
            self.expected_routines['routines'][routine_id] = {
                'start_time': routine['start_time'],
                'end_time': routine['end_time'],
                'title': routine['title'],
                'tag_id': None,  # Add this line 
                'tag_name' : '',
                'real_time' : routine['is_real_time'],
                'consecutive_days' : routine['consecutive_days'],
                'tasks': []  # Initialize tasks list for each routine
            }
            # print("Routines in expected_routines:", self.expected_routines['routines'])
            
        # Create and insert tasks and update the expected_routines dictionary
        self.tasks_data = insert_routine_tasks([
            {'routine_id': random.choice(self.routines_data)['id'], 'title': f'{i + 100}'} for i in range(5)
        ])

        # Create and insert task records into the database
        self.task_records_data = insert_routine_task_finishes([
            {'task_id': random.choice(self.tasks_data)['id'], 'when': random_dt()} for _ in range(5)
        ])

        # print("Final expected_routines contents:", self.expected_routines)

        for task in self.tasks_data:
            routine_id = str(task['routine_id'])  # Assuming routine_id is a key in the task dictionary
            task_id = task['id']
            latest_task_record = TaskFinish.objects.filter(task_id=task_id).order_by('-when').first()
            is_achieved = latest_task_record.is_achieved if latest_task_record else False  # Fetch is_achieved from the latest record if it exists

            task_data = {
                'task_id': task_id,
                'title': task['title'],
                'detail': task['detail'],
                'required_time': task['required_time'],
                'is_achieved': is_achieved,  # Add this line              
            }
            # print(type(self.expected_routines['routines'][routine_id]['tasks']))
            if routine_id in self.expected_routines['routines']:
                self.expected_routines['routines'][routine_id]['tasks'].append(task_data)
            else:
                print(f"Routine ID {routine_id} not found in expected_routines.")   

    def test_read_routine_task(self):
        # 2. API call
        url = 'http://127.0.0.1:8000/routine/routine_task/?week_start=20231106'
        response = requests.get(url)
        
        # 3. Verify results
        self.assertEqual(response.status_code, 200)
        res_data = response.json()

        print("Returned data:\n", res_data['data'])
        print("//////////////////////////")
        print("Expected data:\n", self.expected_routines)


        # Verify the status code
        self.assertEqual(res_data['status_code'], 1)

        # Verify the routines by the day of the week
        for day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
            self.assertEqual(res_data['data'][day], self.expected_routines[day])

        # Verify the detailed routines
        self.assertEqual(res_data['data']['routines'], self.expected_routines['routines'])


if __name__ == "__main__":
    unittest.main(verbosity=2)