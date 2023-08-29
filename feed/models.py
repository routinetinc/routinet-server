from django.db import models
import secret
import boto3

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

