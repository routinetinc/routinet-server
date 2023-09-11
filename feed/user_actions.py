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
    class FeedPost:
        class _Tx:
            """ トランザクションの設計 """
            @staticmethod
            def create(tx: Transaction, id_for_rdb: int) -> None:
                """ id_for_rdb となるノードを作成 """
                cypher = 'CREATE (:FeedPost {id_for_rdb: $id_for_rdb})'
                tx.run(cypher, id_for_rdb=id_for_rdb)
                return 
            @staticmethod
            def delete(tx: Transaction, id_for_rdb: int) -> None:
                """ id_for_rdb が一致するノード削除 """
                cypher = 'MATCH (p:FeedPost {id_for_rdb: $id_for_rdb}) DETACH DELETE p'
                tx.run(cypher, id_for_rdb=id_for_rdb)
                return 
            @staticmethod
            def read_likes_feed_post_ids(tx: Transaction, user_id: int) -> list[int]:
                """ このユーザーがいいねしている Feed 投稿の ID 一覧を取得 """
                cypher = (
                    'MATCH (u:User {user_id: $user_id})-[:LIKES]->(p:FeedPost) '
                    'RETURN p.id_for_rdb AS id_for_rdb'
                )
                result = tx.run(cypher, user_id=user_id)
                return [record['id_for_rdb'] for record in result]
            @staticmethod
            def read_liked_user_ids(tx: Transaction, id_for_rdb: int) -> list[int]:
                """ この投稿にいいねしているユーザーの ID 一覧を取得 """
                cypher = (
                    'MATCH (p:FeedPost {id_for_rdb: $id_for_rdb})<-[:LIKES]-(u:User) '
                    'RETURN u.user_id AS user_id'
                )
                result = tx.run(cypher, id_for_rdb=id_for_rdb)
                return [record['user_id'] for record in result]  
        @classmethod
        def create(cls, session: Session, id_for_rdb: int) -> None:
            """ id_for_rdb となるノードを作成実行 """
            session.execute_write(cls._Tx.create, id_for_rdb)
            return
        @classmethod
        def delete(cls, session: Session, id_for_rdb: int) -> None:
            """ id_for_rdb が一致するノードを削除実行 """
            session.execute_write(cls._Tx.delete, id_for_rdb)
            return   
        @classmethod
        def read_likes_feed_post_ids(cls, session: Session, user_id: int) -> list[int]:
            """ Return: このユーザーがいいねしている Feed 投稿の ID 一覧 (降順) """
            # 投稿 ID が大きいことを最新の投稿物と仮定して最新のそれを取得しやすいよう降順にソート
            post_ids: list[int] = session.execute_read(cls._Tx.read_likes_feed_post_ids, user_id)
            return post_ids.sort(reverse=True)     
        @classmethod
        def read_liked_user_ids(cls, session: Session, id_for_rdb: int) -> list[int]:
            """ Return: その投稿にいいねしているユーザーの ID 一覧 """
            return session.execute_read(cls._Tx.read_liked_user_ids, id_for_rdb)
    
    #* class Edge:
    # エッジの作成、取得、更新、削除
    class LIKES:
        """ Label: LIKES <Edge> """
        class _Tx:
            """ トランザクションの設計 """
            @staticmethod
            def create(tx: Transaction, from_user_id: int, to_feed_post_id: int) -> None:
                """ いいね """
                GenericEdge.create(tx, from_user_id, to_feed_post_id, label='LIKES', is_to_node_label_feed_post=True)
                return
            @staticmethod
            def delete(tx: Transaction, from_user_id: int, to_feed_post_id: int) -> None:
                """ いいね取り消し """
                GenericEdge.delete(tx, from_user_id, to_feed_post_id, label='LIKES', is_to_node_label_feed_post=True)
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
    
