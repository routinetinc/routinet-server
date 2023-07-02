import json
from django.http import JsonResponse

def get_json(request,serializer_type):
    datas = json.loads(request.body)
    serializer = serializer_type(data=datas["data"])
    if serializer.is_valid():
        return serializer.validated_data  
    else:
        print(serializer.errors)

def make_response(status_code:int = 1, data:dict ={}):
    response_dic = {} 
    response_dic["status_code"] = status_code
    response_dic["data"] = data
    response = JsonResponse(response_dic)
    return response