from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from social_django.utils import psa

from requests.exceptions import HTTPError
import requests


""" @api_view(['POST'])
@permission_classes([AllowAny])
@psa()
def register_by_access_token(request, backend):
    token = request.data.get('access_token')
    user = request.backend.do_auth(token)
    print(request)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                'token': token.key
            },
            status=status.HTTP_200_OK,
            )
    else:
        return Response(
            {
                'errors': {
                    'token': 'Invalid token'
                    }
            },
            status=status.HTTP_400_BAD_REQUEST,
        ) """

@psa('social:complete')
def register_by_access_token(request, backend):
    # This view expects an access_token GET parameter, if it's needed,
    # request.backend and request.strategy will be loaded with the current
    # backend and strategy.
    token = request.GET.get('access_token')
    user = request.backend.do_auth(token)
    if user:
        #login(request, user)
        return 'OK'
    else:
        return 'ERROR'

@api_view(['GET', 'POST'])
def authentication_test(request):
    print(request.user)
    return Response(
        {
            'message': "User successfully authenticated"
        },
        status=status.HTTP_200_OK,
    )
    
class Getemail(APIView):
    def get(self, request, format=None):
        #Item = {'id': 1, 'name': 'MO'}
        #NoSQL.User.create(Item)
        return Response('hello')
    def post(self, request):
        """ parms = {
            'code':<コード>
            'client_id':<クライアントID>
            'client_secret':<クライアントシークレット>
            'redirect_uri':'http://127.0.0.1:8000/auth/login/'
            'grant_type':'authorization_code'
            'access_type':'offline'
        } """
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post('https://www.googleapis.com/oauth2/v4/token', data=parms, headers=headers)
        
def save_profile(backend, user, response, *args, **kwargs):
    if backend.name == 'google-oauth2':
        """ # Googleから取得した情報を使ってユーザーのプロフィールを更新します
        user.details.photo_url = response.get('picture')
        user.profile.locale = response.get('locale')
        user.profile.save() """
        if not user:
            # 新規ユーザ作成
            print(kwargs['details'])