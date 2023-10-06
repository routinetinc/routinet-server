from django.db import models
from django.contrib.postgres.fields import ArrayField
import secret
import boto3
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from supply_auth.models import User  # 2つ目のmodels.pyからインポート
from routine.fields import CustomModels  # 1つ目のmodels.pyから仮にインポート（必要に応じて）
from routine.models import Interest, TaskFinish  # 1つ目のmodels.pyからインポート

class NoSQLBase(models.Model):
    table_name = ''
        
    class Meta:
        abstract = True

    @classmethod
    def get_dynamodb_table(self):
        session = secret.BOTO3_SESSION
        dynamodb = session.resource('dynamodb')
        return dynamodb.Table(self.table_name)
    
    @classmethod
    def create(cls, Item):
        table = cls.get_dynamodb_table()
        table.put_item(Item = Item)
    
    @classmethod
    def get(cls, key):
        table = cls.get_dynamodb_table()
        response = table.get_item(Key=key)
        item = response.get('Item')
        if item:
            return item
        return None
    
    @classmethod
    def delete(cls, key):
        table = cls.get_dynamodb_table()
        table.delete_item(Key=key)
        
class Cache():
    class User(NoSQLBase):
        table_name = 'usercache'
    
    class InterestCAT(NoSQLBase):
        table_name = 'usercache'


# Challengeモデルは独自に定義（適切な場所からインポートする必要があるかもしれません）
class Challenge(models.Model):
    name = models.CharField(max_length=255)

class FeedPost(models.Model):
    table_name = "feed_post"
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sentence = models.CharField(max_length=400, blank=True)
    media_id = models.IntegerField(null=True, blank=True)
    post_time = models.DateTimeField()
    like_num = models.IntegerField(default=0)
    interest_ids = ArrayField(models.IntegerField(null=True, blank=True))
    challenge_id = models.ForeignKey(Challenge, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.sentence


    def __str__(self):
        return self.sentence

class FeedPostComment(models.Model):
    feed_post_id = models.ForeignKey(FeedPost, on_delete=models.CASCADE)
    post_time = models.DateTimeField()
    media_id = models.IntegerField(null=True, blank=True)
    like_num = models.IntegerField(default=0)
    comment = models.CharField(max_length=400)

    def __str__(self):
        return f"Comment by {self.feed_post.user} on {self.post_time}"
    
    def __str__(self):
        return f'{self.feed_post_id}'
    

class TaskFinishComment(models.Model):
    task_finish_id = models.ForeignKey(TaskFinish, on_delete=models.CASCADE)
    post_time = models.DateTimeField()
    media_id = models.IntegerField(null=True, blank=True)
    like_num = models.IntegerField(default=0)
    comment = models.CharField(max_length=400)

    def __str__(self):
        return f"Comment on TaskFinish {self.task_finish_id} at {self.post_time}"

class Tag(models.Model):
    name = models.CharField(max_length=400, blank=True)

    def __str__(self):
        return f"{self.name}"