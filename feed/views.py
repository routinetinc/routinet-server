from feed.models import Cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from django.http import HttpRequest
import json
from django.utils import timezone

from feed.user_actions import TaskFinish as taskfinish
from .utils.graph_db.connections import neo4j_session
from routine.utils.handle_json import *
from .models import TaskFinishComment as taskfinishcomment
from routine.models import TaskFinish as taskfinish
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
    


class TaskCompleteCommentSerializer(serializers.Serializer):
    task_finish_id = serializers.IntegerField(max_value=None, min_value=None)
    comment = serializers.CharField(max_length=400)

class CommentUserSerializer(serializers.Serializer):
    comment_id = serializers.IntegerField(source='id')
    user_id = serializers.IntegerField(source='task_finish_id.routine_id.user_id.id')
    profile_media_id = serializers.IntegerField(source='task_finish_id.routine_id.user_id.profile_media_id')
    username = serializers.CharField(source='task_finish_id.routine_id.user_id.username')
    comment = serializers.CharField()
    content_media_id = serializers.IntegerField(allow_null=True, required=False, source='media_id')
    post_time = serializers.DateTimeField()
    like_num = serializers.IntegerField()


class TaskCompleteComment(APIView):
    def get(self, request):
        # Assume feed_post_id
        task_finish_id = 1

        # Retrieve FeedPostComment instances associated with the given feed_post_id
        comments = taskfinishcomment.objects.filter(task_finish_id=task_finish_id)

        print(comments)

        # Serialize the comments
        serializer = CommentUserSerializer(comments, many=True)

        # print(serializer)

        return make_response(status_code=1, data={"comment_list": serializer.data})

    def post(self, request, format=None):
        data = get_json(request, TaskCompleteCommentSerializer)

        # Debug print
        print("Received data:", data)

        task_finish = taskfinish.objects.get(id=data['task_finish_id'])            

        # Debug print
        print("Fetched task_finish:", task_finish)

        # Save the comment
        comment = taskfinishcomment(
            task_finish_id=task_finish, 
            comment=data['comment'],
            post_time=timezone.now()  # Set the post_time to the current time
        )
        comment.save()

        # Debug print
        print("Created comment:", comment)

        # Return the comment ID in the response
        return make_response(status_code=1, data={"task_finish_id": comment.pk})
