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


class FeedPostComment(APIView):
    def get(self, request, format=None):
        pass
    
    def post(self, request, format=None):
        try:
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
            return make_response(status_code=1, data={"post_id": comment.pk})

        except feedpost.DoesNotExist:
            # Debug print
            print("Error: FeedPost does not exist.")
            return make_response(status_code=400, data={"error": "FeedPost does not exist."})
        except Exception as e:
            # Debug print
            print("Error:", str(e))
            return make_response(status_code=500, data={"error": str(e)})
