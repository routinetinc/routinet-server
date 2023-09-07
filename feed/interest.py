import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class GetTags(APIView):
    def post(self, request, format=None):
        try:
            datas = json.loads(request.body)
        except json.JSONDecodeError:
            return Response({'error': 'Invalid JSON format'}, status=status.HTTP_400_BAD_REQUEST)
        
        tag_ids = datas.get('tag_ids', None)
        
        if tag_ids is None:
            return Response({'error': 'tag_ids key is missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'tag_ids': tag_ids}, status=status.HTTP_200_OK)
