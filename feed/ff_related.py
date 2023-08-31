# import os
# os.chdir('../..')
# os.environ['DJANGO_SETTINGS_MODULE'] = 'KGAvengers.settings'
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'KGAvengers.settings')
# import django
# django.setup()
#* ---------------------------------------------------------------------- *# 
import random
from typing import Any, Final
from neo4j import GraphDatabase, Driver, Transaction, Session
from secret import LocalNeo4jDB as Neo4j
from django.db import connections
from django.db.backends.base.base import BaseDatabaseWrapper as BDW
from psycopg2 import sql
from psycopg2.extensions import cursor

#* PostgreSQL, Neo4j データベースに接続するために必要
pg_connection: BDW = connections['default']
driver: Driver = GraphDatabase.driver(Neo4j.uri, auth=(Neo4j.user, Neo4j.password))

# class Execute:
#     """ 1 回のセッションで単数または複数のトランザクションを実行 """
#     @staticmethod
#     def write_multi(txs: list[tuple]) -> None:
#         """ 複数のトランザクション (書き込み) を実行 """
#         with driver.session() as session:
#             for tx in txs:
#                 session.execute_write(*tx)
#         return 
#     @staticmethod
#     def read_multi(txs: list[tuple]) -> list[Any]:
#         """ 複数のトランザクション (取得) を実行 """
#         stores = []
#         with driver.session() as session:
#             for tx in txs:
#                 stores.append = session.execute_read(*tx)
#         return stores
#     @staticmethod
#     def write_single(*tx) -> None:
#         """ 1 つのトランザクション (書き込み) を実行 """
#         with driver.session() as session:
#             session.execute_write(*tx)
#         return 
#     @staticmethod
#     def read_single(*tx) -> Any:
#         """ 1 つのトランザクション (取得) を実行 """
#         with driver.session() as session:
#             store = session.execute_read(*tx)
#         return store


