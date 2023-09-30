from feed.models import Cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers

from .user_actions import FeedPost
from .utils.graph_db.connections import neo4j_session
from routine.utils.handle_json import *


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
    


class PostLikeSerializer(serializers.Serializer):
    content_id = serializers.IntegerField()

class PostLike(APIView):
    def post(self, request):
        serializer = None
        try:
            datas: dict = get_json(request, PostLikeSerializer)
        except RequestInvalid as e:
            return make_response(status_code=400)

        serializer = PostLikeSerializer(data=datas)

        content_id = datas["content_id"]
        print(f"content_id:{content_id}")

        user_id = 1

        try:
            with neo4j_session:
                # Use the create_likes_feed_post method within the session context
                FeedPost.Relation.create_likes_feed_post(neo4j_session, user_id, content_id)
        except Exception as e:
            return Response({"error": f"Neo4j error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        return make_response(data=datas)