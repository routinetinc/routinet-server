from feed.models import Cache
from qtpy import API
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from feed.models import FeedPost, FeedPostComment
from supplyAuth.models import FeedPost, FeedPostComment, User, Follower  # 適切なモデルをインポート

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
    
class PriorityScore(APIView):
    def get(self, request, format=None):
        key = {'user_id': 3, 'created': '2023-08-26'}
        my_model = Cache.User.get(key)
        
        if my_model:
            feed_post = FeedPost.objects.get(id=my_model.feed_post_id)  # 仮定
            user = User.objects.get(id=my_model.user_id)  # 仮定
            
            # フォロワー数を取得
            follower_count = Follower.objects.filter(following=user).count()
            
            # いいね数を取得
            like_count = feed_post.good_num  # FeedPostモデルにgood_numフィールドがあると仮定
            
            # コメント数を取得
            comment_count = FeedPostComment.objects.filter(feed_post=feed_post).count()
            
            # リプライへのリプライ数を取得（仮定）
            reply_to_reply_count = FeedPostComment.objects.filter(feed_post=feed_post, is_reply_to_reply=True).count()
            
            # メディアが含まれているか
            has_media = bool(feed_post.media_id)
            
            # チャレンジ（コミュニティ）を引用しているか
            has_challenge = bool(feed_post.challenge)
            
            # 優先スコアを計算
            priority_score = (follower_count * 0.5 + like_count + comment_count * 50 + reply_to_reply_count * 150)
            if has_media:
                priority_score *= 2
            if has_challenge:
                priority_score *= 1.5

            return Response({'priority_score': priority_score}, status=status.HTTP_200_OK)
        else:
            return Response('No model found.', status=status.HTTP_404_NOT_FOUND)

