from django.test import TestCase
from drop_and_create_db import random_dt
from routine.views_package import timetree
from routine.models import Task, TaskFinish, Minicomment
from datetime import timedelta

class TimeTreeTests(TestCase):
    def test_timetree_before(self):
        day = random_dt()
        request = {
            'day':day.isoformat(),
            'routine_id':1
        }
        p = Task(
            table_name    = 'task',
            routine_id    = 1,
            title         = '腹筋',
            detail        = '30回行う',
            icon          = '筋',
            required_time = 300,
            is_notified   = False
        )
        p.save()
        s = Task(
            table_name    = 'task',
            routine_id    = 1,
            title         = '腕立て伏せ',
            detail        = '20回行う',
            icon          = 'ト',
            required_time = 200,
            is_notified   = False
        )
        s.save()
        x = Task(
            table_name    = 'task',
            routine_id    = 1,
            title         = '背筋',
            detail        = '25回行う',
            icon          = 'レ',
            required_time = 100,
            is_notified   = False
        )
        x.save()
        q = TaskFinish(
            table_name  = 'task_finish',
            task_id     = 1,
            routine_id    = 1,
            is_achieved = True,
            done_time   = 300,
            when        = (day - timedelta(days=3)),
            like_num = 0
        )
        q.save()
        t = TaskFinish(
            table_name  = 'task_finish',
            task_id     = 2,
            routine_id    = 1,
            is_achieved = True,
            done_time   = 200,
            when        = (day - timedelta(days=2)),
            like_num = 0
        )
        t.save()
        y = TaskFinish(
            table_name  = 'task_finish',
            task_id     = 3,
            routine_id    = 1,
            is_achieved = True,
            done_time   = 100,
            when        = (day - timedelta(days=1)),
            like_num = 0
        )
        y.save()

        print(timetree.TimeTreeBefore(request))

    def test_with_comment(self):
        day = random_dt()
        request = {
            'day':day.isoformat(),
            'routine_id':1
        }
        p = Task(
            table_name    = 'task',
            routine_id    = 1,
            title         = '腹筋',
            detail        = '30回行う',
            icon          = '筋',
            required_time = 300,
            is_notified   = False
        )
        p.save()
        s = Task(
            table_name    = 'task',
            routine_id    = 1,
            title         = '腕立て伏せ',
            detail        = '20回行う',
            icon          = 'ト',
            required_time = 200,
            is_notified   = False
        )
        s.save()
        x = Task(
            table_name    = 'task',
            routine_id    = 1,
            title         = '背筋',
            detail        = '25回行う',
            icon          = 'レ',
            required_time = 100,
            is_notified   = False
        )
        x.save()
        q = TaskFinish(
            table_name  = 'task_finish',
            task_id     = 1,
            routine_id    = 1,
            is_achieved = True,
            done_time   = 300,
            when        = (day - timedelta(days=3)),
            like_num = 0
        )
        q.save()
        t = TaskFinish(
            table_name  = 'task_finish',
            task_id     = 2,
            routine_id    = 1,
            is_achieved = True,
            done_time   = 200,
            when        = (day - timedelta(days=2)),
            like_num = 0
        )
        t.save()
        y = TaskFinish(
            table_name  = 'task_finish',
            task_id     = 3,
            routine_id    = 1,
            is_achieved = True,
            done_time   = 100,
            when        = (day - timedelta(days=1)),
            like_num = 0
        )
        y.save()
        z = Minicomment(
            table_name     = 'minicomment',
            task_finish_id = 3,
            comment        = 'いい運動になった'
        )

        print(timetree.TimeTreeBefore(request))