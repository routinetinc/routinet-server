from rest_framework.views import APIView
from auths.utils.funcs import get_tokens_for_user
from auths.utils.handle_json import make_response
from auths.models import User
from rest_framework.permissions import IsAuthenticated
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
    
class GetToken(APIView):
    def post(self, request, format=None):
        #user = User.objects.create_user("huku","email","password")
        cred = credentials.Certificate('kgavengers-firebase-adminsdk-7s1fl-0fd3d6ec82.json')
        firebase_admin.initialize_app(cred)
        
        id_token = request.data.get('id_token')
        decoded_token = auth.verify_id_token(id_token)
        email = decoded_token['email']
        name  = decoded_token['name']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create_user(name,email,"password")
        tokens = get_tokens_for_user(user)
        
        return make_response(data=tokens)
    
class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, format=None):
        user = request.user
        print(user)
        return make_response(data = {"username": user.username})