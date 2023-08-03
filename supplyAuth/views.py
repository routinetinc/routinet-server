from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from social_django.utils import psa

from requests.exceptions import HTTPError
import requests
from supplyAuth.models import User


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
 
class Getemail(APIView):
    def get(self, request, format=None, **kwargs):
        print("ここ")
        print(kwargs)
        return Response('hello')

def get_user(backend, user, response, *args, **kwargs):
    if user:
        return
    if backend.name == 'google-oauth2':
        if kwargs['uid']:
            try:
                user = User.objects.get(email = kwargs['uid']) 
            except User.DoesNotExist:
                user = None
        return {'user':user}
            
        
def save_profile(backend, user, response, *args, **kwargs):
    if backend.name == 'google-oauth2':
        if not user:
            print(f"ユーザ：{user}")
            # 新規ユーザ作成
            print(kwargs['uid'])
            print(kwargs)
            user = User.objects.create_user(email=kwargs['details']['email'],username=kwargs['details']['fullname'],password="a")
            return {'is_new': False,'user':user}
        else:
            print(f"ユーザ：{user}")
            """ social = user.social_auth.get(provider='google-oauth2')
            social.extra_data['access_token'] """