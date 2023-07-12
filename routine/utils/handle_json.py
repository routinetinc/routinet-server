import json
from django.http import JsonResponse
from rest_framework import serializers
from django.http import HttpRequest

class RequestInvalid(Exception):
    pass

def get_json(request: HttpRequest, serializer_type: serializers.Serializer):
    datas = json.loads(request.body)
    serializer = serializer_type(data=datas['data'])
    if serializer.is_valid():
        return serializer.validated_data  
    else:
        # print(f'request の形式などが不適切です。\n詳細: {serializer.errors}\n')
        raise RequestInvalid(f'request の形式などが不適切です。\n詳細: {serializer.errors}\n')

def make_response(status_code:int = 1, data:dict = {}):
    response_dic = {} 
    response_dic['status_code'] = status_code
    response_dic['data'] = data
    response = JsonResponse(response_dic)
    return response