class Node:
    """ ノードまたはノードの属性の作成、取得、更新、削除 """
    @staticmethod
    def _delete_all() -> None:
        """ 全ノード削除 `実行` """
        with driver.session() as session:
            # ノードのラベルを全種類取得する関数
            def _tx_get_node_labels(tx: Transaction):
                query = 'MATCH (n) UNWIND labels(n) AS label RETURN DISTINCT label'
                with driver.session().begin_transaction() as tx:
                    result = tx.run(query)
                return [record['label'] for record in result]
            # あるラベルのノードを全て削除する関数
            def _tx_delete_nodes_with_label(tx: Transaction, label: str):
                query = f'MATCH (u:{label}) DETACH DELETE u'
                with driver.session().begin_transaction() as tx:
                    tx.run(query)
            # ラベルを一括取得
            labels = session.execute_read(_tx_get_node_labels)
            # ラベルごとにノードを削除
            for node_labels in labels:
                session.execute_write(_tx_delete_nodes_with_label, node_labels)
            return
    class User:
        """ Label: User """
        class TX:
            """ トランザクションの設計 """
            @staticmethod
            def create(tx: Transaction, user_id: int) -> None:
                """ ノード作成 """
                query = 'CREATE (:User {user_id: $user_id})'
                tx.run(query, user_id=user_id)
                return 
            @staticmethod
            def delete(tx: Transaction, user_id):
                """ user_id が一致するノード削除 """
                query = 'MATCH (u:User {user_id: $user_id}) DETACH DELETE u'
                tx.run(query, user_id=user_id)
                return 
            @staticmethod
            def read_follows_user_ids(tx: Transaction, user_id: int) -> list[int]:
                """ フォロー中のユーザー ID 一覧を取得 """
                query = (
                    'MATCH (x:User {user_id: $user_id})-[:FOLLOWS]->(y:User) '
                    'RETURN y.user_id AS following_id'
                )
                result = tx.run(query, user_id=user_id)
                return [record['following_id'] for record in result]
            @staticmethod
            def read_followed_user_ids(tx: Transaction, user_id: int) -> list[int]:
                """ フォロワーの ID 一覧を取得 """
                query = (
                    'MATCH (x:User {user_id: $user_id})<-[:FOLLOWS]-(y:User) '
                    'RETURN y.user_id as follower_id'
                )
                result = tx.run(query, user_id=user_id)
                return [record['follower_id'] for record in result]
            @staticmethod
            def read_likes_feed_post_ids(tx: Transaction, user_id: int) -> list[int]:
                """ このユーザーがいいねしている Feed 投稿の ID 一覧を取得 """
                query = (
                    'MATCH (u:User {user_id: $user_id})-[:LIKES]->(p:FeedPost) '
                    'RETURN p.post_id AS post_id'
                )
                result = tx.run(query, user_id=user_id)
                return [record['post_id'] for record in result]
            @staticmethod
            def read_bookmarks_feed_post_ids(tx: Transaction, user_id: int) -> list[int]:
                """ このユーザーがブックマークしている Feed 投稿の ID 一覧を取得 """
                query = (
                    'MATCH (u:User {user_id: $user_id})-[:BOOKMARKS]->(p:FeedPost) '
                    'RETURN p.post_id AS post_id'
                )
                result = tx.run(query, user_id=user_id)
                return [record['post_id'] for record in result]
        @classmethod
        def read_follows_user_ids(cls, session: Session, user_id: int) -> list[int]:
            """ Return: フォロー中のユーザー ID 一覧 """
            return session.execute_read(cls.TX.read_follows_user_ids, user_id)
        @classmethod 
        def read_followed_user_ids(cls, session: Session, user_id: int) -> list[int]:
            """ Return: フォロワーの ID 一覧 """
            return session.execute_read(cls.TX.read_followed_user_ids, user_id)
        @classmethod
        def read_likes_feed_post_ids(cls, session: Session, user_id: int) -> list[int]:
            """ Return: このユーザーがいいねしている Feed 投稿の ID 一覧 (降順) """
            # 投稿 ID が大きいことを最新の投稿物と仮定して最新のそれを取得しやすいよう降順にソート
            post_ids: list[int] = session.execute_read(cls.TX.read_likes_feed_post_ids, user_id)
            return post_ids.sort(reverse=True)
        @classmethod
        def read_bookmarks_feed_post_ids(cls, session: Session, user_id: int) -> list[int]:
            """ Return: このユーザーがブックマークしている Feed 投稿の ID 一覧 (降順) """
            # 投稿 ID が大きいことを最新の投稿物と仮定して最新のそれを取得しやすいよう降順にソート
            post_ids: list[int] = session.execute_read(cls.TX.read_bookmarks_feed_post_ids, user_id)
            return post_ids.sort(reverse=True)
    class FeedPost:
        """ Label: FeedPost """
        class TX:
            @staticmethod
            def create(tx: Transaction, post_id: int) -> None:
                """ ノード作成 """
                query = 'CREATE (:FeedPost {post_id: $post_id})'
                tx.run(query, post_id=post_id)
                return 
            @staticmethod
            def delete(tx: Transaction, post_id):
                """ post_id が一致するノード削除 """
                query = 'MATCH (p:FeedPost {post_id: $post_id}) DETACH DELETE p'
                tx.run(query, post_id=post_id)
                return 
            @staticmethod
            def read_liked_user_ids(tx: Transaction, post_id: int) -> list[int]:
                """ この投稿にいいねしているユーザーの ID 一覧を取得 """
                query = (
                    'MATCH (p:FeedPost {post_id: $post_id})<-[:LIKES]-(u:User) '
                    'RETURN u.user_id AS user_id'
                )
                result = tx.run(query, post_id=post_id)
                return [record['user_id'] for record in result]
            @staticmethod
            def read_bookmarked_user_ids(tx: Transaction, post_id: int) -> list[int]:
                """ この投稿をブックマークしているユーザーの ID 一覧を取得 """
                query = (
                    'MATCH (p:FeedPost {post_id: $post_id})<-[:BOOKMARKS]-(u:User) '
                    'RETURN u.user_id AS user_id'
                )
                result = tx.run(query, post_id=post_id)
                return [record['user_id'] for record in result]            
        @classmethod
        def read_liked_user_ids(cls, *post_ids: int) -> list[dict]:
            """ Return: これらの投稿にいいねしているユーザーの ID 一覧 """
            user_ids = []
            with driver.session() as session:
                for post_id in post_ids:
                    user_ids.append({'post_id': post_id, 'user_ids': session.execute_read(cls.read_liked_user_ids, post_id)})
            return user_ids
        @classmethod
        def read_bookmarked_user_ids(cls, *post_ids: int) -> list[dict]:
            """ Return: これらの投稿をブックマークしているユーザーの ID 一覧 """
            user_ids = []
            with driver.session() as session:
                for post_id in post_ids:
                    user_ids.append({'post_id': post_id, 'user_ids': session.execute_read(cls.read_bookmarked_user_ids, post_id)})
            return user_ids


