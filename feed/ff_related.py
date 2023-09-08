from secret import LocalNeo4jDB as Neo4j
from neo4j import GraphDatabase, Driver, Transaction, Session
from django.db import connection
from django.db.backends.base.base import BaseDatabaseWrapper as BDW
from feed.utils.graph_db import GenericEdge

#* PostgreSQL, Neo4j データベースに接続するために必要な情報を設定
pg_connection: BDW = connection['default']
driver: Driver = GraphDatabase.driver(Neo4j.uri, auth=(Neo4j.user, Neo4j.password))


#* class Node:
# ノードまたはノードの属性の作成、取得、更新、削除
class User:
    """ Label: User <Node> """
    class _Tx:
        """ トランザクションの設計 """
        @staticmethod
        def create(tx: Transaction, user_id: int) -> None:
            """ user_id となるノードを作成 """
            cypher = 'CREATE (:User {user_id: $user_id})'
            tx.run(cypher, user_id=user_id)
            return 
        @staticmethod
        def delete(tx: Transaction, user_id: int) -> None:
            """ user_id が一致するノードを削除 """
            cypher = 'MATCH (u:User {user_id: $user_id}) DETACH DELETE u'
            tx.run(cypher, user_id=user_id)
            return 
        @staticmethod
        def read_follows_user_ids(tx: Transaction, user_id: int) -> list[int]:
            """ フォロー中のユーザー ID 一覧を取得 """
            cypher = (
                'MATCH (x:User {user_id: $user_id})-[:FOLLOWS]->(y:User) '
                'RETURN y.user_id AS following_id'
            )
            result = tx.run(cypher, user_id=user_id)
            return [record['following_id'] for record in result]
        @staticmethod
        def read_followed_user_ids(tx: Transaction, user_id: int) -> list[int]:
            """ フォロワーの ID 一覧を取得 """
            cypher = (
                'MATCH (x:User {user_id: $user_id})<-[:FOLLOWS]-(y:User) '
                'RETURN y.user_id as follower_id'
            )
            result = tx.run(cypher, user_id=user_id)
            return [record['follower_id'] for record in result]
    @classmethod
    def create(cls, session: Session, user_id: int) -> None:
        """ user_id となるノードを作成実行 """
        session.execute_write(cls._Tx.create, user_id)       
        return
    def delete(cls, session: Session, user_id: int) -> None:
        """ user_id が一致するノードを削除実行 """
        session.execute_write(cls._Tx.delete, user_id)       
        return
    @classmethod
    def read_follows_user_ids(cls, session: Session, user_id: int) -> list[int]:
        """ Return: フォロー中のユーザー ID 一覧 """
        return session.execute_read(cls._Tx.read_follows_user_ids, user_id)
    @classmethod 
    def read_followed_user_ids(cls, session: Session, user_id: int) -> list[int]:
        """ Return: フォロワーの ID 一覧 """
        return session.execute_read(cls._Tx.read_followed_user_ids, user_id)
    
  
#* class Edge:
# エッジの作成、取得、更新、削除
class FOLLOWS:
    """ Label: FOLLOWS <Edge> """
    class _Tx:
        """ トランザクションの設計 """
        @staticmethod
        def create(tx: Transaction, from_user_id: int, to_user_id: int) -> None:
            """ フォロー """
            GenericEdge.create(tx, from_user_id, to_user_id, label='FOLLOWS')
            return
        @staticmethod
        def delete(tx: Transaction, from_user_id: int, to_user_id: int) -> None:
            """ フォロー解除 """
            GenericEdge.delete(tx, from_user_id, to_user_id, label='FOLLOWS')
            return
    @classmethod
    def create(cls, session: Session, from_user_id: int, to_user_id: int) -> None:
        """ フォロー実行 """
        session.execute_write(cls._Tx.create, from_user_id, to_user_id)
        return 
    @classmethod
    def delete(cls, session: Session, from_user_id: int, to_user_id: int) -> None:
        """ フォロー解除実行 """
        session.execute_write(cls._Tx.create, from_user_id, to_user_id)
        return