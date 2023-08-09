import json
from django.http import JsonResponse
from rest_framework import serializers
from django.http import HttpRequest
TwoSpaces = "  "
RED = '\033[91m'
END = '\033[0m'


class RequestInvalid(Exception):  
    def __init__(self, error_messages: str):
        self.error_messages = error_messages
    def __str__(self):
        formatted_messages = self.error_messages
        return f'\n{RED}{formatted_messages}{END}'    

def get_json(request: HttpRequest, serializer_type: serializers.Serializer):
    datas = json.loads(request.body)
    serializer: serializers.Serializer = serializer_type(data=datas['data'])
    if serializer.is_valid():
        return serializer.validated_data  
    else:
        error_messages = serializer.errors
        error_message = ''
        for field, errors in error_messages.items():
            field_errors = [f'{TwoSpaces}{field}: {error}' for error in errors]
            error_message += '\n'.join(field_errors) + '\n'
        print(error_messages)
        raise RequestInvalid(f'{error_message}')

def make_response(status_code:int = 1, data:dict = {}):
    response_dic = {} 
    response_dic['status_code'] = status_code
    response_dic['data'] = data
    response = JsonResponse(response_dic)
    return response