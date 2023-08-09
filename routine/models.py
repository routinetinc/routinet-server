from django.db import models
from routine.fields import CustomModels
import boto3
from supplyAuth.models import User


class NoSQLBase(models.Model):
    table_name = ''
    class Meta:
        abstract = True

    @classmethod
    def get_dynamodb_table(self):
        session = boto3.Session(
            aws_access_key_id = 'AKIA2HQ6AQ7J2RVE4OB3',
            aws_secret_access_key = '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',
            region_name = 'ap-northeast-3'
        )
        dynamodb = session.resource('dynamodb')
        return dynamodb.Table(self.table_name)
    
    @classmethod
    def create(cls, Item):
        table = cls.get_dynamodb_table()
        table.put_item(Item = Item)
    
    @classmethod
    def get(cls, id):
        table = cls.get_dynamodb_table()
        response = table.get_item(Key={'id': id})
        item = response.get('Item')
        if item:
            return item
        return None
    
    @classmethod
    def delete(cls, id):
        table = cls.get_dynamodb_table()
        table.delete_item(Key={'id': id})
        
class NoSQL():
    class test(NoSQLBase):
        table_name = 'test'

    
class Interest(models.Model): # 外部キーのため依存解消のために仮置き
    table_name  = 'interest'
    name        = models.CharField(max_length=20) 

class Routine(models.Model):
    table_name   = 'routine'
    user_id      = models.ForeignKey(User, on_delete=models.CASCADE)        # user_id はバックエンドで取得      # 仮の数字を代入して対処
    interest_id  = models.ManyToManyField(Interest, default=1)              # interest_id はバックエンドで取得  # 複数のラベルが付く可能性を加味
    goal_id      = models.IntegerField(blank=True, default=0)               # goal_id はバックエンドで取得      # 仮の数字を代入して対処
    dow          = CustomModels.DOWField()                                  # 型は仮置き  # day_of_week (曜日のこと)
    start_time   = CustomModels.TimeStringField()
    end_time     = CustomModels.TimeStringField()                           # 時間未設定タスクを含んだ幅を持たせる
    title        = models.CharField(max_length=15)                          # 10 文字に余裕を持たせて 15 文字
    subtitle     = models.CharField(max_length=40, blank=True)              # 簡易的な補足説明
    icon         = models.CharField(max_length=1, blank=True)
    is_published = models.BooleanField(help_text='公開設定', default=False)
    is_notified  = models.BooleanField(help_text='通知設定', default=False)
    def __str__(self):
        return self.title

class Task(models.Model):
    table_name    = 'task'
    routine_id    = models.ForeignKey(Routine, on_delete=models.CASCADE)
    title         = models.CharField(max_length=20)             # ルーティンタイトルの限度より少し長い程度
    detail        = models.CharField(max_length=60, blank=True) # 60 文字に仮置き  # あまり情報を詰め込みすぎないことが目標
    icon          = models.CharField(max_length=1, blank=True)
    required_time = models.IntegerField()
    is_notified   = models.BooleanField(help_text='通知設定', default=False)
    def __str__(self):
        return self.title

class TaskComment(models.Model):
    table_name  = 'task_comment'
    task_id     = models.ForeignKey('Task', on_delete=models.PROTECT)
    comment     = models.CharField(max_length=120)
    def __str__(self):
        return f'{self.task_id}'

class TaskRecord(models.Model):
    table_name  = 'task_record'
    task_id     = models.ForeignKey(Task, on_delete=models.PROTECT)
    is_achieved = models.BooleanField(help_text='完了したか', default=False) 
    done_time   = models.IntegerField()
    when        = models.DateTimeField()
    def __str__(self):
        return f'{self.task_id}'