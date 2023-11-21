from django.test import TestCase, RequestFactory, Client
from drop_and_create_db import random_dt, insert_routine_routines, insert_routine_tasks, insert_routine_task_finishes, insert_routine_task_comments
from routine.views_package import timetree
from routine.models import Routine, Task, TaskFinish, Minicomment
from datetime import timedelta
from supply_auth.models import User
import json
import requests
from datetime import datetime
import time

class TimeTreeTests(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.client.login(email='email', password='password')

    # コメントなしtimetreebeforeのテスト
    def test_timetree_before(self):

        u = User(
            username          = 'ヤマダ',
            email             = '1',
            age               = 19,
            job               = '',
            profile_media_id  = 1,
            self_introduction = '',
            is_hot_user       = True,
            is_active         = True,
            tag_ids           = [],
        )
        u.save()
        ui = User.objects.all()
        r = Routine(
            dow          = ['1'],
            user_id_id   = ui[0].id,
            interest_ids = [],
            start_time   = '000000+0900',
            end_time     = '010000+0900',
            title        = '筋トレ',
        )
        r.save()
        ri = Routine.objects.all()
        t1 = Task(
            routine_id=ri[0],
            title='腹筋',
            detail='a',
            icon='🥹',
            required_time=90,
            is_notified=True
        )
        t1.save()
        t2 = Task(
            routine_id=ri[0],
            title='背筋',
            detail='a',
            icon='🥹',
            required_time=100,
            is_notified=False
        )
        t2.save()
        t3 = Task(
            routine_id=ri[0],
            title='腕立て伏せ',
            detail='a',
            icon='🥹',
            required_time=110,
            is_notified=True
        )
        t3.save()

        tf1 = TaskFinish(
            task_id=Task.objects.get(id=(ri[0].id-1)*3+1),
            is_achieved=True,
            done_time=100,
            routine_id=ri[0]
        )
        tf1.save()
        time.sleep(1)
        tf2 = TaskFinish(
            task_id=Task.objects.get(id=(ri[0].id-1)*3+2),
            is_achieved=False,
            done_time=100,
            routine_id=ri[0]
        )
        tf2.save()
        time.sleep(1)
        tf3 = TaskFinish(
            task_id=Task.objects.get(id=(ri[0].id-1)*3+3),
            is_achieved=True,
            done_time=100,
            routine_id=ri[0]
        )
        tf3.save()

        now = datetime.now()
        request = {
            "data": {
                'day':now.strftime("%Y%m%dT%H%M%S%z")+'+0000',
                'routine_id':ri[0].id
            }
        }
        
        response = self.client.post(
            'http://127.0.0.1:8000/routine/timetree/before/get/',
            json.dumps(request),
            content_type="application/json"
        )
        res = response.json()

        tf = TaskFinish.objects.all()
        tfw1 = tf[0].when
        tfw2 = tf[1].when
        tfw3 = tf[2].when

        d1 = now - timedelta(days=1)
        d2 = now - timedelta(days=2)
        d3 = now - timedelta(days=3)
        d4 = now - timedelta(days=4)
        d5 = now - timedelta(days=5)
        d6 = now - timedelta(days=6)

        self.assertEqual(res['data']['data']['timetree']['days'],[{'day': now.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': [{'task_finish_id': f'{(ri[0].id-1)*3+3}', 'finish_time': tfw3.strftime("%Y%m%dT%H%M%S%z"), 'done_time': 100, 'comment': None}, {'task_finish_id': f'{(ri[0].id-1)*3+2}', 'finish_time': tfw2.strftime("%Y%m%dT%H%M%S%z"), 'done_time': 100, 'comment': None}, {'task_finish_id': f'{(ri[0].id-1)*3+1}', 'finish_time': tfw1.strftime("%Y%m%dT%H%M%S%z"), 'done_time': 100, 'comment': None}]}, {'day': d1.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d2.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d3.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d4.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d5.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d6.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}],'error')

    # コメントありtimetreebeforeのテスト
    def test_timetree_before_with_comment(self):

        u = User(
            username          = 'ヤマダ',
            email             = '1',
            age               = 19,
            job               = '',
            profile_media_id  = 1,
            self_introduction = '',
            is_hot_user       = True,
            is_active         = True,
            tag_ids           = [],
        )
        u.save()
        ui = User.objects.all()
        r = Routine(
            dow          = ['1'],
            user_id_id   = ui[0].id,
            interest_ids = [],
            start_time   = '000000+0900',
            end_time     = '010000+0900',
            title        = '筋トレ',
        )
        r.save()
        ri = Routine.objects.all()
        t1 = Task(
            routine_id=ri[0],
            title='腹筋',
            detail='a',
            icon='🥹',
            required_time=90,
            is_notified=True
        )
        t1.save()
        t2 = Task(
            routine_id=ri[0],
            title='背筋',
            detail='a',
            icon='🥹',
            required_time=100,
            is_notified=False
        )
        t2.save()
        t3 = Task(
            routine_id=ri[0],
            title='腕立て伏せ',
            detail='a',
            icon='🥹',
            required_time=110,
            is_notified=True
        )
        t3.save()

        tf1 = TaskFinish(
            task_id=Task.objects.get(id=(ri[0].id-1)*3+1),
            is_achieved=True,
            done_time=100,
            routine_id=ri[0]
        )
        tf1.save()
        time.sleep(1)
        tf2 = TaskFinish(
            task_id=Task.objects.get(id=(ri[0].id-1)*3+2),
            is_achieved=False,
            done_time=100,
            routine_id=ri[0]
        )
        tf2.save()
        time.sleep(1)
        tf3 = TaskFinish(
            task_id=Task.objects.get(id=(ri[0].id-1)*3+3),
            is_achieved=True,
            done_time=100,
            routine_id=ri[0]
        )
        tf3.save()

        c1 = Minicomment(
            task_finish_id=TaskFinish.objects.get(id=(ri[0].id-1)*3+1),
            comment='a'
        )
        c1.save()
        c2 = Minicomment(
            task_finish_id=TaskFinish.objects.get(id=(ri[0].id-1)*3+2),
            comment='b'
        )
        c2.save()
        c3 = Minicomment(
            task_finish_id=TaskFinish.objects.get(id=(ri[0].id-1)*3+3),
            comment='c'
        )
        c3.save()

        now = datetime.now()
        request = {
            "data": {
                'day':now.strftime("%Y%m%dT%H%M%S%z")+'+0000',
                'routine_id':ri[0].id
            }
        }
        
        response = self.client.post(
            'http://127.0.0.1:8000/routine/timetree/before/get/',
            json.dumps(request),
            content_type="application/json"
        )
        res = response.json()

        tf = TaskFinish.objects.all()
        tfw1 = tf[0].when
        tfw2 = tf[1].when
        tfw3 = tf[2].when

        d1 = now - timedelta(days=1)
        d2 = now - timedelta(days=2)
        d3 = now - timedelta(days=3)
        d4 = now - timedelta(days=4)
        d5 = now - timedelta(days=5)
        d6 = now - timedelta(days=6)

        self.assertEqual(res['data']['data']['timetree']['days'],[{'day': now.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': [{'task_finish_id': f'{(ri[0].id-1)*3+3}', 'finish_time': tfw3.strftime("%Y%m%dT%H%M%S%z"), 'done_time': 100, 'comment': 'c'}, {'task_finish_id': f'{(ri[0].id-1)*3+2}', 'finish_time': tfw2.strftime("%Y%m%dT%H%M%S%z"), 'done_time': 100, 'comment': 'b'}, {'task_finish_id': f'{(ri[0].id-1)*3+1}', 'finish_time': tfw1.strftime("%Y%m%dT%H%M%S%z"), 'done_time': 100, 'comment': 'a'}]}, {'day': d1.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d2.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d3.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d4.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d5.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d6.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}],'error')

    # コメントなしtimetreeafterのテスト
    def test_timetree_after(self):
        u = User(
            username          = 'ヤマダ',
            email             = '1',
            age               = 19,
            job               = '',
            profile_media_id  = 1,
            self_introduction = '',
            is_hot_user       = True,
            is_active         = True,
            tag_ids           = [],
        )
        u.save()
        ui = User.objects.all()
        r = Routine(
            dow          = ['1'],
            user_id_id   = ui[0].id,
            interest_ids = [],
            start_time   = '000000+0900',
            end_time     = '010000+0900',
            title        = '筋トレ',
        )
        r.save()
        ri = Routine.objects.all()
        t1 = Task(
            routine_id=ri[0],
            title='腹筋',
            detail='a',
            icon='🥹',
            required_time=90,
            is_notified=True
        )
        t1.save()
        t2 = Task(
            routine_id=ri[0],
            title='背筋',
            detail='a',
            icon='🥹',
            required_time=100,
            is_notified=False
        )
        t2.save()
        t3 = Task(
            routine_id=ri[0],
            title='腕立て伏せ',
            detail='a',
            icon='🥹',
            required_time=110,
            is_notified=True
        )
        t3.save()

        tf1 = TaskFinish(
            task_id=Task.objects.get(id=(ri[0].id-1)*3+1),
            is_achieved=True,
            done_time=100,
            routine_id=ri[0]
        )
        tf1.save()
        time.sleep(1)
        tf2 = TaskFinish(
            task_id=Task.objects.get(id=(ri[0].id-1)*3+2),
            is_achieved=False,
            done_time=100,
            routine_id=ri[0]
        )
        tf2.save()
        time.sleep(1)
        tf3 = TaskFinish(
            task_id=Task.objects.get(id=(ri[0].id-1)*3+3),
            is_achieved=True,
            done_time=100,
            routine_id=ri[0]
        )
        tf3.save()

        now = datetime.now()
        af = now - timedelta(days=1)
        request = {
            "data": {
                'day':af.strftime("%Y%m%dT%H%M%S%z")+'+0000',
                'routine_id':ri[0].id
            }
        }
        
        response = self.client.post(
            'http://127.0.0.1:8000/routine/timetree/after/get/',
            json.dumps(request),
            content_type="application/json"
        )
        res = response.json()

        tf = TaskFinish.objects.all()
        tfw1 = tf[0].when
        tfw2 = tf[1].when
        tfw3 = tf[2].when

        d1 = now + timedelta(days=1)
        d2 = now + timedelta(days=2)
        d3 = now + timedelta(days=3)
        d4 = now + timedelta(days=4)
        d5 = now + timedelta(days=5)
        d6 = now + timedelta(days=6)

        self.assertEqual(res['data']['data']['timetree']['days'],[{'day': d6.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d5.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d4.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d3.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d2.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d1.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': now.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': [{'task_finish_id': f'{(ri[0].id-1)*3+3}', 'finish_time': tfw3.strftime("%Y%m%dT%H%M%S%z"), 'done_time': 100, 'comment': None}, {'task_finish_id': f'{(ri[0].id-1)*3+2}', 'finish_time': tfw2.strftime("%Y%m%dT%H%M%S%z"), 'done_time': 100, 'comment': None}, {'task_finish_id': f'{(ri[0].id-1)*3+1}', 'finish_time': tfw1.strftime("%Y%m%dT%H%M%S%z"), 'done_time': 100, 'comment': None}]}],'error')

    # コメントありtimetreeafterのテスト
    def test_timetree_after_with_comment(self):
        u = User(
            username          = 'ヤマダ',
            email             = '1',
            age               = 19,
            job               = '',
            profile_media_id  = 1,
            self_introduction = '',
            is_hot_user       = True,
            is_active         = True,
            tag_ids           = [],
        )
        u.save()
        ui = User.objects.all()
        r = Routine(
            dow          = ['1'],
            user_id_id   = ui[0].id,
            interest_ids = [],
            start_time   = '000000+0900',
            end_time     = '010000+0900',
            title        = '筋トレ',
        )
        r.save()
        ri = Routine.objects.all()
        t1 = Task(
            routine_id=ri[0],
            title='腹筋',
            detail='a',
            icon='🥹',
            required_time=90,
            is_notified=True
        )
        t1.save()
        t2 = Task(
            routine_id=ri[0],
            title='背筋',
            detail='a',
            icon='🥹',
            required_time=100,
            is_notified=False
        )
        t2.save()
        t3 = Task(
            routine_id=ri[0],
            title='腕立て伏せ',
            detail='a',
            icon='🥹',
            required_time=110,
            is_notified=True
        )
        t3.save()

        tf1 = TaskFinish(
            task_id=Task.objects.get(id=(ri[0].id-1)*3+1),
            is_achieved=True,
            done_time=100,
            routine_id=ri[0]
        )
        tf1.save()
        time.sleep(1)
        tf2 = TaskFinish(
            task_id=Task.objects.get(id=(ri[0].id-1)*3+2),
            is_achieved=False,
            done_time=100,
            routine_id=ri[0]
        )
        tf2.save()
        time.sleep(1)
        tf3 = TaskFinish(
            task_id=Task.objects.get(id=(ri[0].id-1)*3+3),
            is_achieved=True,
            done_time=100,
            routine_id=ri[0]
        )
        tf3.save()

        c1 = Minicomment(
            task_finish_id=TaskFinish.objects.get(id=(ri[0].id-1)*3+1),
            comment='a'
        )
        c1.save()
        c2 = Minicomment(
            task_finish_id=TaskFinish.objects.get(id=(ri[0].id-1)*3+2),
            comment='b'
        )
        c2.save()
        c3 = Minicomment(
            task_finish_id=TaskFinish.objects.get(id=(ri[0].id-1)*3+3),
            comment='c'
        )
        c3.save()

        now = datetime.now()
        af = now - timedelta(days=1)
        request = {
            "data": {
                'day':af.strftime("%Y%m%dT%H%M%S%z")+'+0000',
                'routine_id':ri[0].id
            }
        }
        
        response = self.client.post(
            'http://127.0.0.1:8000/routine/timetree/after/get/',
            json.dumps(request),
            content_type="application/json"
        )
        res = response.json()

        tf = TaskFinish.objects.all()
        tfw1 = tf[0].when
        tfw2 = tf[1].when
        tfw3 = tf[2].when

        d1 = now + timedelta(days=1)
        d2 = now + timedelta(days=2)
        d3 = now + timedelta(days=3)
        d4 = now + timedelta(days=4)
        d5 = now + timedelta(days=5)
        d6 = now + timedelta(days=6)

        self.assertEqual(res['data']['data']['timetree']['days'],[{'day': d6.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d5.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d4.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d3.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d2.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d1.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': now.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': [{'task_finish_id': f'{(ri[0].id-1)*3+3}', 'finish_time': tfw3.strftime("%Y%m%dT%H%M%S%z"), 'done_time': 100, 'comment': 'c'}, {'task_finish_id': f'{(ri[0].id-1)*3+2}', 'finish_time': tfw2.strftime("%Y%m%dT%H%M%S%z"), 'done_time': 100, 'comment': 'b'}, {'task_finish_id': f'{(ri[0].id-1)*3+1}', 'finish_time': tfw1.strftime("%Y%m%dT%H%M%S%z"), 'done_time': 100, 'comment': 'a'}]}],'error')

    # コメントなしtimetreeaftertobeforeのテスト
    def test_timetree_aftertobefore(self):
        u = User(
            username          = 'ヤマダ',
            email             = '1',
            age               = 19,
            job               = '',
            profile_media_id  = 1,
            self_introduction = '',
            is_hot_user       = True,
            is_active         = True,
            tag_ids           = [],
        )
        u.save()
        ui = User.objects.all()
        r = Routine(
            dow          = ['1'],
            user_id_id   = ui[0].id,
            interest_ids = [],
            start_time   = '000000+0900',
            end_time     = '010000+0900',
            title        = '筋トレ',
        )
        r.save()
        ri = Routine.objects.all()
        t1 = Task(
            routine_id=ri[0],
            title='腹筋',
            detail='a',
            icon='🥹',
            required_time=90,
            is_notified=True
        )
        t1.save()
        t2 = Task(
            routine_id=ri[0],
            title='背筋',
            detail='a',
            icon='🥹',
            required_time=100,
            is_notified=False
        )
        t2.save()
        t3 = Task(
            routine_id=ri[0],
            title='腕立て伏せ',
            detail='a',
            icon='🥹',
            required_time=110,
            is_notified=True
        )
        t3.save()

        tf1 = TaskFinish(
            task_id=Task.objects.get(id=(ri[0].id-1)*3+1),
            is_achieved=True,
            done_time=100,
            routine_id=ri[0]
        )
        tf1.save()
        time.sleep(1)
        tf2 = TaskFinish(
            task_id=Task.objects.get(id=(ri[0].id-1)*3+2),
            is_achieved=False,
            done_time=100,
            routine_id=ri[0]
        )
        tf2.save()
        time.sleep(1)
        tf3 = TaskFinish(
            task_id=Task.objects.get(id=(ri[0].id-1)*3+3),
            is_achieved=True,
            done_time=100,
            routine_id=ri[0]
        )
        tf3.save()

        now = datetime.now()
        request = {
            "data": {
                'day':now.strftime("%Y%m%dT%H%M%S%z")+'+0000',
                'routine_id':ri[0].id
            }
        }
        
        response = self.client.post(
            'http://127.0.0.1:8000/routine/timetree/before_after/get/',
            json.dumps(request),
            content_type="application/json"
        )
        res = response.json()

        tf = TaskFinish.objects.all()
        tfw1 = tf[0].when
        tfw2 = tf[1].when
        tfw3 = tf[2].when

        d0 = now + timedelta(days=7)
        d1 = now + timedelta(days=6)
        d2 = now + timedelta(days=5)
        d3 = now + timedelta(days=4)
        d4 = now + timedelta(days=3)
        d5 = now + timedelta(days=2)
        d6 = now + timedelta(days=1)
        d7 = now - timedelta(days=1)
        d8 = now - timedelta(days=2)
        d9 = now - timedelta(days=3)
        d10 = now - timedelta(days=4)
        d11 = now - timedelta(days=5)
        d12 = now - timedelta(days=6)

        self.assertEqual(res['data']['data']['timetree']['days'],[{'day': d0.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d1.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d2.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d3.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d4.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d5.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d6.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': now.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': [{'task_finish_id': f'{(ri[0].id-1)*3+3}', 'finish_time': tfw3.strftime("%Y%m%dT%H%M%S%z"), 'done_time': 100, 'comment': None}, {'task_finish_id': f'{(ri[0].id-1)*3+2}', 'finish_time': tfw2.strftime("%Y%m%dT%H%M%S%z"), 'done_time': 100, 'comment': None}, {'task_finish_id': f'{(ri[0].id-1)*3+1}', 'finish_time': tfw1.strftime("%Y%m%dT%H%M%S%z"), 'done_time': 100, 'comment': None}]}, {'day': d7.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d8.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d9.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d10.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d11.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d12.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}],'error')

    # コメントありtimetreeaftertobeforeのテスト
    def test_timetree_aftertobefore_with_comment(self):
        u = User(
            username          = 'ヤマダ',
            email             = '1',
            age               = 19,
            job               = '',
            profile_media_id  = 1,
            self_introduction = '',
            is_hot_user       = True,
            is_active         = True,
            tag_ids           = [],
        )
        u.save()
        ui = User.objects.all()
        r = Routine(
            dow          = ['1'],
            user_id_id   = ui[0].id,
            interest_ids = [],
            start_time   = '000000+0900',
            end_time     = '010000+0900',
            title        = '筋トレ',
        )
        r.save()
        ri = Routine.objects.all()
        t1 = Task(
            routine_id=ri[0],
            title='腹筋',
            detail='a',
            icon='🥹',
            required_time=90,
            is_notified=True
        )
        t1.save()
        t2 = Task(
            routine_id=ri[0],
            title='背筋',
            detail='a',
            icon='🥹',
            required_time=100,
            is_notified=False
        )
        t2.save()
        t3 = Task(
            routine_id=ri[0],
            title='腕立て伏せ',
            detail='a',
            icon='🥹',
            required_time=110,
            is_notified=True
        )
        t3.save()

        tf1 = TaskFinish(
            task_id=Task.objects.get(id=(ri[0].id-1)*3+1),
            is_achieved=True,
            done_time=100,
            routine_id=ri[0]
        )
        tf1.save()
        time.sleep(1)
        tf2 = TaskFinish(
            task_id=Task.objects.get(id=(ri[0].id-1)*3+2),
            is_achieved=False,
            done_time=100,
            routine_id=ri[0]
        )
        tf2.save()
        time.sleep(1)
        tf3 = TaskFinish(
            task_id=Task.objects.get(id=(ri[0].id-1)*3+3),
            is_achieved=True,
            done_time=100,
            routine_id=ri[0]
        )
        tf3.save()

        c1 = Minicomment(
            task_finish_id=TaskFinish.objects.get(id=(ri[0].id-1)*3+1),
            comment='a'
        )
        c1.save()
        c2 = Minicomment(
            task_finish_id=TaskFinish.objects.get(id=(ri[0].id-1)*3+2),
            comment='b'
        )
        c2.save()
        c3 = Minicomment(
            task_finish_id=TaskFinish.objects.get(id=(ri[0].id-1)*3+3),
            comment='c'
        )
        c3.save()

        now = datetime.now()
        request = {
            "data": {
                'day':now.strftime("%Y%m%dT%H%M%S%z")+'+0000',
                'routine_id':ri[0].id
            }
        }
        
        response = self.client.post(
            'http://127.0.0.1:8000/routine/timetree/before_after/get/',
            json.dumps(request),
            content_type="application/json"
        )
        res = response.json()

        tf = TaskFinish.objects.all()
        tfw1 = tf[0].when
        tfw2 = tf[1].when
        tfw3 = tf[2].when

        d0 = now + timedelta(days=7)
        d1 = now + timedelta(days=6)
        d2 = now + timedelta(days=5)
        d3 = now + timedelta(days=4)
        d4 = now + timedelta(days=3)
        d5 = now + timedelta(days=2)
        d6 = now + timedelta(days=1)
        d7 = now - timedelta(days=1)
        d8 = now - timedelta(days=2)
        d9 = now - timedelta(days=3)
        d10 = now - timedelta(days=4)
        d11 = now - timedelta(days=5)
        d12 = now - timedelta(days=6)

        self.assertEqual(res['data']['data']['timetree']['days'],[{'day': d0.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d1.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d2.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d3.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d4.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d5.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d6.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': now.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': [{'task_finish_id': f'{(ri[0].id-1)*3+3}', 'finish_time': tfw3.strftime("%Y%m%dT%H%M%S%z"), 'done_time': 100, 'comment': 'c'}, {'task_finish_id': f'{(ri[0].id-1)*3+2}', 'finish_time': tfw2.strftime("%Y%m%dT%H%M%S%z"), 'done_time': 100, 'comment': 'b'}, {'task_finish_id': f'{(ri[0].id-1)*3+1}', 'finish_time': tfw1.strftime("%Y%m%dT%H%M%S%z"), 'done_time': 100, 'comment': 'a'}]}, {'day': d7.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d8.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d9.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d10.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d11.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}, {'day': d12.strftime("%Y%m%dT%H%M%S%z")+'+0000', 'tasks': []}],'error')
