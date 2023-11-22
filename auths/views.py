from rest_framework.views import APIView
from auths.utils.funcs import get_tokens_for_user
from auths.utils.handle_json import make_response
    
class GetToken(APIView):
    def post(self, request, format=None):
        
        tokens = get_tokens_for_user(user)
        
        return make_response(data=tokens)