class UtilityAboutEdge:
    @staticmethod
    def _create_by_user_action(tx: Transaction, from_user_id: int, to_id: int, label: str) -> None:
        """ `rdb_tx` is the RDB transaction function to be linked. `label` is the edge label name. """
        to_node_label = 'User' if(label=='FOLLOWS') else 'FeedPost'
        to_id_name = 'user_id' if(label=='FOLLOWS') else 'post_id'
        check_query = (
                    f'MATCH (x:User {{user_id: $from_user_id}})-[:{label}]->(y:{to_node_label} {{{to_id_name}: $to_id}}) '
                    'RETURN COUNT(*) AS num'
                )
        check_result = tx.run(check_query, from_user_id=from_user_id, to_id=to_id).single()
        num = check_result['num']
        # アクションしていないならばアクション
        if num == 0:
            create_query = (
                        f'MATCH (x:User {{user_id: $from_user_id}}), (y:{to_node_label} {{{to_id_name}: $to_id}}) '
                        f'CREATE (x)-[:{label}]->(y) '
                    )
            query = create_query
            tx.run(query, from_user_id=from_user_id, to_id=to_id)
        return
    @staticmethod
    def _delete_by_user_action(tx: Transaction, from_user_id: int, to_id: int, label: str) -> int:
        """ `rdb_tx` is the RDB transaction function to be linked. `label` is the edge label name. \
            The return value is 1 if the action has already been performed, 0 otherwise."""
        to_id_name = 'user_id' if(label=='FOLLOWS') else 'post_id'
        to_node_label = 'User' if(label=='FOLLOWS') else 'FeedPost'
        check_query = (
                    f'MATCH (x:User {{user_id: $from_user_id}})-[:{label}]->(y:{to_node_label} {{{to_id_name}: $to_id}}) '
                    'RETURN COUNT(*) AS num'
                )
        check_result = tx.run(check_query, from_user_id=from_user_id, to_id=to_id).single()
        num = check_result['num']
        # アクションしていたならばアクション取り消し
        if num > 0:
            create_query = (
                        f'MATCH (x:User {{user_id: $from_user_id}})-[:{label}]->(y:{to_node_label} {{{to_id_name}: $to_user_id}}) '
                        'DELETE r'
                    )
            query = create_query
            tx.run(query, from_user_id=from_user_id, to_id=to_id)
        return num


