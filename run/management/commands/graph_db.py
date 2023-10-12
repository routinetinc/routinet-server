import random
from feed.user_actions import FeedPost
from neo4j import Session, Transaction
from feed.ff_related import User
from feed.user_actions import FeedPost, TaskFinish, Routine, FeedPostComment, TaskFinishComment
from django.core.management.base import BaseCommand
from feed.utils.graph_db.connections import neo4j_session
import cProfile

# Neo4jで使用する関数を持つクラス
class _Neo4jTest:
    @staticmethod
    def _delete_all(session: Session) -> None:
        """ 全ノード削除を実行(テストデータの初期化) """
        # ノードのラベルを全種類取得する関数
        def _tx_get_node_labels(tx: Transaction):
            cypher = 'MATCH (n) UNWIND labels(n) AS label RETURN DISTINCT label'
            result = tx.run(cypher)
            return [record['label'] for record in result]
        # あるラベルのノードを全て削除する関数
        def _tx_delete_nodes_with_label(tx: Transaction, node_label: str):
            cypher = f'MATCH (u:{node_label}) DETACH DELETE u'
            tx.run(cypher)
        # ラベルを一括取得
        labels = session.execute_read(_tx_get_node_labels)
        # ラベルごとにノードを削除
        for node_label in labels:
            session.execute_write(_tx_delete_nodes_with_label, node_label)
    @staticmethod
    def _duplicate_create(session: Session) -> None:
        (_ := User()).create(session, 1)
        (_ := Routine()).create(session, 1)
        (_ := TaskFinish()).create(session, 1)
        (_ := FeedPost()).create(session, 1)
    @staticmethod
    def _create_and_duplicate_delete_edge(session: Session) -> None:
        """ 作ったエッジが消せるかどうか。重複して消すことがないか。 """
        (_ := User.Relation()).create_follows_user(session, 1, 2)
        (_ := User.Relation()).delete_follows_user(session, 1, 2)
        (_ := User.Relation()).delete_follows_user(session, 1, 2)
        (_ := User.Relation()).create_likes_feed_post(session, 1, 2)
        (_ := User.Relation()).delete_likes_feed_post(session, 1, 2)
        (_ := User.Relation()).delete_likes_feed_post(session, 1, 2)
        (_ := User.Relation()).create_likes_task_finish(session, 1, 2)
        (_ := User.Relation()).delete_likes_task_finish(session, 1, 2)
        (_ := User.Relation()).delete_likes_task_finish(session, 1, 2)
        (_ := User.Relation()).create_bookmarks_routine(session, 1, 2)
        (_ := User.Relation()).delete_bookmarks_routine(session, 1, 2)
        (_ := User.Relation()).delete_bookmarks_routine(session, 1, 2)
        (_ := Routine.Relation()).create_bookmarks_routine(session, 1, 2)
        (_ := Routine.Relation()).delete_bookmarks_routine(session, 1, 2)
        (_ := Routine.Relation()).delete_bookmarks_routine(session, 1, 2)
        (_ := TaskFinish.Relation()).create_likes_task_finish(session, 1, 2)
        (_ := TaskFinish.Relation()).delete_likes_task_finish(session, 1, 2)
        (_ := TaskFinish.Relation()).delete_likes_task_finish(session, 1, 2)
        (_ := TaskFinishComment.Relation()).create_likes_task_finish_comment(session, 1, 2)
        (_ := TaskFinishComment.Relation()).delete_likes_task_finish_comment(session, 1, 2)
        (_ := TaskFinishComment.Relation()).delete_likes_task_finish_comment(session, 1, 2)
        (_ := FeedPost.Relation()).create_likes_feed_post(session, 1, 2)
        (_ := FeedPost.Relation()).delete_likes_feed_post(session, 1, 2)
        (_ := FeedPost.Relation()).delete_likes_feed_post(session, 1, 2)
        (_ := FeedPostComment.Relation()).create_likes_feed_post_comment(session, 1, 2)
        (_ := FeedPostComment.Relation()).delete_likes_feed_post_comment(session, 1, 2)
        (_ := FeedPostComment.Relation()).delete_likes_feed_post_comment(session, 1, 2)
    @classmethod
    def run_test(cls, session: Session) -> None:
        # コードを実行したい関数またはスクリプトを呼び出す
        n, m = 1, 10
        cls._delete_all(session)
        for i in range(1, n + 1):
            (_ := User()).create(session, i)
            (_ := Routine()).create(session, i)
            (_ := TaskFinish()).create(session, i)
            (_ := TaskFinishComment()).create(session, i)
            (_ := FeedPost()).create(session, i)
            (_ := FeedPostComment()).create(session, i)
        _Neo4jTest._duplicate_create(session)
        _Neo4jTest._create_and_duplicate_delete_edge(session)
        for _ in range(1, n + 1):
            (_ := User.Relation()).create_follows_user(session, *random.sample(range(1,  m), 2))
            (_ := User.Relation()).create_likes_feed_post(session, *random.sample(range(1,  m), 2))
            (_ := User.Relation()).create_likes_task_finish(session, *random.sample(range(1,  m), 2))
            (_ := User.Relation()).create_bookmarks_routine(session, *random.sample(range(1,  m), 2))
            print(f'\033[30m ここまで実行できた。 \033[0m')  #WARNING: routine.models.Routine.DoesNotExist: Routine matching query does not exist.
            (_ := Routine.Relation()).create_bookmarks_routine(session, *random.sample(range(1,  m), 2))
            (_ := TaskFinish.Relation()).create_likes_task_finish(session, *random.sample(range(1,  m), 2))
            (_ := TaskFinishComment.Relation()).create_likes_task_finish_comment(session, *random.sample(range(1,  m), 2))
            (_ := FeedPost.Relation()).create_likes_feed_post(session, *random.sample(range(1,  m), 2))
            (_ := FeedPostComment.Relation()).create_likes_feed_post_comment(session, *random.sample(range(1,  m), 2))
        # 存在しないノードを対象に探索してもエラーは吐かないことを確認
        for user_id in range(1, m):
            print(f'user_id = {user_id} --[FOLLOWS]-> user_ids      = {(_ := User()).read_follows_user_ids(session, user_id)}')
            print(f'user_id = {user_id} <-[FOLLOWS]-- user_ids      = {(_ := User()).read_followed_user_ids(session, user_id)}')
            print(f'user_id = {user_id} --[LIKES]---> feed_post_ids = {(_ := User()).read_likes_feed_post_ids(session, user_id)}')
            print(f'user_id = {user_id} --[LIKES]---> feed_post_ids = {(_ := FeedPost()).read_likes_feed_post_ids(session, user_id)}')
        BLUE, END = '\033[36m', '\033[0m'
        print(f"{BLUE}Successfully completed.{END}")


class Command(BaseCommand):
    help = 'Description of your command'

    def handle(self, *args, **kwargs):
        with neo4j_session:
            _Neo4jTest.run_test(neo4j_session)
