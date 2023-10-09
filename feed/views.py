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
        img = data['image']

        # 画像を保存
        (_ := models.Image(img=img)).save()

        return make_response(1)

    def get(self, request, *args, **kwargs):
        img_id = request.GET.get('media_id', None)
        if img_id is None:
            return make_response(400)
        img = models.Image.objects.get(id=img_id)

        # Base64 エンコード (∵ バイナリデータの変換後のサイズは base85 と大きく差異がないが変換速度やセキュリティ要件は base64 が勝るため) 
        buffered = io.BytesIO()                                     # バイトデータをメモリ内のバッファに書き込むための一時的なストリームを作成
        img.save(buffered, format='JPEG')                           # JPEG 形式でエンコードし img を JPEG 形式で保存し buffered に書き込み
        img_str = base64.b64encode(buffered.getvalue()).decode()    # Base64 エンコードし、エンコード後のバイト文字列を通常の文字列に変換 (.decode())

        return make_response(1, data={'img_by_base64': img_str})