class Edge:
    """ エッジの作成、取得、更新、削除 """
    class FOLLOWS:
        """ Label: FOLLOWS """
        class TX:
            """ トランザクションの設計 """
            @staticmethod
            def create(tx: Transaction, from_user_id: int, to_user_id: int) -> None:
                """ フォロー時の Neo4j 側の動作を指定 """
                UtilityAboutEdge._create_by_user_action(tx, from_user_id, to_user_id, label='FOLLOWS')
                return
            @staticmethod
            def delete(tx: Transaction, from_user_id: int, to_user_id: int) -> None:
                """ フォロー解除時の Neo4j 側の動作を指定 """
                UtilityAboutEdge._delete_by_user_action(tx, from_user_id, to_user_id, label='FOLLOWS')
                return
            class PG:
                """ PostgreSQL """
                @staticmethod
                def _update_user_by_create(pg_cursor: cursor, from_user_id: int, to_user_id: int) -> None:
                    """ フォロー時にそれぞれのユーザーのフォロー人数及びフォロワー人数を更新 """
                    pg_query = sql.SQL('''
                                WARNING: テーブル構造やテーブル名、属性の変更に注意
                                UPDATE supplyauth_user 
                                SET following = following + 1 
                                WHERE id = %s;
                                UPDATE supplyauth_user 
                                SET followers = follower + 1 
                                WHERE id = %s;
                        ''')
                    pg_cursor.execute(pg_query, (from_user_id, to_user_id))
                    pg_connection.commit()
                    return
                def _update_user_by_delete(pg_cursor: cursor, from_user_id: int, to_user_id: int) -> None:
                    """ フォロー解除時にそれぞれのユーザーのフォロー人数及びフォロワー人数を更新 """
                    pg_query = sql.SQL('''
                                WARNING: テーブル構造やテーブル名、属性の変更に注意
                                UPDATE supplyauth_user 
                                SET following = following - 1 
                                WHERE id = %s;
                                UPDATE supplyauth_user 
                                SET followers = follower - 1 
                                WHERE id = %s;
                        ''')
                    pg_cursor.execute(pg_query, (from_user_id, to_user_id))
                    pg_connection.commit()
                    return                    
        @classmethod
        def create(cls, cursor: cursor, session: Session, from_user_id: int, to_user_id: int) -> None:
            """ Neo4j と PostgreSQL のフォロー時のトランザクションを統合 """
            try: 
                session.execute_write(cls.TX.create, from_user_id, to_user_id)
                cls.TX.PG._update_user_by_create(cursor, from_user_id, to_user_id)
            except Exception as e:
                return {'status_code': -1, 'error_message': f'Transaction Failed: {e}'}
        @classmethod
        def delete(cls, cursor: cursor, session: Session, from_user_id: int, to_user_id: int) -> None:
            """ Neo4j と PostgreSQL のフォロー解除時のトランザクションを統合 """
            try: 
                session.execute_write(cls.TX.create, from_user_id, to_user_id)
                cls.TX.PG._update_user_by_delete(cursor, from_user_id, to_user_id)
            except Exception as e:
                return {'status_code': -1, 'error_message': f'Transaction Failed: {e}'}
    class LIKES:
        """ Label: LIKES """
        class TX:
            """ トランザクションの設計 """
            @staticmethod
            def create_to_feed_post(tx: Transaction, from_user_id: int, to_feed_post_id: int) -> None:
                """ いいね時の Neo4j 側の動作を指定 """
                UtilityAboutEdge._create_by_user_action(tx, from_user_id, to_feed_post_id, label='LIKES')
                return
            @staticmethod
            def delete_to_feed_post(tx: Transaction, from_user_id: int, to_feed_post_id: int) -> None:
                """ いいね取り消し時の Neo4j 側の動作を指定 """
                UtilityAboutEdge._delete_by_user_action(tx, from_user_id, to_feed_post_id, label='LIKES')
                return
            class PG:
                """ PostgreSQL """
                @staticmethod
                def _update_feed_post_by_create(pg_cursor: cursor, to_feed_post_id: int) -> None:
                    """ いいね時にコンテンツのいいね数を更新 """
                    pg_query = sql.SQL('''
                                WARNING: テーブル構造やテーブル名、属性の変更に注意
                                UPDATE feed_post 
                                SET like_num = like_num + 1 
                                WHERE id = %s;
                        ''')
                    pg_cursor.execute(pg_query, (to_feed_post_id, ))
                    pg_connection.commit()
                    return
                @staticmethod
                def _update_feed_post_by_delete(pg_cursor: cursor, to_feed_post_id: int) -> None:
                    """ いいね取り消し時にコンテンツのいいね数を更新 """
                    pg_query = sql.SQL('''
                                WARNING: テーブル構造やテーブル名、属性の変更に注意
                                UPDATE feed_post 
                                SET like_num = like_num - 1 
                                WHERE id = %s;
                        ''')
                    pg_cursor.execute(pg_query, (to_feed_post_id, ))
                    pg_connection.commit()
                    return  
        @classmethod
        def create(cls, cursor: cursor, session: Session, from_user_id: int, to_user_id: int) -> None:
            """ Neo4j と PostgreSQL のいいね時のトランザクションを統合 """
            try: 
                session.execute_write(cls.TX.create_to_feed_post, from_user_id, to_user_id)
                cls.TX.PG._update_feed_post_by_create(cursor, from_user_id, to_user_id)
            except Exception as e:
                pg_connection.rollback()
                driver.session().rollback()#HACK
                return {'status_code': -1, 'error_message': f'Transaction Failed: {e}'}
        @classmethod
        def delete(cls, cursor: cursor, session: Session, from_user_id: int, to_user_id: int) -> None:
            """ Neo4j と PostgreSQL のいいね取り消し時のトランザクションを統合 """
            try: 
                session.execute_write(cls.TX.create_to_feed_post, from_user_id, to_user_id)
                cls.TX.PG._update_feed_post_by_delete(cursor, from_user_id, to_user_id)
            except Exception as e:
                return {'status_code': -1, 'error_message': f'Transaction Failed: {e}'}
    class BOOKMARKS:
        """ Label: BOOKMARKS """
        class TX:
            """ トランザクションの設計 """
            @staticmethod
            def create_to_feed_post(tx: Transaction, from_user_id: int, to_feed_post_id: int) -> None:
                """ ブックマークに追加 """
                UtilityAboutEdge._create_by_user_action(tx, from_user_id, to_feed_post_id, label='BOOKMARKS')
                return
            @staticmethod
            def delete_to_feed_post(tx: Transaction, from_user_id: int, to_feed_post_id: int) -> None:
                """ ブックマーク削除 """
                UtilityAboutEdge._delete_by_user_action(tx, from_user_id, to_feed_post_id, label='BOOKMARKS')
                return
            class PG:
                """ PostgreSQL """
                @staticmethod
                def _update_user_by_create(pg_cursor: cursor, post_id: int) -> None:
                    """ いいね時にコンテンツのいいね数を更新 """
                    pg_query = sql.SQL('''
                                WARNING: テーブル構造やテーブル名、属性の変更に注意
                                UPDATE feed_post 
                                SET like_num = like_num + 1 
                                WHERE id = %s;
                        ''')
                    pg_cursor.execute(pg_query, (post_id, ))
                    pg_connection.commit()
                    return
                @staticmethod
                def _update_user_by_delete(pg_cursor: cursor, post_id: int) -> None:
                    """ いいね取り消し時にコンテンツのいいね数を更新 """
                    pg_query = sql.SQL('''
                                WARNING: テーブル構造やテーブル名、属性の変更に注意
                                UPDATE feed_post 
                                SET like_num = like_num - 1 
                                WHERE id = %s;
                        ''')
                    pg_cursor.execute(pg_query, (post_id, ))
                    pg_connection.commit()
                    return  


