from rest_framework import serializers
from routine.fields import CustomSerializers


class Task_create(serializers.Serializer):  # /routine/task/(POST)
    routine_id    = serializers.IntegerField(max_value=None, min_value=None)
    title         = serializers.CharField(max_length=20, min_length=None, allow_blank=False, trim_whitespace=True)
    detail        = serializers.CharField(max_length=60, min_length=None, allow_blank=True, trim_whitespace=True)
    icon          = serializers.CharField(max_length=1, min_length=None, allow_blank=True, trim_whitespace=True)
    required_time = serializers.IntegerField(max_value=None, min_value=0)
    is_notified   = serializers.BooleanField()
    
class Routine_create(serializers.Serializer):  # /routine/routine/(POST)
    dow           = serializers.ListField(child=serializers.CharField(max_length=1))
    start_time    = CustomSerializers.TimeStringField()
    end_time      = CustomSerializers.TimeStringField()  # 時間未設定タスクを含んだ幅を持たせる
    title         = serializers.CharField(max_length=15, min_length=None, allow_blank=False, trim_whitespace=True)
    subtitle      = serializers.CharField(max_length=40, min_length=None, allow_blank=True, trim_whitespace=True)
    icon          = serializers.CharField(max_length=1, min_length=None, allow_blank=True, trim_whitespace=True)
    is_published  = serializers.BooleanField()
    is_notified   = serializers.BooleanField()
    interest_ids  = serializers.ListField(child=serializers.IntegerField(max_value=None, min_value=None))
    
class Task_update(serializers.Serializer):  # /routine/task/(PATCH)
    task_id       = serializers.IntegerField(max_value=None, min_value=None)
    title         = serializers.CharField(max_length=20, min_length=None, allow_blank=False, trim_whitespace=True)
    detail        = serializers.CharField(max_length=60, min_length=None, allow_blank=True, trim_whitespace=True)
    icon          = serializers.CharField(max_length=1, min_length=None, allow_blank=True, trim_whitespace=True)
    required_time = serializers.IntegerField(max_value=None, min_value=0)
    is_notified   = serializers.BooleanField()
    
class Routine_update(serializers.Serializer):  # /routine/routine(PATCH)
    routine_id    = serializers.IntegerField(max_value=None, min_value=None)
    dow           = serializers.ListField(child=serializers.IntegerField(min_value=0, max_value=6))
    start_time    = CustomSerializers.TimeStringField()
    end_time      = CustomSerializers.TimeStringField()  # 時間未設定タスクを含んだ幅を持たせる
    title         = serializers.CharField(max_length=15, min_length=None, allow_blank=False, trim_whitespace=True)
    subtitle      = serializers.CharField(max_length=40, min_length=None, allow_blank=True, trim_whitespace=True)
    icon          = serializers.CharField(max_length=1, min_length=None, allow_blank=True, trim_whitespace=True)
    is_published  = serializers.BooleanField()
    is_notified   = serializers.BooleanField()
    interest_ids  = serializers.ListField(child=serializers.IntegerField(max_value=None, min_value=None))
    
class Task_delete(serializers.Serializer):  # /routine/task/(DELETE)
    task_id       = serializers.IntegerField(max_value=None, min_value=None)
    
class Routine_delete(serializers.Serializer):  # /routine/routine/(DELETE)
    routine_id    = serializers.IntegerField(max_value=None, min_value=None)
    
class TaskFinish_create(serializers.Serializer): # /routine/task/finish/(POST)
    task_id       = serializers.IntegerField(max_value=None, min_value=None)
    done_time     = serializers.IntegerField(max_value=None, min_value=0)
    
class MiniComment_create(serializers.Serializer): # /routine/task/minicomment/(POST)
    task_finish_id= serializers.IntegerField(max_value=None, min_value=None)
    comment       = serializers.CharField(max_length=50, min_length=None, allow_blank=False, trim_whitespace=False)
    
class MiniComment_update(serializers.Serializer): # /routine/task/minicomment/(PATCH)
    minicomment_id= serializers.IntegerField(max_value=None, min_value=None)
    comment       = serializers.CharField(max_length=50, min_length=None, allow_blank=False, trim_whitespace=False)
    
class TimeTree(serializers.Serializer):
    day           = CustomSerializers.ISOTimeField()
    routine_id    = serializers.IntegerField(max_value=None, min_value=1)


class RoutineFinishSerializer(serializers.Serializer):
    routine_id = serializers.IntegerField()
    icon = serializers.CharField(max_length=10)
    memo = serializers.CharField(max_length=255)

class ShareRegister(serializers.Serializer):
    routine_finish_id = serializers.IntegerField()
    share   = serializers.BooleanField()