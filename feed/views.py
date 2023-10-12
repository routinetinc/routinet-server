from feed.models import Cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from django.http import HttpRequest
import json
from django.utils import timezone

from feed.user_actions import TaskFinishComment, FeedPost
from .utils.graph_db.connections import neo4j_session
from routine.utils.handle_json import *
from .models import FeedPostComment as feedpostcomment, FeedPost as feedpost, Tag
from supply_auth.models import *


class Hello(APIView):
    def get(self, request, format=None):
        Item = {'user_id': 3, 'created': '2023-08-26','data':{'task_record_id':4}}
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
    
class TaskCompleteCommentLikeSerializer(serializers.Serializer):
    task_finish_comment_id = serializers.IntegerField()

class TaskFinishCommentLike(APIView):
    def get(self, request):
        # Assume content_id
        task_finish_id = 1

        try:
            with neo4j_session:
                # Retrieve user IDs who liked the specific post
                user_ids = (_ := TaskFinishComment()).read_liked_user_ids(neo4j_session, task_finish_id)
        except Exception as e:
            return make_response(status_code=500, data={"error": str(e)})
        
        print(user_ids)

        # Fetch users from the relational database based on the IDs retrieved from Neo4j
        users_db = User.objects.filter(pk__in=user_ids)

        print(users_db)

        user_list = []
        for user in users_db:
            user_tags = Tag.objects.filter(id__in=user.tag_ids)
            tag_list = [{"id": tag, "name": tag.name} for tag in user_tags]

            user_data = {
                "user_id": user.username,  # Adjust based on your data model
                "profile_media_id": user.profile_media_id,
                "name": user.username,
                "self_introduction": user.self_introduction,
                "hot_user": user.is_hot_user,
                "tags": tag_list
            }
            user_list.append(user_data)

        return make_response(status_code=1, data={"user_list": user_list})
    
    def post(self, request):
        serializer = None
        try:
            datas: dict = get_json(request, TaskCompleteCommentLikeSerializer)
        except RequestInvalid as e:
            return make_response(status_code=400)

        serializer = TaskCompleteCommentLikeSerializer(data=datas)

        task_finish_comment_id = datas["task_finish_comment_id"]
        print(f"task_finish_comment_id:{task_finish_comment_id}")

        user_id = 1

        try:
            with neo4j_session:
                # Use the create_likes_feed_post method within the session context
                TaskFinishComment.Relation().create_likes_task_finish_comment(neo4j_session, user_id, task_finish_comment_id)
                print("ok")
        except Exception as e:
            print("not ok")
            return make_response(status_code=500, data={"error": str(e)})


        return make_response(status_code=1, data=datas)        

