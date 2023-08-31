import time
from django.http import JsonResponse

class MyCustomMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Middlewareの前処理をここに記述する
        # print('Hellow PreProcessor')
        #time.sleep(10)
        # print('Hellow World!')

        response = self.get_response(request)

        # Middlewareの後処理をここに記述する
        # ...

        return response
    
class HandleError:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        data = {"error":f"{exception.__class__.__name__}: {exception}"}
        return JsonResponse(data)