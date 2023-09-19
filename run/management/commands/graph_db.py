import random
from feed.user_actions import FeedPost
from neo4j import Session, Transaction
from feed.ff_related import User
from feed.user_actions import FeedPost, TaskFinish
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
    @classmethod
    def run_test(cls, session: Session):
        # コードを実行したい関数またはスクリプトを呼び出す
        cls._delete_all(session)
        n = 10
        for i in range(1, n + 1):
            User.create(session, i)
            FeedPost.create(session, i)
        for i in range(1, n + 1):
            FeedPost.Relation.create(session, *random.sample(range(1, 5), 2))
        # 存在しないノードを対象に探索してもエラーは吐かないことを確認
        for user_id in range(1, n):
            print(f'{user_id} -[LIKES]-> {FeedPost.read_likes_feed_post_ids(session, user_id)}')
        BLUE, END = '\033[36m', '\033[0m'
        print(f"{BLUE}Successfully completed.{END}")


class Command(BaseCommand):
    help = 'Description of your command'

    def handle(self, *args, **kwargs):
        with neo4j_session:
            _Neo4jTest.run_test(neo4j_session)
