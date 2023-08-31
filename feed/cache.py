from feed.models import Cache
from django.core.cache import cache
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .ff_related import Node  # ff_related.pyからNodeクラスをインポート
from .models import FeedPost, FeedPostComment  # models.pyから必要なモデルをインポート

def calculate_priority_score(follower_count, like_count, comment_count, reply_to_reply_count, has_media, has_challenge):
    # 基本のスコアを計算
    base_score = (follower_count * 0.5) + like_count + (comment_count * 50) + (reply_to_reply_count * 150)
    
    # メディアがあればスコアを2倍
    if has_media:
        base_score *= 2
    
    # チャレンジを引用していればスコアを1.5倍
    if has_challenge:
        base_score *= 1.5
    
    return base_score

class PriorityScore(APIView):
    def get(self, request, format=None):
        user_id = 3  # この例では仮に3としています

        # フォロワー数を取得
        follower_ids = Node.UserFF.read_follower_ids(user_id)
        follower_count = len(follower_ids)

        # いいね数、コメント数、メディア有無、チャレンジ有無をFeedPostモデルから取得
        try:
            feed_post = FeedPost.objects.get(user_id=user_id)  # 仮にuser_idで検索
            like_count = feed_post.good_num
            comment_count = FeedPostComment.objects.filter(feed_post=feed_post).count()
            has_media = feed_post.media_id is not None
            has_challenge = feed_post.challenge is not None
        except FeedPost.DoesNotExist:
            # このユーザーのFeedPostが存在しない場合
            return Response({'error': 'FeedPost does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # リプライへのリプライ数は、仮に0とします（このデータがない場合）
        reply_to_reply_count = 0

        # 優先スコアを計算
        priority_score = calculate_priority_score(follower_count, like_count, comment_count, reply_to_reply_count, has_media, has_challenge)

        # DynamoDBに優先スコアを保存
        item = {
            'user_id': user_id,
            'created': '2023-08-26',  # この値も適当に設定しています
            'data': {
                'priority_score': priority_score,
                'content_id': 1234  # 仮のコンテンツID
            }
        }
        Cache.User.create(Item=item)

        # フォロワーのキャッシュに優先スコアを保存（1週間のタイムアウト）
        for follower_id in follower_ids:
            cache_key = f'priority_score_for_follower_{follower_id}'
            cache.set(cache_key, priority_score, timeout=60 * 60 * 24 * 7)  # 1週間

        return Response({'priority_score': priority_score}, status=status.HTTP_200_OK)
