from django.db import models
import boto3
import json
from supplyAuth.models import User

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

class Interest(models.Model): # 仮置き
    table_name = 'interest'

class Routine(models.Model):
    table_name = 'routine'
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    interest_id = models.OneToOneField(Interest, on_delete=models.PROTECT)
    title = models.CharField(max_length=15)  # 10 文字に余裕を持たせて 15 文字
    def __str__(self):
        return self.title
    

class Task(models.Model):
    table_name = 'task'
    routine_id = models.ForeignKey(Routine, on_delete=models.CASCADE)
    title = models.CharField(max_length=20)  # ルーティンタイトルの限度より少し長い程度
    detail = models.CharField(max_length=60, blank=True)  # 60 文字に仮置き. あまり情報を詰め込みすぎないことを目標に.
    icon = models.CharField(max_length=1, blank=True)
    required_time = models.IntegerField()
    def __str__(self):
        return self.title
