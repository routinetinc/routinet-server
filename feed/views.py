from feed.models import Cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers

from .user_actions import TaskFinish
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
    


class TaskCompleteLikeSerializer(serializers.Serializer):
    task_record_id = serializers.IntegerField()

class TaskCompleteLike(APIView):
    def post(self, request):
        serializer = None
        data = request.data.get('data')
        print("Request data:", request.data)

        if not data:
            return Response({"error": "Missing 'data' key in request", "status_code": 400}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TaskCompleteLikeSerializer(data=data)
        print("Serializer created:", serializer)

        if serializer.is_valid():
            print("Validated data:", serializer.validated_data)
        else:
            print("Serializer errors:", serializer.errors)

        # if not serializer.is_valid():
        #     print(data)
        #     print("Serializer errors:", serializer.errors)
        #     return Response({"errors": serializer.errors, "status_code": 400}, status=status.HTTP_400_BAD_REQUEST)

        task_record_id = serializer.validated_data.get("task_record_id")
        if task_record_id is None:
            return Response({"error": "task_record_id not present in validated data"}, status=status.HTTP_400_BAD_REQUEST)


        # Assuming a method to get the logged-in user's ID
        # This is just a placeholder and should be replaced by the actual method to get the user's ID
        user_id = 1

        # Use the get_neo4j_session method to get a Neo4j session
        try:
            with neo4j_session:
                # Use the create_likes_feed_post method within the session context
                TaskFinish.Relation.create_likes_task_finish(neo4j_session, user_id, task_record_id)
        except Exception as e:
            return Response({"error": f"Neo4j error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        return Response({"status_code": 1, "data": {"task_record_id": task_record_id}}, status=status.HTTP_200_OK)
