import random
from functools import partial
from feed.ff_related import FOLLOWS, User
from feed.user_actions import BOOKMARKS, LIKES, FeedPost
from secret import LocalNeo4jDB as Neo4j
from neo4j import GraphDatabase, Driver, Session, Transaction
from django.db import transaction, connection
from django.db.backends.base.base import BaseDatabaseWrapper as BDW
from supplyAuth.models import User as UserModel
from feed.models import FeedPost as FeedPostModel

#* PostgreSQL, Neo4j データベースに接続するために必要な情報を設定
pg_connection: BDW = connection['default']
driver: Driver = GraphDatabase.driver(Neo4j.uri, auth=(Neo4j.user, Neo4j.password))


def _delete_all(session: Session) -> None:
    """ 全ノード削除 `実行` """
    # ノードのラベルを全種類取得する関数
    def _tx_get_node_labels(tx: Transaction):
        cypher = 'MATCH (n) UNWIND labels(n) AS label RETURN DISTINCT label'
        result = tx.run(cypher)
        return [record['label'] for record in result]
    # あるラベルのノードを全て削除する関数
    def _tx_delete_nodes_with_label(tx: Transaction, label: str):
        cypher = f'MATCH (u:{label}) DETACH DELETE u'
        tx.run(cypher)
    # ラベルを一括取得
    labels = session.execute_read(_tx_get_node_labels)
    # ラベルごとにノードを削除
    for node_labels in labels:
        session.execute_write(_tx_delete_nodes_with_label, node_labels)
    return


