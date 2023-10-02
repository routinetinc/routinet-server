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

import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
from io import BytesIO
from django.shortcuts import render

from django.http import JsonResponse
from django.views import View
from PIL import Image
import os

class UploadImageView(View):
    @csrf_exempt
    def post(self, request):
        if request.FILES.get('image'):
            uploaded_image = request.FILES['image']
            # Save the uploaded image to the backend server
            fs = FileSystemStorage()
            filename = fs.save(uploaded_image.name, uploaded_image)
            # Determine the file extension
            _, file_extension = os.path.splitext(filename)
            # Check if encoding is needed (for example, convert to PNG)
            encoded_image_url = ''
            if file_extension.lower() not in ['.png', '.jpeg', '.jpg', '.gif']:
                with Image.open(settings.MEDIA_ROOT + '/' + filename) as img:
                    img = img.convert('RGB')
                    encoded_image_buffer = BytesIO()
                    img.save(encoded_image_buffer, format='PNG')
                    encoded_image_name = fs.save(uploaded_image.name.split('.')[0] + '.png', encoded_image_buffer)
                    encoded_image_url = fs.url(encoded_image_name)
            else:
                encoded_image_url = fs.url(filename)
            return JsonResponse({'image_url': encoded_image_url})

        return JsonResponse({'error': 'Image upload failed'})

    def get(self, request):
        return render(request, 'upload_form.html')



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


