from django.db import models
import boto3
import json
from supplyAuth.models import User
from datetime import datetime

class NoSQLBase(models.Model):
    table_name = ''
    class Meta:
        abstract = True

    @classmethod
    def get_dynamodb_table(self):
        session = boto3.Session(
            aws_access_key_id='AKIA2HQ6AQ7J2RVE4OB3',
            aws_secret_access_key='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',
            region_name='ap-northeast-3'
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

class TimeField(models.DateTimeField):
    def __init__(self, *args, **kwargs):
        kwargs['default'] = '00:00:00'
        super().__init__(*args, **kwargs)
    def from_db_value(self, value: datetime, expression, connection):
        if value is None:
            return value
        return value.strftime('%H:%M:%S')
    def to_python(self, value: datetime):
        if isinstance(value, str):
            return value
        if value is None:
            return value
        return value.strftime('%H:%M:%S')
    def get_prep_value(self, value: datetime):
        if isinstance(value, str):
            return value
        if value is None:
            return value
        return value.strftime('%H:%M:%S')
    
class Interest(models.Model): # 外部キーのため依存解消のために仮置き
    table_name = 'interest'

class Routine(models.Model):
    table_name = 'routine'
    user_id = models.ForeignKey(User, on_delete=models.CASCADE) # user_idはバックエンドで取得します。現段階では仮の数字を代入してください
    interest_id = models.OneToOneField(Interest, on_delete=models.PROTECT)# interest_idはバックエンドで取得します。現段階では仮の数字を代入してください
    goal_id = models.IntegerField()# interest_idはバックエンドで取得します。現段階では仮の数字を代入してください
    dow = models.IntegerField()  # 型は仮置き # day_of_week(曜日のこと)
    start_time = models.TimeField()
    end_time = models.TimeField()  # 時間未設定タスクを含んだ幅を持たせる
    title = models.CharField(max_length=15)  # 10 文字に余裕を持たせて 15 文字
    subtitle = models.CharField(max_length=40, blank=True)  # 簡易的な補足説明
    icon = models.CharField(max_length=1, blank=True)
    public = models.BooleanField(help_text='公開RoutineならTrue', default=False)
    notification = models.BooleanField(help_text='通知onならTrue', default=False)
    def __str__(self):
        return self.title
    

class Task(models.Model):
    table_name = 'task'
    routine_id = models.ForeignKey(Routine, on_delete=models.CASCADE)
    title = models.CharField(max_length=20)  # ルーティンタイトルの限度より少し長い程度
    detail = models.CharField(max_length=60, blank=True)  # 60 文字に仮置き. あまり情報を詰め込みすぎないことを目標に.
    icon = models.CharField(max_length=1, blank=True)
    required_time = models.IntegerField()
    notification = models.BooleanField(help_text='通知onならTrue', default=False)
    def __str__(self):
        return self.title
