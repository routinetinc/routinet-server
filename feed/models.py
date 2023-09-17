from django.db import models
import secret
import boto3
import random
import datetime
from boto3.dynamodb.conditions import Key, Attr

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

        @classmethod
        def create_meta(cls, data, format=None):
            table_name = 'interest_metadata'
            string = ''
            for i in range(200,400):
                string = string + 'a' + str(i)
            Item = {
                'categoryid': data.categoryid,
                'priority': ['a198','a199',string]
            }
            table = cls.get_dynamodb_table()
            table.put_item(Item=Item)
        
        @classmethod
        def create(cls, data, format=None):
            table_name = 'interest_category'
            if data.score <= 100: #数値は仮置き
                string = 'a198'

            elif 100 < data.score <=200:
                string = 'a199'

            else:
                string = ''
                for i in range(200,400):
                    string = string + 'a' + str(i)
                time = datetime.datetime.now().isoformat()
            Item = {
                'categoryid': data.categoryid,
                'priority': string,
                'time': time,
                'contentid': [data.contentid],
                'data': {
                    {
                        data.contentid,
                        data.score
                    }
                }
            }
            table = cls.get_dynamodb_table()
            table.put_item(Item=Item)
        
        @classmethod
        def put(cls, data, format=None):
            if data.score <= 100: #数値は仮置き
                num = 100

            elif 100 < data.score <=200:
                num = 110

            else:
                num = random.randint(200,300)
            options = {
                'Key': {
                    'categoryid': data.category_id,
                    'priority': num,
                },
                'UpdateExpression': 'set #data = list_append(data,:add)',
                'ExpressionAttributeNames': {'#data': 'data'},
                'ExpressionAttributeValues': {
                    ':add': {
                        data.content_id,
                        data.score
                    }
                }
            }
            table = cls.get_dynamodb_table()
            table.update_item(**options)

        @classmethod
        def update(cls, data, format=None):
            if data.score <= 100: #数値は仮置き
                num = [198]

            elif 100 < data.score <=200:
                
                num = [199]

            else:
                num = random.randint(200,300)
            options = {
                'Key': {
                    'categoryid': data.category_id,
                    'priority': num,
                },
                'UpdateExpression': 'set #data = list_append(data,:add)',
                'ExpressionAttributeNames': {'#data': 'data'},
                'ExpressionAttributeValues': {
                    ':add': {
                        data.content_id,
                        data.score
                    }
                }
            }
            table = cls.get_dynamodb_table()
            table.update_item(**options)

        @classmethod
        def query(cls, data, format=None):
            table_name = 'interest_metadata'
            table = cls.get_dynamodb_table()
            num = random.randint(198,400)
            sort = table.query(
                KeyConditionExpression=Key('categoryid').eq(data.categoryid) & Attr('priority').contains(str(num))
            )

            table_name = 'interest_category'
            table = cls.get_dynamodb_table()
            response = table.query(
                KeyConditionExpression=Key('categoryid').eq(data.categoryid) & Key('priority').eq(sort['Item']['priority'])
            )
            items = len(response)
            rand = random.randint(items)
            return response['Item']['data'][rand]