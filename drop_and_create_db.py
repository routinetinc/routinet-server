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
from routine.utils.time_format_conversion import trans_datetime_iso
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

#* 恣意的な数にならないように調整するための関数
def random_dow():
    original_list = [f'{i}' for i in range(6)]
    num_elements_to_pick = random.randint(1, 6)  # 修正
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
def insert_supplyAuth_users(users: list[dict]):
    instance = [User(username=user['username'], email=user['email']) for user in users]
    User.objects.bulk_create(instance)  
    return
def insert_routine_interests(interests: list[dict]):
    instance = [Interest(name=interest['name']) for interest in interests]
    Interest.objects.bulk_create(instance)
    return
def insert_routine_routines(routines: list[dict]):
    user = User.objects.get(id=1)
    for routine in routines:
        instance = Routine.objects.create(
            user_id=user,
            dow=routine['dow'], 
            start_time='000000+0900', 
            end_time='010000+0900',
            title=routine['title'],
            subtitle='a',
            icon='🥺',
            is_published=random.choice([True, False]),
            is_notified=random.choice([True, False])
        )
        interests = Interest.objects.all()  # すべてのインタレストを取得するか、適切な方法でインタレストを指定する
        instance.interest_id.set(interests)
def insert_routine_tasks(tasks: list[dict]):
    instance = [Task(routine_id=Routine.objects.get(id=task["routine_id"]),
                     title=task['title'],
                     detail='a',
                     icon='🥹',
                     required_time=random.randint(0, 100),
                     is_notified=True)
                for task in tasks]
    Task.objects.bulk_create(instance)
    return
def insert_routine_task_records(task_records: list[dict]):
    instance = [TaskRecord(task_id=Task.objects.get(id=tr['task_id']),
                          is_achieved=random.choice([True, False]),
                          done_time=random.randint(0, 100),
                          when=tr['when'])
                for tr in task_records]
    TaskRecord.objects.bulk_create(instance)
    return
def insert_routine_task_comments(task_comments: list[dict]):
    instance = [TaskComment(task_record_id=TaskRecord.objects.get(id=tc['task_record_id']),
                            comment='a')
                for tc in task_comments]
    TaskComment.objects.bulk_create(instance)
    return

#* インサートするインスタンスのパラメータを設定
users = [{'username': chr(i), 'email': chr(i)} for i in range(ord('a'), ord('z') + 1)]
interests = [{'name': 'NULL'}]
routines = [{'dow': random_dow(), 'title': f'{i}'} for i in range(50)]
tasks = [{'routine_id': random.randint(1, len(routines)), 'title': f'{i + 100}'} for i in range(100)]
task_records = [{'task_id': random.randint(1, len(tasks)), 'when': random_dt()} for _ in range(150)]
tasK_comments = [{'task_record_id': random.randint(1, len(task_records))} for _ in range(100)]

#* 実行
if __name__ == '__main__':
    drop_all_tables()                   #! 取扱注意
    create_all_tables()
    insert_supplyAuth_users(users)
    insert_routine_interests(interests)
    insert_routine_routines(routines)
    insert_routine_tasks(tasks)
    insert_routine_task_records(task_records)
    insert_routine_task_comments(tasK_comments)
    print(f"{BLUE}Successfully completed.{END}")