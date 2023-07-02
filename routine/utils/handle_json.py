import json

def get_json(request,serializer_type):
    datas = json.loads(request.body)
    serializer = serializer_type(data=datas["data"])
    if serializer.is_valid():
        return serializer.validated_data
        
    else:
        print(serializer.errors)