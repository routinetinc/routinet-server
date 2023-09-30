from feed.models import Cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers

from .user_actions import TaskFinish
from .utils.graph_db.connections import neo4j_session
from routine.utils.handle_json import RequestInvalid, get_json, make_response


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
        try:
            datas: dict = get_json(request, TaskCompleteLikeSerializer)
        except RequestInvalid as e:
            return make_response(status_code=400)

        serializer = TaskCompleteLikeSerializer(data=datas)

        task_record_id = datas["task_record_id"]
        print(f"task_record_id:{task_record_id}")

        user_id = 1

        try:
            with neo4j_session:
                # Use the create_likes_feed_post method within the session context
                TaskFinish.Relation.create_likes_task_finish(neo4j_session, user_id, task_record_id)
        except Exception as e:
            return Response({"error": f"Neo4j error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        return make_response(data=datas)
