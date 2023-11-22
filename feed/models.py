from django.db import models
from django.contrib.postgres.fields import ArrayField
import secret
import boto3
from django.contrib.postgres.fields import ArrayField
from auths.models import User  # 2つ目のmodels.pyからインポート
from routine.fields import CustomModels  # 1つ目のmodels.pyから仮にインポート（必要に応じて）
from routine.models import RoutineFinish, Tag  # 1つ目のmodels.pyからインポート
from django.utils import timezone

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

class FeedPost(models.Model):
    table_name   = "feed_post"
    user_id      = models.ForeignKey(User, on_delete=models.CASCADE)
    sentence     = models.CharField(max_length=400, blank=True)
    #media_id    = models.IntegerField(null=True, blank=True)
    post_time    = models.DateTimeField()
    like_num     = models.IntegerField(default=0)
    interest_ids = ArrayField(models.IntegerField(null=True, blank=True))
    tag_id       = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Sentence is 「{self.sentence}」"
    
    def save(self, *args, **kwargs):
        self.when = timezone.now()  # 保存されるたびに更新
        return super(FeedPost, self).save(*args, **kwargs)

class FeedPostComment(models.Model):
    feed_post_id = models.ForeignKey(FeedPost, on_delete=models.CASCADE)
    post_time    = models.DateTimeField()
    #media_id    = models.IntegerField(null=True, blank=True)
    like_num     = models.IntegerField(default=0)
    comment      = models.CharField(max_length=400, blank=True)

    def __str__(self):
        return f"Comment on FeedPost {self.feed_post_id} at {self.post_time}"
    
    def save(self, *args, **kwargs):
        self.when = timezone.now()  # 保存されるたびに更新
        return super(FeedPostComment, self).save(*args, **kwargs)
    

class RoutineFinishComment(models.Model):
    routine_finish_id = models.ForeignKey(RoutineFinish, on_delete=models.CASCADE)
    post_time         = models.DateTimeField()
    #media_id         = models.IntegerField(null=True, blank=True)
    like_num          = models.IntegerField(default=0)
    comment           = models.CharField(max_length=400, blank=True)

    def __str__(self):
        return f"Comment on Routine_finish {self.routine_finish_id} at {self.post_time}"
    
    def save(self, *args, **kwargs):
        self.when = timezone.now()  # 保存されるたびに更新
        return super(FeedPostComment, self).save(*args, **kwargs)