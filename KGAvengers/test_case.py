from django.test import TestCase
from drop_and_create_db import random_dt, insert_routine_routines, insert_routine_tasks, insert_routine_task_finishes
from routine.views_package import timetree
from routine.models import Routine, Task, TaskFinish, Minicomment
from datetime import timedelta
from supply_auth.models import User

class TimeTreeTests(TestCase):
    def test_timetree_before(self):
        day = random_dt()
        request = {
            'day':day.isoformat(),
            'routine_id':1
        }
        u = User(
            username          = 'ヤマダ',
            email             = '',
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
        insert_routine_task_finishes([{'task_id':1,
                                       'when':day - timedelta(days=3)},
                                       {'task_id':2,
                                       'when':day - timedelta(days=2)},
                                       {'task_id':3,
                                       'when':day - timedelta(days=1)}])

        print(timetree.TimeTreeBefore())

    def test_with_comment(self):
        day = random_dt()
        request = {
            'day':day.isoformat(),
            'routine_id':1
        }
        u = User(
            username          = 'ヤマダ',
            email             = '',
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
        insert_routine_task_finishes([{'task_id':1,
                                       'when':day - timedelta(days=1,minutes=20)},
                                       {'task_id':2,
                                       'when':day - timedelta(days=1,minutes=10)},
                                       {'task_id':3,
                                       'when':day - timedelta(days=1)}])
        z = Minicomment(
            table_name     = 'minicomment',
            task_finish_id = 3,
            comment        = 'いい運動になった'
        )
        z.save()

        print(timetree.TimeTreeBefore())

        