import secret


class CustomError():
    class KeyInvalidValue(Exception):
        pass
    class UserTaskTypeError(Exception):
        pass


# ユーザキャッシュについてデータベース操作をバッチ処理するための個々のタスク定義
class UserTask():
    class Delete():
        def __init__(self, content_ids:list):
            self.content_ids = content_ids
        def create_update_expression(self, expression_attribute_names):
            update_expression = ""
            for i in range(len(self.content_ids)):
                update_expression += f"datas.#delete{str(i)}, "
                expression_attribute_names[f"#delete{i}"] = str(self.content_ids[i])
            return update_expression
    class Add():
        def __init__(self, content_ids, priorities):
            self.content_ids = content_ids
            self.priorities = priorities
        def create_update_expression(self, expression_attribute_names, expression_attribute_values):
            update_expression = ""
            for i in range(len(self.content_ids)):
                update_expression += f"datas.#add{str(i)} = :add{str(i)}, "
                expression_attribute_names[f"#add{i}"] = str(self.content_ids[i])
                expression_attribute_values[f":add{str(i)}"] = str(self.priorities[i])
            return update_expression
    class Update():
        def __init__(self, content_ids, priorities):
            self.content_ids = content_ids
            self.priorities = priorities
        def create_update_expression(self, expression_attribute_names, expression_attribute_values):
            update_expression = ""
            for i in range(len(self.content_ids)):
                update_expression += f"datas.#update{str(i)} = :update{str(i)}, "
                expression_attribute_names[f"#update{str(i)}"] = str(self.content_ids[i])
                expression_attribute_values[f":update{str(i)}"] = str(self.priorities[i])
            return update_expression


class NoSQLBase():
    table_name = ''
        
    class Meta:
        abstract = True

    @classmethod
    def get_dynamodb_table(self):
        session  = secret.BOTO3_SESSION
        dynamodb = session.resource('dynamodb')
        return dynamodb.Table(self.table_name)
    
    @classmethod
    def get_dynamodb_client(self):
        session = secret.BOTO3_SESSION
        client  = session.client('dynamodb')
        return client
    
    @classmethod
    def make_keys(cls, attribute:str, values:list)->list:
        setthing_type = None
        if type(values[0])==str:
            setthing_type = 'S'
        if type(values[0])==int:
            setthing_type = 'N'
            tmp = [str(value) for value in values]
            values = tmp
        if setthing_type==None:
            raise CustomError.KeyInvalidValue
        keys = []
        for value in values:
            keys.append(
                {
                    attribute: {
                        setthing_type:value,
                    }
                }
            )
        return keys
    
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
    def batch_get(cls, key_attribute:str, key_values:list):
        keys = cls.make_keys(key_attribute, key_values)
        client = cls.get_dynamodb_client()
        response =  client.batch_get_item(RequestItems={
                    cls.table_name: {
                        'Keys': keys
                    }
                })
        return response["Responses"][f"{cls.table_name}"]
    
    """ @classmethod
    def batch_delete(cls, key_attribute:str, key_values:list):
        keys = cls.make_keys(key_attribute, key_values)
        client = cls.get_dynamodb_client()
        response =  client.batch_get_item(RequestItems={
                    cls.table_name: {
                        'Keys': keys
                    }
                })
        return response """
    
    @classmethod
    def delete(cls, key):
        table = cls.get_dynamodb_table()
        table.delete_item(Key=key)