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
class FeedPost:
    """ Label: FeedPost <Node> """
    class _Tx:
        """ トランザクションの設計 """
        @staticmethod
        def create(tx: Transaction, post_id: int) -> None:
            """ post_id となるノードを作成 """
            cypher = 'CREATE (:FeedPost {post_id: $post_id})'
            tx.run(cypher, post_id=post_id)
            return 
        @staticmethod
        def delete(tx: Transaction, post_id: int) -> None:
            """ post_id が一致するノード削除 """
            cypher = 'MATCH (p:FeedPost {post_id: $post_id}) DETACH DELETE p'
            tx.run(cypher, post_id=post_id)
            return 
        @staticmethod
        def read_likes_feed_post_ids(tx: Transaction, user_id: int) -> list[int]:
            """ このユーザーがいいねしている Feed 投稿の ID 一覧を取得 """
            cypher = (
                'MATCH (u:User {user_id: $user_id})-[:LIKES]->(p:FeedPost) '
                'RETURN p.post_id AS post_id'
            )
            result = tx.run(cypher, user_id=user_id)
            return [record['post_id'] for record in result]
        @staticmethod
        def read_bookmarks_feed_post_ids(tx: Transaction, user_id: int) -> list[int]:
            """ このユーザーがブックマークしている Feed 投稿の ID 一覧を取得 """
            cypher = (
                'MATCH (u:User {user_id: $user_id})-[:BOOKMARKS]->(p:FeedPost) '
                'RETURN p.post_id AS post_id'
            )
            result = tx.run(cypher, user_id=user_id)
            return [record['post_id'] for record in result]
        @staticmethod
        def read_liked_user_ids(tx: Transaction, post_id: int) -> list[int]:
            """ この投稿にいいねしているユーザーの ID 一覧を取得 """
            cypher = (
                'MATCH (p:FeedPost {post_id: $post_id})<-[:LIKES]-(u:User) '
                'RETURN u.user_id AS user_id'
            )
            result = tx.run(cypher, post_id=post_id)
            return [record['user_id'] for record in result]
        @staticmethod
        def read_bookmarked_user_ids(tx: Transaction, post_id: int) -> list[int]:
            """ この投稿をブックマークしているユーザーの ID 一覧を取得 """
            cypher = (
                'MATCH (p:FeedPost {post_id: $post_id})<-[:BOOKMARKS]-(u:User) '
                'RETURN u.user_id AS user_id'
            )
            result = tx.run(cypher, post_id=post_id)
            return [record['user_id'] for record in result]   
    @classmethod
    def create(cls, session: Session, post_id: int) -> None:
        """ post_id となるノードを作成実行 """
        session.execute_write(cls._Tx.create, post_id)
        return
    @classmethod
    def delete(cls, session: Session, post_id: int) -> None:
        """ post_id が一致するノードを削除実行 """
        session.execute_write(cls._Tx.delete, post_id)
        return   
    @classmethod
    def read_likes_feed_post_ids(cls, session: Session, user_id: int) -> list[int]:
        """ Return: このユーザーがいいねしている Feed 投稿の ID 一覧 (降順) """
        # 投稿 ID が大きいことを最新の投稿物と仮定して最新のそれを取得しやすいよう降順にソート
        post_ids: list[int] = session.execute_read(cls._Tx.read_likes_feed_post_ids, user_id)
        return post_ids.sort(reverse=True)
    @classmethod
    def read_bookmarks_feed_post_ids(cls, session: Session, user_id: int) -> list[int]:
        """ Return: このユーザーがブックマークしている Feed 投稿の ID 一覧 (降順) """
        # 投稿 ID が大きいことを最新の投稿物と仮定して最新のそれを取得しやすいよう降順にソート
        post_ids: list[int] = session.execute_read(cls._Tx.read_bookmarks_feed_post_ids, user_id)
        return post_ids.sort(reverse=True)      
    @classmethod
    def read_liked_user_ids(cls, session: Session, post_id: int) -> list[int]:
        """ Return: その投稿にいいねしているユーザーの ID 一覧 """
        return session.execute_read(cls._Tx.read_liked_user_ids, post_id)
    @classmethod
    def read_bookmarked_user_ids(cls, session: Session, post_id: int) -> list[int]:
        """ Return: その投稿をブックマークしているユーザーの ID 一覧 """
        return session.execute_read(cls._Tx.read_bookmarked_user_ids, post_id)
    

#* class Edge:
# エッジの作成、取得、更新、削除
class LIKES:
    """ Label: LIKES <Edge> """
    class _Tx:
        """ トランザクションの設計 """
        @staticmethod
        def create(tx: Transaction, from_user_id: int, to_feed_post_id: int) -> None:
            """ いいね """
            GenericEdge.create(tx, from_user_id, to_feed_post_id, label='LIKES')
            return
        @staticmethod
        def delete(tx: Transaction, from_user_id: int, to_feed_post_id: int) -> None:
            """ いいね取り消し """
            GenericEdge.delete(tx, from_user_id, to_feed_post_id, label='LIKES')
            return
    @classmethod
    def create(cls, session: Session, from_user_id: int, to_user_id: int) -> None:
        """ いいね実行 """
        session.execute_write(cls._Tx.create, from_user_id, to_user_id)
        return
    @classmethod
    def delete(cls, session: Session, from_user_id: int, to_user_id: int) -> None:
        """ いいね取り消し実行 """
        session.execute_write(cls._Tx.create, from_user_id, to_user_id)
        return
class BOOKMARKS:
    """ Label: BOOKMARKS <Edge> """
    class _Tx:
        """ トランザクションの設計 """
        @staticmethod
        def create(tx: Transaction, from_user_id: int, to_feed_post_id: int) -> None:
            """ ブックマークへ追加 """
            GenericEdge.create(tx, from_user_id, to_feed_post_id, label='BOOKMARKS')
            return
        @staticmethod
        def delete(tx: Transaction, from_user_id: int, to_feed_post_id: int) -> None:
            """ ブックマーク削除 """
            GenericEdge.delete(tx, from_user_id, to_feed_post_id, label='BOOKMARKS')
            return
    @classmethod
    def create(cls, session: Session, to_feed_post_id: int) -> None:
        """ ブックマークへ追加実行 """
        session.execute_write(cls._Tx.create, to_feed_post_id)
        return
    @classmethod
    def delete(cls, session: Session, to_feed_post_id: int) -> None:
        """ ブックマーク削除実行 """
        session.execute_write(cls._Tx.create, to_feed_post_id)
        return