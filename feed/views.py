from feed.models import Cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from run.management.commands import graph_db
from routine.utils.handle_json import make_response

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
    
class Follow_related(APIView):
    def get(self, request, format=None):
        from_user_id = request.GET.get('user_id')
        with graph_db.neo4j_session as session:
            (_ :=graph_db.User()).read_follows_user_ids(session, from_user_id)

    def post(self, request, format=None):
        with graph_db.neo4j_session as session:
            (_ :=graph_db.User.Relation()).create_follows_user(session, request.from_user_id, request.data.to_user_id)
        make_response(status_code=1,data={'to_user_id':request.data.to_user_id})

    def delete(self, request, format=None):
        with graph_db.neo4j_session as session:
            (_ :=graph_db.User.Relation()).delete_follows_user(session, request.data.from_user_id, request.data.to_user_id)

class Follower_related(APIView):
    def get(self, request, format=None):
        from_user_id = request.GET.get('user_id')
        with graph_db.neo4j_session as session:
            (_ :=graph_db.User()).read_followed_user_ids(session, from_user_id)