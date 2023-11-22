from django.db import models
from routine.fields import CustomModels
from auths.models import User
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
    
class Interest(models.Model): # 外部キーのため依存解消のために仮置き
    table_name  = 'interest'
    name        = models.CharField(max_length=20) 
    detail      = models.CharField(max_length=50) 
    
    def __str__(self):
        return f"Interest name is 「{self.name}」"   
    
class Tag(models.Model):
    table_name  = 'tag'
    name        = models.CharField(max_length=20) 
    detail      = models.CharField(max_length=50) 

    def __str__(self):
        return f"Tag name is 「{self.name}」" 
    
class Routine(models.Model):
    table_name   = 'routine'
    user_id      = models.ForeignKey(User, on_delete=models.CASCADE)        # user_id はバックエンドで取得      # 仮の数字を代入して対処
    interest_ids = ArrayField(models.IntegerField(),null=True)
    tag_id       = models.ForeignKey(Tag, on_delete=models.DO_NOTHING)
    goal_id      = models.IntegerField(blank=True, default=0)               # goal_id はバックエンドで取得      # 仮の数字を代入して対処
    dow          = CustomModels.DOWField()                                  # 型は仮置き  # day_of_week (曜日のこと)
    start_time   = CustomModels.TimeStringField()
    end_time     = CustomModels.TimeStringField()                           # 時間未設定タスクを含んだ幅を持たせる
    title        = models.CharField(max_length=15)                          # 10 文字に余裕を持たせて 15 文字
    subtitle     = models.CharField(max_length=40, blank=True)              # 簡易的な補足説明
    icon         = models.CharField(max_length=1, blank=True)
    is_published = models.BooleanField(help_text='公開設定', default=False)
    is_notified  = models.BooleanField(help_text='通知設定', default=False)
    bookmark_num = models.IntegerField(default=0)
    is_real_time    = models.BooleanField(help_text='リアルタイムタスク', default=False)
    def __str__(self):
        return f"Routine title is 「{self.title}」"

class Task(models.Model):
    table_name    = 'task'
    routine_id    = models.ForeignKey(Routine, on_delete=models.CASCADE)
    title         = models.CharField(max_length=20)             # ルーティンタイトルの限度より少し長い程度
    detail        = models.CharField(max_length=60, blank=True) # 60 文字に仮置き  # あまり情報を詰め込みすぎないことが目標
    icon          = models.CharField(max_length=1, blank=True)
    required_time = models.IntegerField()
    is_notified   = models.BooleanField(help_text='通知設定', default=False)
    def __str__(self):
        return f"Task title is 「{self.title}」"

class RoutineFinish(models.Model):
    table_name         = 'routine_finish'
    routine_id         = models.ForeignKey(Routine, on_delete=models.PROTECT)
    is_achieved        = models.BooleanField(help_text='完了したか', default=True) 
    icon               = models.CharField(max_length=1, blank=True)
    memo               = models.CharField(max_length=60, blank=True)
    done_time          = models.IntegerField()
    when               = models.DateTimeField(help_text='完了日時')
    like_num           = models.IntegerField(default=0)
    
    def save(self, *args, **kwargs):
        self.when = timezone.now()  # 保存されるたびに更新
        return super(RoutineFinish, self).save(*args, **kwargs)
    
    def __str__(self):
        return f'RoutineFinish of Routine {self.routine_id} at {self.when}'
class TaskFinish(models.Model):
    table_name         = 'task_finish'
    task_id            = models.ForeignKey(Task, on_delete=models.PROTECT)
    routine_finish_id  = models.ForeignKey(RoutineFinish, on_delete=models.CASCADE,null=True)
    is_achieved        = models.BooleanField(help_text='完了したか', default=True) 
    done_time          = models.IntegerField()
    when               = models.DateTimeField(help_text='完了日時')
    
    def save(self, *args, **kwargs):
        self.when = timezone.now()  # 保存されるたびに更新
        return super(TaskFinish, self).save(*args, **kwargs)
    
    def __str__(self):
        return f'TaskFinish of Task {self.task_id} at {self.when}'
    
class Diary(models.Model):
    table_name    = 'daiary'
    when          = models.DateTimeField(help_text='作成日時')
    user_id       = models.ForeignKey(User, on_delete=models.CASCADE)
    comment       = models.CharField(max_length=500)
    icon          = models.CharField(max_length=1, blank=True)
    def __str__(self):
        return f"Dairy at {self.when} by user_id:{self.user_id}"