from rest_framework.views import APIView
from auths.utils.funcs import get_tokens_for_user
from auths.utils.handle_json import make_response
from auths.models import User
    
class GetToken(APIView):
    def post(self, request, format=None):
        user_id = 1 if(request.user.id is None) else request.user.id
        user = User.objects.get(id=user_id)
        tokens = get_tokens_for_user(user)
        
        return make_response(data=tokens)