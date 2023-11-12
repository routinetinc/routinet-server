from django.db import models
from routine.fields import CustomModels
from supply_auth.models import User
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
    tag_id       = models.ForeignKey(Tag, on_delete=models.DO_NOTHING,null=True)
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

    def calculate_consecutive_days(self):
        # Filter RoutineFinish records by routine_id, ordered by 'when' descending
        all_records = RoutineFinish.objects.filter(routine_id=self.id).order_by('-when')

        if not all_records:
            print("No records found for routine.")
            return 0  # If no records found, return 0

        consecutive_days = 1  # Start the count from the most recent record if it's achieved

        for record in all_records:
            print(record.is_achieved)
            if record.is_achieved:
                consecutive_days += 1  # Increment if the task was achieved
            else:
                break  # Stop counting when a non-achieved record is encountered

        return consecutive_days

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
    routine_id = models.ForeignKey(Routine, on_delete=models.PROTECT)
    is_achieved = models.BooleanField(default=True, help_text='完了したか')
    icon = models.CharField(max_length=4, help_text='アイコン')  # 4 chars to accommodate any UTF-8mb4 character
    memo = models.TextField(blank=True, null=True, help_text='メモ')  # Use TextField if memos can be long
    done_time = models.IntegerField(help_text='実行時間（分）')
    when = models.DateTimeField(help_text='完了日時')  
    like_num = models.IntegerField(default=0, help_text='いいねの数')
    share = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.when = timezone.now()  
        super(RoutineFinish, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.routine_id)  
    
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