class GenericEdge:
    """ 汎用的な Edge に関する機能の枠組み """
    class PgRun:
        """ RDB 操作用関数群 """
        @staticmethod
        def create_follows(from_user_id: int, to_user_id: int) -> None:
            """ フォロー・フォロワー数を加算 """
            from_u: UserModel = UserModel.objects.get(id=from_user_id)
            to_u:   UserModel = UserModel.objects.get(id=to_user_id)
            from_u.following += 1 
            to_u.follower    += 1 
            from_u.save()
            to_u.save()
            return
        @staticmethod
        def delete_follows(from_user_id: int, to_user_id: int) -> None:
            """ フォロー・フォロワー数を減算 """
            from_u: UserModel = UserModel.objects.get(id=from_user_id)
            to_u:   UserModel = UserModel.objects.get(id=to_user_id)
            from_u.following -= 1 
            to_u.follower    -= 1 
            from_u.save()
            to_u.save()
            return
        @staticmethod
        def create_likes(to_feed_post_id: int) -> None:
            """ いいね数を加算 """
            p: FeedPostModel = FeedPostModel.objects.get(id=to_feed_post_id)
            p.like_num      += 1 
            p.save()
            return
        @staticmethod
        def delete_likes(to_feed_post_id: int) -> None:
            """ いいね数を減算 """
            p: FeedPostModel = FeedPostModel.objects.get(id=to_feed_post_id)
            p.like_num      -= 1 
            p.save()
            return
        @staticmethod
        def create_bookmarks(to_feed_post_id: int) -> None:
            """ ブックマーク数を加算 """
            p: FeedPostModel = FeedPostModel.objects.get(id=to_feed_post_id)
            p.bookmark_num  += 1
            p.save
            return
        @staticmethod
        def delete_bookmarks(to_feed_post_id: int):
            """ ブックマーク数を減算 """
            p: FeedPostModel = FeedPostModel.objects.get(id=to_feed_post_id)
            p.bookmark_num  -= 1
            p.save
            return
    @classmethod
    def create(cls, tx: Transaction, from_user_id: int, to_id: int, label: str) -> None:
        """ `rdb_tx` is the RDB transaction function to be linked. `label` is the edge label name. """
        # 必要な値をセット
        if(label=='FOLLOWS'):
            to_node_label = 'User' 
            to_id_name = 'user_id' 
            pg_tx = partial(cls.PgRun.create_follows, from_user_id=from_user_id, to_user_id=to_id)
        elif(label=='LIKES'):
            to_node_label = 'FeedPost'
            to_id_name = 'post_id'
            pg_tx = partial(cls.PgRun.create_likes, to_feed_post_id=to_id)
        elif(label=='BOOKMARKS'):
            to_node_label = 'FeedPost'
            to_id_name = 'post_id'
            pg_tx = partial(cls.PgRun.create_bookmarks, to_feed_post_id=to_id)
        # アクション済みかを調べる Cypher
        check_cypher = (
                    f'MATCH (x:User {{user_id: $from_user_id}})-[:{label}]->(y:{to_node_label} {{{to_id_name}: $to_id}}) '
                    'RETURN COUNT(*) AS num'
                )
        check_result = tx.run(check_cypher, from_user_id=from_user_id, to_id=to_id).single()
        num = check_result['num']
        # アクション済みでなかったならばアクション
        if num == 0:
            create_cypher = (
                        f'MATCH (x:User {{user_id: $from_user_id}}), (y:{to_node_label} {{{to_id_name}: $to_id}}) '
                        f'CREATE (x)-[:{label}]->(y) '
                    )
            cypher = create_cypher
            try:
                tx.run(cypher, from_user_id=from_user_id, to_id=to_id)
                with transaction.atomic():
                    pg_tx()
            except Exception as e:
                print(f'Transaction Failed: {e}')
                tx.rollback()
                pg_connection.rollback() 
        return num
    @classmethod
    def delete(cls, tx: Transaction, from_user_id: int, to_id: int, label: str) -> int:
        """ `rdb_tx` is the RDB transaction function to be linked. `label` is the edge label name. """
        # 必要な値をセット
        if(label=='FOLLOWS'):
            to_node_label = 'User' 
            to_id_name = 'user_id' 
            pg_tx = partial(cls.PgRun.delete_follows, from_user_id=from_user_id, to_user_id=to_id)
        elif(label=='LIKES'):
            to_node_label = 'FeedPost'
            to_id_name = 'post_id'
            pg_tx = partial(cls.PgRun.delete_likes, to_feed_post_id=to_id)
        elif(label=='BOOKMARKS'):
            to_node_label = 'FeedPost'
            to_id_name = 'post_id'
            pg_tx = partial(cls.PgRun.delete_bookmarks, to_feed_post_id=to_id)
        # アクション済みかを調べる Cypher
        check_cypher = (
                    f'MATCH (x:User {{user_id: $from_user_id}})-[:{label}]->(y:{to_node_label} {{{to_id_name}: $to_id}}) '
                    'RETURN COUNT(*) AS num'
                )
        check_result = tx.run(check_cypher, from_user_id=from_user_id, to_id=to_id).single()
        num = check_result['num']
        # アクション済みであったならばアクション取り消し
        if num > 0:
            delete_cypher = (
                        f'MATCH (x:User {{user_id: $from_user_id}})-[:{label}]->(y:{to_node_label} {{{to_id_name}: $to_user_id}}) '
                        'DELETE r'
                    )
            cypher = delete_cypher
            try:
                tx.run(cypher, from_user_id=from_user_id, to_id=to_id)
                with transaction.atomic():
                    pg_tx()
            except Exception as e:
                print(f'Transaction Failed: {e}')
                tx.rollback()
                pg_connection.rollback() 
        return
    

#* テスト
if __name__ == '__main__':
    with driver.session() as session: 
        n = 15
        for i in range(1, n + 1):
            User.create(session, i)
            FeedPost.create(session, i)
            FOLLOWS.create(session, *random.sample(tuple(range(1, n - 10)), 2))            
            LIKES.create_to_feed(session, *random.sample(tuple(range(1, n - 10)), 2))            
            BOOKMARKS.create_to_feed(session, *random.sample(tuple(range(1, n - 10)), 2))   

        def _read_edge(session: Session, n: int):
            #WARNING 存在しないノードを対象に探索していたとしてもエラーは吐かない
            for user_id in range(1, n):
                print(f'{user_id} -> {User.read_follows_user_ids(session, user_id)}')
            for user_id in range(1, n):
                print(f'{user_id} <- {User.read_followed_user_ids(session, user_id)}')

        _delete_all(session)
        _read_edge(session, n)
        

    YELLOW, RESET = '\033[93m', '\033[0m'    
    print(f'{YELLOW} succeeded {RESET}')
    pass