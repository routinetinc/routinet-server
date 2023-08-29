from django.db import models
import secret
import boto3

class NoSQLBase(models.Model):
    def __init__(self):
        self.table_name = ''
        
    class Meta:
        abstract = True

    @classmethod
    def get_dynamodb_table(self):
        session = secret.BOTO3_SESSION
        dynamodb = session.resource('dynamodb')
        return dynamodb.Table(self.table_name)
    
    @classmethod
    def create(self, Item):
        response = self.client.put_item(
                    TableName=self.table_name,
                    Item=Item
        )
    
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
        
class Cache():
    class User(NoSQLBase):
        table_name = 'usercache'
        client = boto3.client('dynamodb')
    
    class InterestCAT(NoSQLBase):
        table_name = 'usercache'