class TaskFinish:
    """ Label: FeedPost <Node> """
    class _Tx:
        """ トランザクションの設計 """
        @staticmethod
        def create(tx: Transaction, id_for_rdb: int) -> None:
            """ ノードを作成 """
            cypher = 'CREATE (:TaskFinish {id_for_rdb: $id_for_rdb})'
            tx.run(cypher, id_for_rdb=id_for_rdb)
            return 
        @staticmethod
        def delete(tx: Transaction, id_for_rdb: int) -> None:
            """ ノード削除 """
            cypher = 'MATCH (p:TaskFinish {id_for_rdb: $id_for_rdb}) DETACH DELETE p'
            tx.run(cypher, id_for_rdb=id_for_rdb)
            return 
        @staticmethod
        def read_likes_feed_post_ids(tx: Transaction, user_id: int) -> list[int]:
            """ このユーザーがいいねしている Feed 投稿の ID 一覧を取得 """
            cypher = (
                'MATCH (u:User {user_id: $user_id})-[:LIKES]->(p:TaskFinish) '
                'RETURN p.id_for_rdb AS id_for_rdb'
            )
            result = tx.run(cypher, user_id=user_id)
            return [record['id_for_rdb'] for record in result]
        @staticmethod
        def read_liked_user_ids(tx: Transaction, id_for_rdb: int) -> list[int]:
            """ この投稿にいいねしているユーザーの ID 一覧を取得 """
            cypher = (
                'MATCH (p:TaskFinish {id_for_rdb: $id_for_rdb})<-[:LIKES]-(u:User) '
                'RETURN u.user_id AS user_id'
            )
            result = tx.run(cypher, id_for_rdb=id_for_rdb)
            return [record['user_id'] for record in result]  
    @classmethod
    def create(cls, session: Session, id_for_rdb: int) -> None:
        """ ノードを作成実行 """
        session.execute_write(cls._Tx.create, id_for_rdb)
        return
    @classmethod
    def delete(cls, session: Session, id_for_rdb: int) -> None:
        """ ノードを削除実行 """
        session.execute_write(cls._Tx.delete, id_for_rdb)
        return   
    @classmethod
    def read_likes_feed_post_ids(cls, session: Session, user_id: int) -> list[int]:
        """ Return: このユーザーがいいねしている Feed 投稿の ID 一覧 (降順) """
        # 投稿 ID が大きいことを最新の投稿物と仮定して最新のそれを取得しやすいよう降順にソート
        post_ids: list[int] = session.execute_read(cls._Tx.read_likes_feed_post_ids, user_id)
        return post_ids.sort(reverse=True)     
    @classmethod
    def read_liked_user_ids(cls, session: Session, id_for_rdb: int) -> list[int]:
        """ Return: その投稿にいいねしているユーザーの ID 一覧 """
        return session.execute_read(cls._Tx.read_liked_user_ids, id_for_rdb)
    
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


class Routine:
    class Routine:
        class _Tx:
            """ トランザクションの設計 """
            @staticmethod
            def create(tx: Transaction, id_for_rdb: int) -> None:
                """ id_for_rdb となるノードを作成 """
                cypher = 'CREATE (:FeedPost {id_for_rdb: $id_for_rdb})'
                tx.run(cypher, id_for_rdb=id_for_rdb)
                return 
            @staticmethod
            def delete(tx: Transaction, id_for_rdb: int) -> None:
                """ id_for_rdb が一致するノード削除 """
                cypher = 'MATCH (p:FeedPost {id_for_rdb: $id_for_rdb}) DETACH DELETE p'
                tx.run(cypher, id_for_rdb=id_for_rdb)
                return 
            @staticmethod
            def read_bookmarks_feed_post_ids(tx: Transaction, user_id: int) -> list[int]:
                """ このユーザーがブックマークしている Feed 投稿の ID 一覧を取得 """
                cypher = (
                    'MATCH (u:User {user_id: $user_id})-[:BOOKMARKS]->(p:Routine) '
                    'RETURN p.id_for_rdb AS id_for_rdb'
                )
                result = tx.run(cypher, user_id=user_id)
                return [record['id_for_rdb'] for record in result]
            @staticmethod
            def read_bookmarked_user_ids(tx: Transaction, id_for_rdb: int) -> list[int]:
                """ この投稿をブックマークしているユーザーの ID 一覧を取得 """
                cypher = (
                    'MATCH (p:Routine {id_for_rdb: $id_for_rdb})<-[:BOOKMARKS]-(u:User) '
                    'RETURN u.user_id AS user_id'
                )
                result = tx.run(cypher, id_for_rdb=id_for_rdb)
                return [record['user_id'] for record in result]
        @classmethod
        def create(cls, session: Session, id_for_rdb: int) -> None:
            """ ノードを作成実行 """
            session.execute_write(cls._Tx.create, id_for_rdb)
            return
        @classmethod
        def delete(cls, session: Session, id_for_rdb: int) -> None:
            """ ノードを削除実行 """
            session.execute_write(cls._Tx.delete, id_for_rdb)
            return     
        @classmethod
        def read_bookmarks_feed_post_ids(cls, session: Session, user_id: int) -> list[int]:
            """ Return: このユーザーがブックマークしている Feed 投稿の ID 一覧 (降順) """
            # 投稿 ID が大きいことを最新の投稿物と仮定して最新のそれを取得しやすいよう降順にソート
            post_ids: list[int] = session.execute_read(cls._Tx.read_bookmarks_feed_post_ids, user_id)
            return post_ids.sort(reverse=True)      
        @classmethod
        def read_bookmarked_user_ids(cls, session: Session, id_for_rdb: int) -> list[int]:
            """ Return: その投稿をブックマークしているユーザーの ID 一覧 """
            return session.execute_read(cls._Tx.read_bookmarked_user_ids, id_for_rdb)
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
