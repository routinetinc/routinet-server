import boto3
import random
from routine.models import NoSQLBase
class Category(NoSQLBase):
    dynamodb = boto3.resource('dynamodb')
    table_name = 'interest_category'
    def create_category_table(self):
        table = self.dynamodb.create_table(
            TableName = self.table_name,
            KeySchema = [
                {
                    'AttributeName' : 'Categoryid',
                    'KeyType' : 'HASH'
                },
                {
                    'AttributeName' : 'Priority',
                    'KeyType' : 'RANGE'
                }
            ],
            AttributeDefinitions = [
                {
                    'AttributeName' : 'Categoryid',
                    'AttributeType' : 'N'
                },
                {
                    'AttributeName' : 'Priority',
                    'AttributeType' : 'N'
                },
                {
                    'AttributeName' : 'data',
                    'AttributeType' : 'M'
                },
            ],
            ProvisionedThroughput = {
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            }
        )

    def put(self, request, format=None):
        if request.score <= 100: #数値は仮置き
            options = {
                'TableName': self.table_name,
                'Item': {
                    'Categoryid': {'N': ''},
                    'Priority': {'N': '100'},
                    'data': {'M': request.data}
                }
            }

        elif 100 < request.score <=200:
            options = {
                'TableName': self.table_name,
                'Item': {
                    'Categoryid': {'N': ''},
                    'Priority': {'N': '110'},
                    'data': {'M': request.data}
                }
            }

        else:
            num = random.randint(200,300)
            options = {
                'TableName': self.table_name,
                'Item': {
                    'Categoryid': {'N': ''},
                    'Priority': {'N': f'{num}'},
                    'data': {'M': request.data}
                }
            }

        self.dynamodb.put_item(**options)
    
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