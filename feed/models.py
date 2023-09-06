from django.db import models
import secret
import boto3
import random

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
        table_name = 'interest_category'
        
        @classmethod
        def create(cls, data, format=None):
            if data.score <= 100: #数値は仮置き
                Item = {
                    'categoryid': 1,
                    'priority': 100,
                    'data': {}
                }

            elif 100 < data.score <=200:
                Item = {
                    'categoryid': 1,
                    'priority': 110,
                    'data': {}
                }

            else:
                num = random.randint(200,300)
                Item = {
                    'categoryid': 1,
                    'priority': num,
                    'data': {}
                }
            table = cls.get_dynamodb_table()
            table.put_item(Item=Item)
        
        def update(self, request, format=None):
            options = {
                'TableName': self.table_name,
                'Key': {
                    'Categoryid': {'N': ''},
                    'Priority': {'N': ''}
                },
                'ExpressionAttributeValues': {
                    'data': {'M' : request.data}
                }
            }
            self.dynamodb.update_item(**options)