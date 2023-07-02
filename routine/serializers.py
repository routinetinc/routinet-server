from rest_framework import serializers

class Task_create(serializers.Serializer):
    routine_id    = serializers.IntegerField(max_value=None, min_value=None)
    title         = serializers.CharField(max_length=20, min_length=None, allow_blank=False, trim_whitespace=True)
    detail        = serializers.CharField(max_length=60, min_length=None, allow_blank=True, trim_whitespace=True)
    icon          = serializers.CharField(max_length=1, min_length=None, allow_blank=True, trim_whitespace=True)
    required_time = serializers.IntegerField(max_value=None, min_value=None)
    notification  = serializers.BooleanField()
    
class Routine_create(serializers.Serializer):
    dow           = serializers.IntegerField(max_value=None, min_value=None)
    #start_time = models.TimeField()
    #end_time = models.TimeField()  # 時間未設定タスクを含んだ幅を持たせる
    title         = serializers.CharField(max_length=15, min_length=None, allow_blank=False, trim_whitespace=True)
    subtitle      = serializers.CharField(max_length=40, min_length=None, allow_blank=True, trim_whitespace=True)
    icon          = serializers.CharField(max_length=1, min_length=None, allow_blank=True, trim_whitespace=True)
    public        = serializers.BooleanField()
    notification  = serializers.BooleanField()