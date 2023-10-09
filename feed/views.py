from django.shortcuts import render
from feed.models import Cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views import View
from django.http import HttpResponse
import base64
import io
from PIL import Image
from feed import models, serializers
from routine.utils.handle_json import RequestInvalid, get_json, make_response


class Hello(APIView):
    def get(self, request, format=None):
        Item = {'user_id': 3, 'created': '2023-08-26','data':{'content_id':4}}
        Cache.User.create(Item = Item)
        return Response('hello')
    
class Read(APIView):
    def get(self, request, format=None):
        key = {'user_id':3,
               'created':'2023-08-26'}
        my_model = Cache.User.get(key)
        if my_model:
            print(my_model)
        else:
            print("なし")
        return Response('hello')
    
class Delete(APIView):
    def get(self, request, format=None):
        key = {'user_id':3,
               'created':'2023-08-26'}
        Cache.User.delete(key)
        return Response('hello')
    

#* ---------------------------------------------------

class ImageView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = get_json(request, serializers.Image)
        except RequestInvalid:
            return make_response(status_code=400)
        image = data['image']

        # 画像を処理（ここでは例として画像を開いてすぐ閉じる）
        (_ := models.Image(image=image)).save()

        return HttpResponse('Image received and processed.')

    def get(self, request, *args, **kwargs):
        # ここでは例として黒い10x10ピクセルの画像を作成します
        img = Image.new('RGB', (10, 10))

        # Base64 エンコード (∵ バイナリデータの変換後のサイズは base85 と大きく差異がないが変換速度やセキュリティ要件は base64 が勝るため) 
        buffered = io.BytesIO()                                     # バイトデータをメモリ内のバッファに書き込むための一時的なストリームを作成
        img.save(buffered, format='JPEG')                           # JPEG 形式でエンコードし img を JPEG 形式で保存し buffered に書き込み
        img_str = base64.b64encode(buffered.getvalue()).decode()    # Base64 エンコードし、エンコード後のバイト文字列を通常の文字列に変換 (.decode())

        return render(request, 'image.html', {'image': img_str})
