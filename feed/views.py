from feed.models import Cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

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

# feed/views.py
from django.shortcuts import render
from django.http import JsonResponse
import os
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import os

def upload_image(request):
    if request.method == "POST" and request.FILES.get("image"):
        uploaded_image = request.FILES["image"]
        # 画像の拡張子を取得
        file_extension = os.path.splitext(uploaded_image.name)[-1].lower()
        # 保存先のパスを指定
        save_path = os.path.join("media", uploaded_image.name)

        with open(save_path, "wb") as destination:
            for chunk in uploaded_image.chunks():
                destination.write(chunk)

        # 画像のURLをフロントエンドに返す
        image_url = os.path.join("/media/", uploaded_image.name)
        return JsonResponse({"image_url": image_url})

    return JsonResponse({"error": "Invalid request"})


def display_image(request, image_name):
    # 画像のフルパスを取得
    image_path = os.path.join(settings.MEDIA_ROOT, image_name)

    # 画像が存在するか確認
    if os.path.exists(image_path):
        with open(image_path, 'rb') as image_file:
            response = HttpResponse(image_file.read(), content_type="image/jpeg")  # 画像のMIMEタイプに合わせて調整
        return response
    else:
        return HttpResponse("Image not found", status=404)


