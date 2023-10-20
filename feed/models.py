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
        
        def __create_complete_setting(tasks:list)->str:
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
            expression_attribute_names  = {}
            expression_attribute_values = {}
            
            # SETコマンドでAddタスクとUpdateタスクを登録
            if sets:
                update_expression += "SET "
                for set in sets:
                    update_expression += set.create_update_expression(expression_attribute_names, expression_attribute_values)
                update_expression = update_expression[:-2] + " "

                
            # REMOVEコマンドでDeleteタスクを登録
            if deletes:
                update_expression += "REMOVE "
                for delete in deletes:
                    update_expression += delete.create_update_expression(expression_attribute_names)
                update_expression = update_expression[:-2] + " "
            
            print(update_expression)
            print(expression_attribute_names)
            print(expression_attribute_values)
            return update_expression, expression_attribute_names, expression_attribute_values
        
        @classmethod
        def create_new_record(cls, user_id):
            Item = {'user_id': user_id, 'datas':{}}
            cls.create(Item=Item)
        
        @classmethod
        def execute(cls, user_id:int, tasks:list):
            table = cls.get_dynamodb_table()
            settings = cls.__create_complete_setting(tasks)
            if settings[2]:
                response = table.update_item(
                    Key={
                        'user_id': user_id
                    },
                    UpdateExpression          = settings[0],
                    ExpressionAttributeNames  = settings[1],
                    ExpressionAttributeValues = settings[2]
                )
            else:
                response = table.update_item(
                    Key={
                        'user_id': user_id
                    },
                    UpdateExpression          = settings[0],
                    ExpressionAttributeNames  = settings[1],
                )
    
    class InterestCAT(NoSQLBase):
        time = datetime.datetime.now().isoformat()
        @classmethod
        def create_meta(cls, data, format=None):
            cls.table_name = 'priority_metadata'
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
            cls.table_name = 'interest_category'
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
                'data': [
                    {
                        'contentid': data.contentid,
                        'priority': data.score
                    }
                ]
            }
            table = cls.get_dynamodb_table()
            table.put_item(Item=Item)
        
        @classmethod
        def put(cls, data, format=None):
            #　ソートキーの取得
            if data.score <= 100: #数値は仮置き
                string = 'a198'

            elif 100 < data.score <=200:
                string = 'a199'

            else:
                num = random.randint(200,400)
                cls.table_name = 'priority_metadata'
                table = cls.get_dynamodb_table()
                sort = table.query(
                    KeyConditionExpression=Key('categoryid').eq(data.categoryid)
                )
                string = ''
                for e in sort['Items'][0]['priority']:
                    if str(num) in e:
                        string = e
                        break

            #　データの追加
            options = {
                'Key': {
                    'categoryid': data.categoryid,
                    'priority': string,
                },
                'UpdateExpression': 'set #data = list_append(#data, :add), #li_contentid = list_append(li_contentid, :li_add), #time = :now',
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
            cls.table_name = "interest_category"
            table = cls.get_dynamodb_table()
            table.update_item(**options)

            #　データ量が多ければ分割
            if string != 'a198' and string != 'a199' and len(sort['Items'][0]['data']) >= 10: #値は仮置き
                cls.divide(data=data, string=string)
            

        @classmethod
        def update(cls, data, format=None):
            #ソートキーの取得
            cls.table_name = 'interest_category'
            table = cls.get_dynamodb_table()
            sort = table.query(
                KeyConditionExpression=Key('categoryid').eq(data.categoryid),
                FilterExpression=Attr('li_contentid').contains(data.contentid)
            )
            num = sort['Items'][0]['li_contentid'].index(data.contentid)
            string = sort['Items'][0]['priority']
            if data.score > 100 and string == 'a198':
                # 元データの削除
                options = {
                    'Key': {
                        'categoryid': data.categoryid,
                        'priority': 'a198',
                    },
                    'UpdateExpression': f'remove #data[{num}], #li_contentid[{num}])',
                    'ExpressionAttributeNames': {'#data': 'data'},
                }
                table.update_item(**options)

                # 新データの追加
                options = {
                    'Key': {
                        'categoryid': data.categoryid,
                        'priority': 'a199',
                    },
                    'UpdateExpression': 'set #data = list_append(#data, :add), #li_contentid = list_append(li_contentid, :li_add), #time = :now',
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
                #　元データの削除
                options = {
                    'Key': {
                        'categoryid': data.categoryid,
                        'priority': 'a199',
                    },
                    'UpdateExpression': f'remove #data[{num}], #li_contentid[{num}])',
                    'ExpressionAttributeNames': {'#data': 'data','#li_contentid': 'li_contentid'},
                }
                table.update_item(**options)

                #　新データの追加
                num = random.randint(200,400)
                cls.table_name = 'priority_metadata'
                table = cls.get_dynamodb_table()
                sort = table.query(
                    KeyConditionExpression=Key('categoryid').eq(data.categoryid)
                )
                for e in sort['Items'][0]['priority']:
                    if str(num) in e:
                        string = e
                        break
                cls.table_name = 'interest_category'
                table = cls.get_dynamodb_table()
                options = {
                    'Key': {
                        'categoryid': data.categoryid,
                        'priority': string,
                    },
                    'UpdateExpression': 'set #data = list_append(#data, :add), #li_contentid = list_append(li_contentid, :li_add), #time = :now',
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
                #　元データの削除
                options = {
                    'Key': {
                        'categoryid': data.categoryid,
                        'priority': string,
                    },
                    'UpdateExpression': f'remove #data[{num}], #li_contentid[{num}]',
                    'ExpressionAttributeNames': {'#data': 'data','#li_contentid': 'li_contentid'}
                }
                table.update_item(**options)

                #　新データの追加
                options = {
                    'Key': {
                        'categoryid': data.categoryid,
                        'priority': string,
                    },
                    'UpdateExpression': 'set #data = list_append(#data, :add), #li_contentid = list_append(li_contentid, :li_add), #time = :now',
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
            
            #　データ量が多ければ分割
            if string != 'a198' and string != 'a199' and len(sort['Items'][0]['data']) >= 10: #値は仮置き
                cls.divide(data=data, string=string)

        @classmethod
        def divide(cls, data, string, format=None):
            #　メタデータの分割
            cls.table_name = 'priority_metadata'
            table = cls.get_dynamodb_table()
            sort = table.query(
                KeyConditionExpression=Key('categoryid').eq(data.categoryid)
            )
            #　入っている順番の取得
            num = 0
            for i,e in enumerate(sort['Items'][0]['priority']):
                if string == e:
                    num = i

            #　分割する境界の設定
            if (int(string[-1]) + int(string[3])) % 2 == 0:
                half = len(string)//2 - 2
            else:
                half = len(string)//2
            #　元データの削除
            options = {
                'Key': {
                    'categoryid': data.categoryid
                },
                'UpdateExpression': f'remove #priority[{num}]',
                'ExpressionAttributeNames': {'#priority': 'priority'}
            }
            table.update_item(**options)
            #　ソートキーの分割
            former = string[:half]
            later = string[half:]
            options = {
                'Key': {
                    'categoryid': data.categoryid
                },
                'UpdateExpression': 'set #priority = list_append(#priority, :add)',
                'ExpressionAttributeNames': {'#priority': 'priority'},
                'ExpressionAttributeValues': {
                    ':add': [former,later]
                }
            }
            table.update_item(**options)

            #　レコードの分割
            cls.table_name = 'interest_category'
            table = cls.get_dynamodb_table()
            sort = table.query(
                KeyConditionExpression=Key('categoryid').eq(data.categoryid) & Key('priority').eq(string)
            )
            #　入っているデータの分割
            half = int(len(sort['Items'][0]['data'])//2)
            data1 = sort['Items'][0]['data'][:half]
            data2 = sort['Items'][0]['data'][half:]
            li1 = sort['Items'][0]['li_contentid'][:half]
            li2 = sort['Items'][0]['li_contentid'][half:]
            #　元レコードの削除
            table.delete_item(
                Key = {
                    'categoryid': data.categoryid,
                    'priority': string
                }
            )
            #　新レコード（二つ）の追加
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
            #　ソートキーの取得
            cls.table_name = 'priority_metadata'
            table = cls.get_dynamodb_table()
            num = random.randint(198,400)
            sort = table.query(
                KeyConditionExpression=Key('categoryid').eq(data.categoryid)
            )
            for e in sort['Items'][0]['priority']:
                if str(num) in e:
                    string = e

            #　データの取得
            cls.table_name = 'interest_category'
            table = cls.get_dynamodb_table()
            response = table.query(
                KeyConditionExpression=Key('categoryid').eq(data.categoryid) & Key('priority').eq(string)
            )
            items = len(response['Items'][0]['data'])
            rand = random.randint(0,items-1)
            print(response['Items'][0]['data'][rand])