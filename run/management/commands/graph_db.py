import random
from feed.user_actions import FeedPost
from secret import LocalNeo4jDB as Neo4j
from neo4j import GraphDatabase, Driver, Session, Transaction
from django.db import connections
from django.db.backends.base.base import BaseDatabaseWrapper as BDW
from feed.ff_related import User
from feed.user_actions import FeedPost, TaskFinish
from django.core.management.base import BaseCommand
from feed.utils.graph_db.abstract_by_graph_db import Option

# DjangoのデータベースドライバとNeo4jのドライバを取得
pg_driver: BDW = connections['default']
neo4j_driver: Driver = GraphDatabase.driver(Neo4j.uri, auth=(Neo4j.user, Neo4j.password))

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
    def _read_edge(session: Session, n: int):
        # 存在しないノードを対象に探索してもエラーは吐かないことを確認
        for user_id in range(1, n):
            print(f'{user_id} -> {User.read_follows_user_id(session, user_id)}')
        for user_id in range(1, n):
            print(f'{user_id} <- {User.read_followed_user_id(session, user_id)}')
    @classmethod
    def run_test(cls, session: Session):
        cls._delete_all(session)
        n = 10
        for i in range(1, n + 1):
            FeedPost.create(session, i)
            User.create(session, i)
            TaskFinish.create(session, i)
        for i in range(1, n + 1):
            User.Relation.create(session, pg_driver, *random.sample(range(1, 5), 2))
        cls._read_edge(session, n)

class Command(BaseCommand):
    help = 'Description of your command'

    def handle(self, *args, **kwargs):
        with neo4j_driver.session() as session:
            _Neo4jTest.run_test(session)
