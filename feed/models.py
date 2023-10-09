from django.db import models
import secret
import boto3
import random
import datetime
from boto3.dynamodb.conditions import Key, Attr     
from feed.utils.NoSQL import NoSQLBase, UserTask, CustomError

class Cache():
    class User(NoSQLBase):
        table_name = 'usercache'
        
        class Task(UserTask):
            pass
        
        def __create_complete_update_expression(tasks:list)->str:
            sets    = []
            deletes = []
            for task in tasks:
                if type(task) == UserTask.Add:
                    sets.append(task)
                elif type(task) == UserTask.Update:
                    sets.append(task)
                elif type(task) == UserTask.Delete:
                    deletes.append(task)
                else: raise CustomError.UserTaskTypeError("User.Task.xxxのインスタンス以外のインスタンスは対応しません")
                
            update_expression = ""
            
            # SETコマンドでAddタスクとUpdateタスクを登録
            update_expression += "SET "
            for set in sets:
                update_expression += set.create_update_expression()
                
            # REMOVEコマンドでDeleteタスクを登録
            update_expression += "REMOVE "
            for set in sets:
                update_expression += set.create_update_expression() 
            
            return update_expression
        
        def create_new_record(self):
            pass
        
        @classmethod
        def execute(cls, user_id:int, tasks:list):
            table = cls.get_dynamodb_table()
            response = table.update_item(
                Key={
                    'user_id': user_id
                },
                UpdateExpression=cls.__create_complete_update_expression(tasks),
            )
    
    class InterestCAT(NoSQLBase):
        time = datetime.datetime.now().isoformat()
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
                
            Item = {
                'categoryid': data.categoryid,
                'priority': string,
                'time': cls.time,
                'li_contentid': [data.contentid],
                'data': {
                    {
                        'contentid': data.contentid,
                        'priority': data.score
                    }
                }
            }
            table = cls.get_dynamodb_table()
            table.put_item(Item=Item)
        
        @classmethod
        def put(cls, data, format=None):
            if data.score <= 100: #数値は仮置き
                string = 'a198'

            elif 100 < data.score <=200:
                string = 'a199'

            else:
                num = random.randint(200,400)
                table_name = 'interest_metadata'
                table = cls.get_dynamodb_table()
                sort = table.query(
                    KeyConditionExpression=Key('categoryid').eq(data.categoryid)
                )
                for e in sort['Item']['priority']:
                    if str(num) in e:
                        string = e
                        break
            options = {
                'Key': {
                    'categoryid': data.categoryid,
                    'priority': string,
                },
                'UpdateExpression': 'set #data = list_append(data, :add), #li_contentid = list_append(li_contentid, :li_add), #time = :now',
                'ExpressionAttributeNames': {'#data': 'data', '#li_contentid': 'li_contentid', '#time': 'time'},
                'ExpressionAttributeValues': {
                    ':add': [
                        {
                            data.contentid,
                            data.score
                        }
                    ],
                    ':li_add': [
                        data.contentid
                    ],
                    ':now': cls.time
                }
            }
            table_name = "interest_category"
            table = cls.get_dynamodb_table()
            table.update_item(**options)
            

        @classmethod
        def update(cls, data, format=None):
            table_name = 'interest_category'
            table = cls.get_dynamodb_table()
            sort = table.query(
                KeyConditionExpression=Key('categoryid').eq(data.categoryid),
                FilterExpression=Attr('li_contentid').contains(data.contentid)
            )
            num = sort['Item']['li_contentid'].index(data.contentid)
            string = sort['Item']['priority']
            if data.score > 100 and string == 'a198':
                options = {
                    'Key': {
                        'categoryid': data.categoryid,
                        'priority': 'a198',
                    },
                    'UpdateExpression': f'remove #data[{num}], #li_contentid[{num}])',
                    'ExpressionAttributeNames': {'#data': 'data'},
                }
                table.update_item(**options)
                options = {
                    'Key': {
                        'categoryid': data.categoryid,
                        'priority': 'a199',
                    },
                    'UpdateExpression': 'set #data = list_append(data, :add), #li_contentid = list_append(li_contentid, :li_add), #time = :now',
                    'ExpressionAttributeNames': {'#data': 'data', '#li_contentid': 'li_contentid', '#time': 'time'},
                    'ExpressionAttributeValues': {
                        ':add': [
                            {
                                data.contentid,
                                data.score
                            }
                        ],
                        ':li_add': [
                            data.contentid
                        ],
                        ':now': cls.time
                    }
                }
                table.update_item(**options)

            if data.score > 200 and string == 'a199':
                options = {
                    'Key': {
                        'categoryid': data.categoryid,
                        'priority': 'a199',
                    },
                    'UpdateExpression': f'remove #data[{num}], #li_contentid[{num}])',
                    'ExpressionAttributeNames': {'#data': 'data','#li_contentid': 'li_contentid'},
                }
                table.update_item(**options)
                num = random.randint(200,400)
                table_name = 'interest_metadata'
                table = cls.get_dynamodb_table()
                sort = table.query(
                    KeyConditionExpression=Key('categoryid').eq(data.categoryid)
                )
                for e in sort['Item']['priority']:
                    if str(num) in e:
                        string = e
                        break
                table_name = 'interest_category'
                table = cls.get_dynamodb_table()
                options = {
                    'Key': {
                        'categoryid': data.categoryid,
                        'priority': string,
                    },
                    'UpdateExpression': 'set #data = list_append(data, :add), #li_contentid = list_append(li_contentid, :li_add), #time = :now',
                    'ExpressionAttributeNames': {'#data': 'data', '#li_contentid': 'li_contentid', '#time': 'time'},
                    'ExpressionAttributeValues': {
                        ':add': [
                            {
                                data.content_id,
                                data.score
                            }
                        ],
                        ':li_add': [
                            data.contentid
                        ],
                        ':now': cls.time
                    }
                }
                table.update_item(**options)

            else:
                options = {
                    'Key': {
                        'categoryid': data.categoryid,
                        'priority': string,
                    },
                    'UpdateExpression': f'remove #data[{num}], #li_contentid[{num}])',
                    'ExpressionAttributeNames': {'#data': 'data','#li_contentid': 'li_contentid'}
                }
                table.update_item(**options)
                options = {
                    'Key': {
                        'categoryid': data.categoryid,
                        'priority': string,
                    },
                    'UpdateExpression': 'set #data = list_append(data, :add), #li_contentid = li_append(li_contentid, :li_add), #time = :now',
                    'ExpressionAttributeNames': {'#data': 'data', '#li_contentid': 'li_contentid', '#time': 'time'},
                    'ExpressionAttributeValues': {
                        ':add': [
                            {
                                data.contentid,
                                data.score
                            }
                        ],
                        ':li_add': [
                            data.contentid
                        ],
                        ':now': cls.time
                    }
                }
                table = cls.get_dynamodb_table()
                table.update_item(**options)
            
            if string != 'a198' and string != 'a199' and len(sort['Item']['data']) >= 50: #値は仮置き
                cls.divide(data=data, string=string)

        @classmethod
        def divide(cls, data, string, format=None):
            table_name = 'interest_metadata'
            table = cls.get_dynamodb_table()
            sort = table.query(
                KeyConditionExpression=Key('categoryid').eq(data.categoryid)
            )
            for e, i in enumerate(sort['Item']['priority']):
                if string == e:
                    num = i

            if int(string[-1]) % 2 == 0:
                half = len(string)/2
            else:
                half = len(string)/2 - 2
            options = {
                'Key': {
                    'categoryid': data.categoryid
                },
                'UpdateExpression': f'remove #priority[{num}])',
                'ExpressionAttributeNames': {'#priority': 'priority'}
            }
            table.update_item(**options)
            former = string[:half]
            later = string[half:]
            options = {
                'Key': {
                    'categoryid': data.categoryid
                },
                'UpdateExpression': 'set #priority = list_append(priority, :add)',
                'ExpressionAttributeNames': {'#priority': 'priority'},
                'ExpressionAttributeValues': {
                    ':add': [former,later]
                }
            }

            table_name = 'interest_category'
            table = cls.get_dynamodb_table()
            sort = table.query(
                KeyConditionExpression=Key('contentid').eq(data.categoryid) & Key('contentid').eq(data.contentid)
            )
            half = int(len(sort['Item']['data'])/2)
            data1 = sort['Item']['data'][:half]
            data2 = sort['Item']['data'][half:]
            li1 = sort['Item']['li_contentid'][:half]
            li2 = sort['Item']['li_contentid'][half:]
            table.delete_item(
                Key = {
                    'categoryid': data.categoryid,
                    'priority': string
                }
            )
            Item = {
                'categoryid': data.categoryid,
                'priority': former,
                'time': cls.time,
                'li_contentid': li1,
                'data': data1
            }
            table.put_item(Item=Item)
            Item = {
                'categoryid': data.categoryid,
                'priority': later,
                'time': cls.time,
                'li_contentid': li2,
                'data': data2
            }
            table.put_item(Item=Item)

        @classmethod
        def query(cls, data, format=None):
            table_name = 'interest_metadata'
            table = cls.get_dynamodb_table()
            num = random.randint(198,400)
            sort = table.query(
                KeyConditionExpression=Key('categoryid').eq(data.categoryid)
            )
            for e in sort['Item']['priority']:
                if str(num) in e:
                    string = e
            table_name = 'interest_category'
            table = cls.get_dynamodb_table()
            response = table.query(
                KeyConditionExpression=Key('categoryid').eq(data.categoryid) & Key('priority').eq(string)
            )
            items = len(response['Item']['data'])
            rand = random.randint(items)
            return response['Item']['data'][rand]