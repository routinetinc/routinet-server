from rest_framework import serializers
from datetime import datetime
from fields import TimeStringField


class Task_create(serializers.Serializer):  # /api/routine/create(POST)
    routine_id    = serializers.IntegerField(max_value=None, min_value=None)
    title         = serializers.CharField(max_length=20, min_length=None, allow_blank=False, trim_whitespace=True)
    detail        = serializers.CharField(max_length=60, min_length=None, allow_blank=True, trim_whitespace=True)
    icon          = serializers.CharField(max_length=1, min_length=None, allow_blank=True, trim_whitespace=True)
    required_time = serializers.IntegerField(max_value=None, min_value=None)
    notification  = serializers.BooleanField()
    
class Routine_create(serializers.Serializer):  # /api/task/create(POST)
    dow           = serializers.ListField(child=serializers.CharField(max_length=1))
    start_time    = TimeStringField()
    end_time      = TimeStringField()  # 時間未設定タスクを含んだ幅を持たせる
    title         = serializers.CharField(max_length=15, min_length=None, allow_blank=False, trim_whitespace=True)
    subtitle      = serializers.CharField(max_length=40, min_length=None, allow_blank=True, trim_whitespace=True)
    icon          = serializers.CharField(max_length=1, min_length=None, allow_blank=True, trim_whitespace=True)
    public        = serializers.BooleanField()
    notification  = serializers.BooleanField()
    
class Task_update(serializers.Serializer):  # /api/routine(PATCH)
    task_id       = serializers.IntegerField(max_value=None, min_value=None)
    title         = serializers.CharField(max_length=20, min_length=None, allow_blank=False, trim_whitespace=True)
    detail        = serializers.CharField(max_length=60, min_length=None, allow_blank=True, trim_whitespace=True)
    icon          = serializers.CharField(max_length=1, min_length=None, allow_blank=True, trim_whitespace=True)
    required_time = serializers.IntegerField(max_value=None, min_value=None)
    notification  = serializers.BooleanField()
    
class Routine_update(serializers.Serializer):  # /api/task(PATCH)
    routine_id    = serializers.IntegerField(max_value=None, min_value=None)
    dow           = serializers.ListField(child=serializers.IntegerField(min_value=0, max_value=6))
    start_time    = TimeStringField()
    end_time      = TimeStringField()  # 時間未設定タスクを含んだ幅を持たせる
    title         = serializers.CharField(max_length=15, min_length=None, allow_blank=False, trim_whitespace=True)
    subtitle      = serializers.CharField(max_length=40, min_length=None, allow_blank=True, trim_whitespace=True)
    icon          = serializers.CharField(max_length=1, min_length=None, allow_blank=True, trim_whitespace=True)
    public        = serializers.BooleanField()
    notification  = serializers.BooleanField()
    
class Task_delete(serializers.Serializer):  # /api/routine(DELETE)
    task_id       = serializers.IntegerField(max_value=None, min_value=None)
    
class Routine_delete(serializers.Serializer):  # /api/task(DELETE)
    routine_id    = serializers.IntegerField(max_value=None, min_value=None)