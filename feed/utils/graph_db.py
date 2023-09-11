import random
from functools import partial
from feed.ff_related import FOLLOWS, User
from feed.user_actions import FeedPost
from secret import LocalNeo4jDB as Neo4j
from neo4j import GraphDatabase, Driver, Session, Transaction
from django.db import transaction, connection
from django.db.backends.base.base import BaseDatabaseWrapper as BDW
from supplyAuth.models import User as UserModel
from feed.models import FeedPost as FeedPostModel
from routine.models import TaskRecord as TaskFinishModel
from routine.models import Routine as RoutineModel

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
    def _tx_delete_nodes_with_label(tx: Transaction, node_label: str):
        cypher = f'MATCH (u:{node_label}) DETACH DELETE u'
        tx.run(cypher)
    # ラベルを一括取得
    labels = session.execute_read(_tx_get_node_labels)
    # ラベルごとにノードを削除
    for node_label in labels:
        session.execute_write(_tx_delete_nodes_with_label, node_label)
    return


class GenericEdge:
    """ 汎用的な Edge に関する機能の枠組み """
    class _PgRun:
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
        def create_likes(to_feed_post_id: int, node_label: str) -> None:
            """ いいね数を加算 """
            if(node_label=='FeedPost'):
                p: FeedPostModel = FeedPostModel.objects.get(id=to_feed_post_id)
            elif(node_label=='TaskFinish'):
                p: TaskFinishModel = TaskFinishModel.objects.get(id=to_feed_post_id)
            elif(node_label=='Routine'):
                p: RoutineModel = RoutineModel.objects.get(id=to_feed_post_id)
            else:
                raise Exception('Invalid Value Error: The node label name does not exist.')
            p.like_num      += 1 
            p.save()
            return
        @staticmethod
        def delete_likes(to_feed_post_id: int, node_label: str) -> None:
            """ いいね数を減算 """
            if(node_label=='FeedPost'):
                p: FeedPostModel = FeedPostModel.objects.get(id=to_feed_post_id)
            elif(node_label=='TaskFinish'):
                p: TaskFinishModel = TaskFinishModel.objects.get(id=to_feed_post_id)
            elif(node_label=='Routine'):
                p: RoutineModel = RoutineModel.objects.get(id=to_feed_post_id)
            else:
                raise Exception('Invalid Value Error: The node label name does not exist.')
            p.like_num      -= 1 
            p.save()
            return
        @staticmethod
        def create_bookmarks(to_feed_post_id: int, node_label: str) -> None:
            """ ブックマーク数を加算 """
            if(node_label=='FeedPost'):
                p: FeedPostModel = FeedPostModel.objects.get(id=to_feed_post_id)
            elif(node_label=='TaskFinish'):
                p: TaskFinishModel = TaskFinishModel.objects.get(id=to_feed_post_id)
            elif(node_label=='Routine'):
                p: RoutineModel = RoutineModel.objects.get(id=to_feed_post_id)
            else:
                raise Exception('Invalid Value Error: The node label name does not exist.')
            p.bookmark_num  += 1
            p.save
            return
        @staticmethod
        def delete_bookmarks(to_feed_post_id: int, node_label: str):
            """ ブックマーク数を減算 """
            if(node_label=='FeedPost'):
                p: FeedPostModel = FeedPostModel.objects.get(id=to_feed_post_id)
            elif(node_label=='TaskFinish'):
                p: TaskFinishModel = TaskFinishModel.objects.get(id=to_feed_post_id)
            elif(node_label=='Routine'):
                p: RoutineModel = RoutineModel.objects.get(id=to_feed_post_id)
            else:
                raise Exception('Invalid Value Error: The node label name does not exist.')            
            p: FeedPostModel = FeedPostModel.objects.get(id=to_feed_post_id)
            p.bookmark_num  -= 1
            p.save
            return
    @classmethod
    def create(cls, tx: Transaction, from_user_id: int, to_id: int, edge_label: str, is_to_node_label_feed_post: bool = False) -> None:
        """ `rdb_tx` is the RDB transaction function to be linked. """
        # 必要な値をセット
        if(edge_label=='FOLLOWS'):
            to_node_label = 'User'
            to_id_name = 'user_id' 
            pg_tx = partial(cls._PgRun.create_follows, from_user_id=from_user_id, to_user_id=to_id)
        elif(edge_label=='LIKES'):
            to_node_label = 'FeedPost' if(is_to_node_label_feed_post) else 'TaskFinish'
            to_id_name = 'id_for_rdb'
            pg_tx = partial(cls._PgRun.create_likes, to_feed_post_id=to_id, to_node_label=to_node_label)
        elif(edge_label=='BOOKMARKS'):
            to_node_label = 'Rouine'
            to_id_name = 'id_for_rdb'
            pg_tx = partial(cls._PgRun.create_bookmarks, to_feed_post_id=to_id, to_node_label=to_node_label)
        else:
            raise Exception('Invalid Value Error: The edge label name does not exist.')
        # アクション済みかを調べる Cypher
        check_cypher = (
                    f'MATCH (x:User {{user_id: $from_user_id}})-[:{edge_label}]->(y:{to_node_label} {{{to_id_name}: $to_id}}) '
                    'RETURN COUNT(*) AS num'
                )
        check_result = tx.run(check_cypher, from_user_id=from_user_id, to_id=to_id).single()
        num = check_result['num']
        # アクション済みでなかったならばアクション
        if num == 0:
            create_cypher = (
                        f'MATCH (x:User {{user_id: $from_user_id}}), (y:{to_node_label} {{{to_id_name}: $to_id}}) '
                        f'CREATE (x)-[:{edge_label}]->(y) '
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
                raise Exception('Control Error: The rollback has taken place.')
        return num
    @classmethod
    def delete(cls, tx: Transaction, from_user_id: int, to_id: int, edge_label: str, is_to_node_label_feed_post: bool = False) -> int:
        """ `rdb_tx` is the RDB transaction function to be linked. """
        # 必要な値をセット
        if(edge_label=='FOLLOWS'):
            to_node_label = 'User' 
            to_id_name = 'user_id' 
            pg_tx = partial(cls._PgRun.delete_follows, from_user_id=from_user_id, to_user_id=to_id)
        elif(edge_label=='LIKES'):
            to_node_label = 'FeedPost' if(is_to_node_label_feed_post) else 'TaskFinish'
            to_id_name = 'id_for_rdb'
            pg_tx = partial(cls._PgRun.delete_likes, to_feed_post_id=to_id, to_node_label=to_node_label)
        elif(edge_label=='BOOKMARKS'):
            to_node_label = 'FeedPost'
            to_id_name = 'id_for_rdb'
            pg_tx = partial(cls._PgRun.delete_bookmarks, to_feed_post_id=to_id, to_node_label=to_node_label)
        else:
            raise Exception('Invalid Value Error: The edge_label name does not exist.')
        # アクション済みかを調べる Cypher
        check_cypher = (
                    f'MATCH (x:User {{user_id: $from_user_id}})-[:{edge_label}]->(y:{to_node_label} {{{to_id_name}: $to_id}}) '
                    'RETURN COUNT(*) AS num'
                )
        check_result = tx.run(check_cypher, from_user_id=from_user_id, to_id=to_id).single()
        num = check_result['num']
        # アクション済みであったならばアクション取り消し
        if num > 0:
            delete_cypher = (
                        f'MATCH (x:User {{user_id: $from_user_id}})-[:{edge_label}]->(y:{to_node_label} {{{to_id_name}: $to_user_id}}) '
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
                raise Exception('Control Error: The rollback has taken place.')
        return
    

#* テスト
if __name__ == '__main__':
    with driver.session() as session: 
        n = 15
        for i in range(1, n + 1):
            User.create(session, i)
            FeedPost.create(session, i)
            FOLLOWS.create(session, *random.sample(tuple(range(1, n - 10)), 2))            

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