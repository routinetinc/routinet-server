from django.test import TestCase, RequestFactory, Client
from drop_and_create_db import random_dt, insert_routine_routines, insert_routine_tasks, insert_routine_task_finishes, insert_routine_task_comments
from routine.views_package import timetree
from routine.models import Routine, Task, TaskFinish, Minicomment
from datetime import timedelta
from supply_auth.models import User
import json
import requests
import datetime

class TimeTreeTests(TestCase):
    headers = {'Content-Type': 'application/json'}
    request = {
            "data": {
                'day':"20231111T101010+0900",
                'routine_id':1
            }
        }
    def setUp(self):
        self.client = Client()
        self.client.login(email='email', password='password')

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
        insert_routine_routines([{'dow':['1'],
                                  'title':'筋トレ'}])
        insert_routine_tasks([{'routine_id':1,
                               'title':'腹筋'},
                               {'routine_id':1,
                               'title':'背筋'},
                               {'routine_id':1,
                               'title':'腕立て伏せ'}])
        insert_routine_task_finishes([{'title':'腹筋',
                                       'when':datetime.datetime.strptime("20231110T101010+0900","%Y%m%dT%H%M%S%z")},
                                       {'title':'背筋',
                                       'when':datetime.datetime.strptime("20231110T101009+0900","%Y%m%dT%H%M%S%z")},
                                       {'title':'腕立て伏せ',
                                       'when':datetime.datetime.strptime("20231110T101008+0900","%Y%m%dT%H%M%S%z")}])
        
        response = requests.post('http://127.0.0.1:8000/routine/timetree/before/get/', json=self.request, headers=self.headers)
        res = response.json()
        
        self.assertEqual(res['data']['data']['timetree']['days'],1,'error')

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
        insert_routine_routines([{'dow':['1'],
                                  'title':'筋トレ'}])
        insert_routine_tasks([{'routine_id':1,
                               'title':'腹筋'},
                               {'routine_id':1,
                               'title':'背筋'},
                               {'routine_id':1,
                               'title':'腕立て伏せ'}])
        insert_routine_task_finishes([{'title':'腹筋',
                                       'when':"20231110T101010+0900"},
                                       {'title':'背筋',
                                       'when':"20231109T101010+0900"},
                                       {'title':'腕立て伏せ',
                                       'when':"20231108T101010+0900"}])
        insert_routine_task_comments({})

        response = requests.post('http://127.0.0.1:8000/routine/timetree/before/get/', json=self.request, headers=self.headers)
        res = response.json()
        
        self.assertEqual(res['data'],1,'error')

    def test_timetree_after(self):
        day = random_dt()
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
        insert_routine_routines([{'dow':['1'],
                                  'title':'筋トレ'}])
        insert_routine_tasks([{'routine_id':1,
                               'title':'腹筋'},
                               {'routine_id':1,
                               'title':'背筋'},
                               {'routine_id':1,
                               'title':'腕立て伏せ'}])
        insert_routine_task_finishes([{'title':'腹筋',
                                       'when':day + timedelta(days=3)},
                                       {'title':'背筋',
                                       'when':day + timedelta(days=2)},
                                       {'title':'腕立て伏せ',
                                       'when':day + timedelta(days=1)}])

        response = requests.post('http://127.0.0.1:8000/routine/timetree/after/get/', json=self.request, headers=self.headers)
        res = response.json()
        
        self.assertEqual(res['data'],1,'error')

    def test_timetree_after_with_comment(self):
        day = random_dt()
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
        insert_routine_routines([{'dow':['1'],
                                  'title':'筋トレ'}])
        insert_routine_tasks([{'routine_id':1,
                               'title':'腹筋'},
                               {'routine_id':1,
                               'title':'背筋'},
                               {'routine_id':1,
                               'title':'腕立て伏せ'}])
        insert_routine_task_finishes([{'title':'腹筋',
                                       'when':day - timedelta(days=1,minutes=20)},
                                       {'title':'背筋',
                                       'when':day - timedelta(days=1,minutes=10)},
                                       {'title':'腕立て伏せ',
                                       'when':day - timedelta(days=1)}])
        insert_routine_task_comments({})

        response = requests.post('http://127.0.0.1:8000/routine/timetree/after/get/', json=self.request, headers=self.headers)
        res = response.json()
        
        self.assertEqual(res['data'],1,'error')
    
    def test_timetree_aftertobefore(self):
        day = random_dt()
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
        insert_routine_routines([{'dow':['1'],
                                  'title':'筋トレ'}])
        insert_routine_tasks([{'routine_id':1,
                               'title':'腹筋'},
                               {'routine_id':1,
                               'title':'背筋'},
                               {'routine_id':1,
                               'title':'腕立て伏せ'}])
        insert_routine_task_finishes([{'title':'腹筋',
                                       'when':day + timedelta(days=3)},
                                       {'title':'背筋',
                                       'when':day + timedelta(days=2)},
                                       {'title':'腕立て伏せ',
                                       'when':day + timedelta(days=1)}])

        response = requests.post('http://127.0.0.1:8000/routine/timetree/before_after/get/', json=self.request, headers=self.headers)
        res = response.json()
        
        self.assertEqual(res['data'],1,'error')

    def test_timetree_aftertobefore_with_comment(self):
        day = random_dt()
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
        insert_routine_routines([{'dow':['1'],
                                  'title':'筋トレ'}])
        insert_routine_tasks([{'routine_id':1,
                               'title':'腹筋'},
                               {'routine_id':1,
                               'title':'背筋'},
                               {'routine_id':1,
                               'title':'腕立て伏せ'},
                               {'routine_id':1,
                               'title':'スクワット'},
                               {'routine_id':1,
                               'title':'プランク'},
                               {'routine_id':1,
                               'title':'プレス'}])
        insert_routine_task_finishes([{'title':'腹筋',
                                       'when':day - timedelta(days=1,minutes=20)},
                                       {'title':'背筋',
                                       'when':day - timedelta(days=1,minutes=10)},
                                       {'title':'腕立て伏せ',
                                       'when':day - timedelta(days=1)},
                                       {'title':'スクワット',
                                       'when':day + timedelta(days=3)},
                                       {'title':'プランク',
                                       'when':day + timedelta(days=2)},
                                       {'title':'プレス',
                                       'when':day + timedelta(days=1)}])
        insert_routine_task_comments({})

        response = requests.post('http://127.0.0.1:8000/routine/timetree/before_after/get/', json=self.request, headers=self.headers)
        res = response.json()
        
        self.assertEqual(res['data'],1,'error')

