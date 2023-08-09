import time

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