#* テスト
n = 15
if __name__ == '__main__':
    txs  = [(Node.User.TX.create, i) for i in range(1, n + 1)]
    txs += [(Edge.FOLLOWS.TX.create, *random.sample(tuple(range(1, n - 10)), 2)) for _ in range(1, n // 2)]
    txs += [(Node.FeedPost.TX.create, i) for i in range(1, 3 * n + 1)]
    txs += [(Edge.LIKES.TX.create_to_feed_post, *random.sample(tuple(range(1, 3 * n - 10)), 2)) for _ in range(1, n)]
    txs += [(Edge.BOOKMARKS.TX.create_to_feed_post, *random.sample(tuple(range(1, 3 * n - 10)), 2)) for _ in range(1, n)]
    def __read_edge(n: int):
        for user_id in range(1, n):
            # 実行している関数の仕様上、毎回 driver.session() が発生し低速であることに留意
            # 存在しないノードであったとしてもエラーは吐かないことに留意
            print(f'{user_id} -> {Node.User.read_follows_user_ids(user_id)}')
        for user_id in range(1, n):
            print(f'{user_id} <- {Node.User.read_followed_user_ids(user_id)}')

    Node._delete_all()
    # Execute.write_single(Node.User.TX.delete, 5)
    # __read_edge(n)

    print(f'\[')
    pass


