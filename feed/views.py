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
from .models import FeedPostComment as feedpostcomment, FeedPost as feedpost
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
    


class FeedPostCommentSerializer(serializers.Serializer):
    post_id = serializers.IntegerField(max_value=None, min_value=None)
    comment = serializers.CharField(max_length=400)

class CommentUserSerializer(serializers.Serializer):
    comment_id = serializers.IntegerField(source='id')
    user_id = serializers.IntegerField(source='feed_post_id.user.id')
    profile_media_id = serializers.IntegerField(source='feed_post_id.user.profile_media_id')
    username = serializers.CharField(source='feed_post_id.user.username')
    comment = serializers.CharField()
    content_media_id = serializers.IntegerField(allow_null=True, required=False, source='media_id')
    post_time = serializers.DateTimeField()
    like_num = serializers.IntegerField()


class FeedPostComment(APIView):
    def get(self, request):
        # Assume feed_post_id
        feed_post_id = 1

        # Retrieve FeedPostComment instances associated with the given feed_post_id
        comments = feedpostcomment.objects.filter(feed_post_id=feed_post_id)

        # Serialize the comments
        serializer = CommentUserSerializer(comments, many=True)

        return make_response(status_code=1, data={"comment_list": serializer.data})
    
    def post(self, request, format=None):
        data = get_json(request, FeedPostCommentSerializer)

        # Debug print
        print("Received data:", data)

        feed_post = feedpost.objects.get(id=data['post_id'])            

        # Debug print
        print("Fetched feed_post:", feed_post)

        # Save the comment
        comment = feedpostcomment(
            feed_post_id=feed_post, 
            comment=data['comment'],
            post_time=timezone.now()  # Set the post_time to the current time
        )
        comment.save()

        # Debug print
        print("Created comment:", comment)

        # Return the comment ID in the response
        return make_response(status_code=1, data={"content_id": comment.pk})
