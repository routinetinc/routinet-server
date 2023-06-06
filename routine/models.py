from django.db import models
import boto3

class NoSQLBase(models.Model):
    table_name = ''
    
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
    class User(NoSQLBase):
        table_name = "test"