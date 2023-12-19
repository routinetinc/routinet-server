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
import string
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
    instance = [User(username=user['username'], email=user['email'], tag_ids=user.get('tag_ids', [0])) for user in users]
    User.objects.bulk_create(instance)  
    return
def insert_routine_interests(interests: list[dict]):
    instance = [Interest(name=interest['name']) for interest in interests]
    Interest.objects.bulk_create(instance)
    return

def insert_routine_tags(tags: list[dict]):
    instances = [
        Tag(
            name=tag.get('name', None),  # Inserts NULL if 'name' is not provided
            detail=tag.get('detail', None)  # Inserts NULL if 'detail' is not provided
        )
        for tag in tags
    ]
    Tag.objects.bulk_create(instances)
    return
def insert_routine_routines(routines: list[dict]):
    user = User.objects.get(id=1)
    default_tag = Tag.objects.first()  
    instance = [
        Routine(
            user_id=user,
            dow=routine['dow'], 
            start_time='000000+0900', 
            end_time='010000+0900',
            title=routine['title'],
            subtitle='a',
            icon='🥺',
            is_published=random.choice([True, False]),
            is_notified=random.choice([True, False]),
            interest_ids = [random.randint(0,5)],
            tag_id=default_tag 

        )
    for routine in routines]
    Routine.objects.bulk_create(instance)
    return
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
def insert_routine_finishes(routine_finishes: list[dict]):
    instances = [
        RoutineFinish(
            routine_id=Routine.objects.get(id=rf['routine_id']),
            is_achieved=rf.get('is_achieved', True),
            icon=rf.get('icon', ''),
            memo=rf.get('memo', ''),
            done_time=rf.get('done_time', 0),
            when=rf.get('when', timezone.now()),
            like_num=rf.get('like_num', 0)
        )
        for rf in routine_finishes
    ]
    RoutineFinish.objects.bulk_create(instances)
def insert_routine_task_finishes(task_records: list[dict]):
    default_routine_finish = RoutineFinish.objects.first()

    instances = [
        TaskFinish(
            task_id=Task.objects.get(id=tr['task_id']),
            routine_finish_id=default_routine_finish,
            is_achieved=random.choice([True, False]),
            done_time=random.randint(0, 100),
            when=tr['when']
        ) for tr in task_records
    ]

    TaskFinish.objects.bulk_create(instances)
    return
def insert_diaries(diaries: list[dict]):
    instances = [
        Diary(
            when=diary['when'],
            user_id=User.objects.get(id=diary['user_id']),
            comment=diary.get('comment', ''),
            icon=diary.get('icon', '')
        )
        for diary in diaries
    ]
    Diary.objects.bulk_create(instances)
    return
def insert_routine_finish_comments(routine_finish_comments: list[dict]):
    instances = [
        RoutineFinishComment(
            routine_finish_id=RoutineFinish.objects.get(id=comment['routine_finish_id']),
            post_time=timezone.now(),
            like_num=random.randint(0, 100),
            comment=f'Sample comment {i}'
        ) for i, comment in enumerate(routine_finish_comments)
    ]
    RoutineFinishComment.objects.bulk_create(instances)
def insert_feed_feed_posts() -> None:
    user = User.objects.get(id=1)  
    instance = [FeedPost(like_num=1, post_time="2023-09-24", interest_ids=[1], user_id=user) for _ in range(10)]
    FeedPost.objects.bulk_create(instance)
    return

#* インサートするインスタンスのパラメータを設定
users = [{'username': chr(i), 'email': chr(i)} for i in range(ord('a'), ord('z') + 1)]
interests = [{'name': 'NULL'}]
tags = [{'name' : 'NULL', 'detail': 'NULL'}]
routines = [{'dow': random_dow(), 'title': f'{i}'} for i in range(5)]
tasks = [{'routine_id': random.randint(1, len(routines)), 'title': f'{i + 100}'} for i in range(20)]
routine_finishes = [{'routine_id': random.randint(1, len(routines))} for _ in range(50)]
task_finishes = [{'task_id': random.randint(1, len(tasks)), 'when': random_dt()} for _ in range(60)]
diaries_data = [{'user_id': random.randint(1, len(users)), 'when': random_dt(),'comment': f'Sample diary entry {i}'} for i in range(10)] 
routine_finish_comments = [{'routine_finish_id': random.randint(1, len(routine_finishes))} for _ in range(20)]  

#* 実行
if __name__ == '__main__':
    drop_all_tables()                   #! 取扱注意
    create_all_tables()
    insert_supply_auth_users(users)
    insert_routine_interests(interests)
    insert_routine_tags(tags)
    insert_routine_routines(routines)
    insert_routine_tasks(tasks)
    insert_routine_finishes(routine_finishes)
    insert_routine_task_finishes(task_finishes)
    insert_diaries(diaries_data)
    insert_routine_finish_comments(routine_finish_comments)
    insert_feed_feed_posts()
    print(f"{BLUE}Successfully completed.{END}")