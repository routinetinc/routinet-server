from django.db import models
from routine.fields import CustomModels
from supply_auth.models import User
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
    
class Interest(models.Model): # 外部キーのため依存解消のために仮置き
    table_name  = 'interest'
    name        = models.CharField(max_length=20) 

class Routine(models.Model):
    table_name   = 'routine'
    user_id      = models.ForeignKey(User, on_delete=models.CASCADE)        # user_id はバックエンドで取得      # 仮の数字を代入して対処
    interest_ids = ArrayField(models.IntegerField(null=True, blank=True))
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
    def __str__(self):
        return self.title

class Task(models.Model):
    table_name    = 'task'
    routine_id    = models.ForeignKey(Routine, on_delete=models.CASCADE)
    title         = models.CharField(max_length=20)             # ルーティンタイトルの限度より少し長い程度
    detail        = models.CharField(max_length=60, blank=True) # 60 文字に仮置き  # あまり情報を詰め込みすぎないことが目標
    icon          = models.CharField(max_length=1, blank=True)
    required_time = models.IntegerField()
    def __str__(self):
        return self.title

class TaskFinish(models.Model):
    table_name  = 'task_finish'
    task_id     = models.ForeignKey(Task, on_delete=models.PROTECT)
    routine_id    = models.ForeignKey(Routine, on_delete=models.CASCADE)
    is_achieved = models.BooleanField(help_text='完了したか', default=True) 
    done_time   = models.IntegerField()
    when        = models.DateTimeField(help_text='完了日時')
    like_num = models.IntegerField(default=0)
    
    def save(self, *args, **kwargs):
        self.when = timezone.now()  # 保存されるたびに更新
        return super(TaskFinish, self).save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.task_id}'
    
class Minicomment(models.Model):
    table_name     = 'minicomment'
    task_finish_id = models.ForeignKey(TaskFinish, on_delete=models.PROTECT)
    comment        = models.CharField(max_length=120)
    def __str__(self):
        return f'{self.task_finish_id}'