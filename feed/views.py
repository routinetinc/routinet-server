from feed.models import Cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers

from .user_actions import FeedPost
from .utils.graph_db.connections import neo4j_session


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
    def get(self, request):
        content_id = request.GET.get('id')
        if not content_id:
            return Response({"status_code": 400, "error": "content_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Assuming a method `get_users_liking_post` exists in FeedPost or related model
        users = FeedPost.get_users_liking_post(content_id)
        
        user_list = []
        for user in users:
            user_data = {
                "user_id": user.id,
                "profile_media_id": user.profile_media_id,
                "name": user.name,
                "self_introduction": user.self_introduction,
                "hot_user": user.hot_user,
                "tags": [{"id": tag.id, "name": tag.name} for tag in user.tags]
            }
            user_list.append(user_data)
        
        return Response({"status_code": 1, "data": {"user_list": user_list}}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = None
        data = request.data.get('data')
        print("Request data:", request.data)

        if not data:
            return Response({"error": "Missing 'data' key in request", "status_code": 400}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PostLikeSerializer(data=data)
        print("Serializer created:", serializer)

        if serializer.is_valid():
            print("Validated data:", serializer.validated_data)
        else:
            print("Serializer errors:", serializer.errors)

        # if not serializer.is_valid():
        #     print(data)
        #     print("Serializer errors:", serializer.errors)
        #     return Response({"errors": serializer.errors, "status_code": 400}, status=status.HTTP_400_BAD_REQUEST)

        content_id = serializer.validated_data.get("content_id")
        if content_id is None:
            return Response({"error": "content_id not present in validated data"}, status=status.HTTP_400_BAD_REQUEST)


        # Assuming a method to get the logged-in user's ID
        # This is just a placeholder and should be replaced by the actual method to get the user's ID
        user_id = 1

        # Use the get_neo4j_session method to get a Neo4j session
        try:
            with neo4j_session:
                # Use the create_likes_feed_post method within the session context
                FeedPost.Relation.create_likes_feed_post(neo4j_session, user_id, content_id)
        except Exception as e:
            return Response({"error": f"Neo4j error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        return Response({"status_code": 1, "data": {"content_id": content_id}}, status=status.HTTP_200_OK)
