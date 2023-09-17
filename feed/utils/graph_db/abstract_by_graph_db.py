from neo4j import Session, Transaction
from django.db import transaction
from django.db.backends.base.base import BaseDatabaseWrapper as BDW
from supplyAuth.models import User as UserModel
from feed.models import FeedPost as FeedPostModel
from routine.models import TaskRecord as TaskFinishModel
from routine.models import Routine as RoutineModel
from typing import Final


class Option:
    class NodeLabel():
        User: Final        = 'User'
        FeedPost: Final    = 'FeedPost'
        TaskFinish: Final  = 'TaskFinish'
        Routine: Final     = 'Routine'
    class EdgeLabel():
        FOLLOWS: Final   = 'FOLLOWS'
        LIKES: Final     = 'LIKES'
        BOOKMARKS: Final = 'BOOKMARKS' 
    class RDBTable():
        User: Final        = UserModel
        FeedPost: Final    = FeedPostModel
        TaskFinish: Final  = TaskFinishModel
        Routine: Final     = RoutineModel
    class PgRunSetsForEdge:
        """ RDB 操作用関数群 """
        table: UserModel | FeedPostModel | TaskFinishModel | RoutineModel = None
        @classmethod
        def create_follows(cls, from_rdb_id: int, to_rdb_id: int) -> None:
            """ フォロー・フォロワー数を加算 """
            from_u: UserModel = UserModel.objects.get(id=from_rdb_id)
            to_u:   UserModel = UserModel.objects.get(id=to_rdb_id)
            from_u.following += 1 
            to_u.follower    += 1 
            from_u.save()
            to_u.save()
            return
        @classmethod
        def delete_follows(cls, from_rdb_id: int, to_rdb_id: int) -> None:
            """ フォロー・フォロワー数を減算 """
            from_u: UserModel = UserModel.objects.get(id=from_rdb_id)
            to_u:   UserModel = UserModel.objects.get(id=to_rdb_id)
            from_u.following -= 1 
            to_u.follower    -= 1 
            from_u.save()
            to_u.save()
            return
        @classmethod
        def create_likes(cls, *rdb_id: int) -> None:
            """ いいね数を加算 """
            p: cls.table = cls.table.objects.get(id=rdb_id[0])
            p.like_num += 1 
            p.save()
            return
        @classmethod
        def delete_likes(cls, *rdb_id: int) -> None:
            """ いいね数を減算 """
            p: cls.table = cls.table.objects.get(id=rdb_id[0])
            p.like_num -= 1 
            p.save()
            return
        @classmethod
        def create_bookmarks(cls, *rdb_id: int) -> None:
            """ ブックマーク数を加算 """
            p: cls.table = cls.table.objects.get(id=rdb_id[0])
            p.bookmark_num += 1
            p.save
            return
        @classmethod
        def delete_bookmarks(cls, *rdb_id: int) -> None:
            """ ブックマーク数を減算 """
            p: cls.table = cls.table.objects.get(id=rdb_id[0])
            p.bookmark_num -= 1
            p.save
            return

class AbstractNode:
    """ ノードを用いた汎用的な操作を行うための関数群を持った抽象クラス

    Attributes:
        from_node (String): 対象となるノード、もしくは関係付け時の発生点となるノードのラベル名 \n
        edge (String): 関係付け時のエッジのラベル名 \n
        to_node (String): 関係付け時の目的点となるノードのラベル名 \n
    """
    from_node = ''
    edge = ''
    to_node = ''
    props = {}
    class _Tx:
        """ トランザクションの設計 """
        @classmethod
        def create(cls, tx: Transaction, rdb_id: int, props: dict) -> None:
            cypher = f'CREATE (:{props["from_node"]} {{rdb_id: $rdb_id}})'
            tx.run(cypher, rdb_id=rdb_id)
            return 
        @classmethod
        def delete(cls, tx: Transaction, rdb_id: int, props: dict) -> None:
            cypher = f'MATCH (u:{props["from_node"]} {{rdb_id: $rdb_id}}) DETACH DELETE u'
            tx.run(cypher, rdb_id=rdb_id)
            return 
        @classmethod
        def read_rdb_id_of_destination(cls, tx: Transaction, from_rdb_id: int, props: dict) -> list[int]:
            """ あるノードに対して、そのノードからエッジを方向づけられているノードの RDB 特定用 id を一覧取得するトランザクション """
            cypher = (
                f'MATCH (x:{props["from_node"]} {{rdb_id: $from_rdb_id}})-[:{props["edge"]}]->(y:{props["to_node"]}) '
                'RETURN y.rdb_id as rdb_id'
            )
            result = tx.run(cypher, from_rdb_id=from_rdb_id)
            return [record['rdb_id'] for record in result]
        @classmethod
        def read_rdb_id_of_starting(cls, tx: Transaction, to_rdb_id: int, props: dict) -> list[int]:
            """ あるノードに対して、エッジを方向づけているノードの RDB 特定用 id を一覧取得するトランザクション"""
            cypher = (
                f'MATCH (x:{props["from_node"]})-[:{props["edge"]}]->(y:{props["to_node"]} {{rdb_id: $to_rdb_id}}) '
                f'RETURN x.rdb_id AS rdb_id'
            )
            result = tx.run(cypher, to_rdb_id=to_rdb_id)
            return [record['rdb_id'] for record in result]
    @classmethod
    def set_class_props(cls):
        cls.props['from_node'] = cls.from_node
        cls.props['edge'] = cls.edge
        cls.props['to_node'] = cls.to_node
    @classmethod
    def create(cls, session: Session, rdb_id: int) -> None:
        cls.set_class_props()
        session.execute_write(cls._Tx.create, rdb_id, cls.props)       
        return
    @classmethod
    def delete(cls, session: Session, rdb_id: int) -> None:
        cls.set_class_props()
        session.execute_write(cls._Tx.delete, rdb_id, cls.props)       
        return
    @classmethod 
    def read_rdb_id_of_destination(cls, session: Session, from_rdb_id: int) -> list[int]:
        """ (e.g.) (X {rdb_id: 1}) -[F]-> (X {rdb_id: 2}) AND (X {rdb_id: 1}) -[F]-> (X {rdb_id: 3}) の場合、戻り値は [2, 3] """
        cls.set_class_props()
        return session.execute_read(cls._Tx.read_rdb_id_of_destination, from_rdb_id, cls.props)  
    @classmethod
    def read_rdb_id_of_starting(cls, session: Session, to_rdb_id: int) -> list[int]:
        """ (e.g.) (X {rdb_id: 2}) -[F]-> (X {rdb_id: 1}) AND (X {rdb_id: 3}) -[F]-> (X {rdb_id: 1}) の場合、戻り値は [2, 3] """
        cls.set_class_props()
        return session.execute_read(cls._Tx.read_rdb_id_of_starting, to_rdb_id, cls.props)


class AbstractEdge:
    """ エッジを用いた汎用的な操作を行うための関数群を持った抽象クラス

    Attributes:

        from_node (String): 対象となるノード、もしくは関係付け時の発生点となるノードのラベル名 \n
        edge (String): 関係付け時のエッジのラベル名 \n
        to_node (String): 関係付け時の目的点となるノードのラベル名 \n
        pg_tx_by_create (Function): エッジ作成時に必要となる RDB 操作用のトランザクション関数 \n
        pg_tx_by_delete (Function): エッジ削除時に必要となる RDB 操作用のトランザクション関数 \n
    """
    from_node = ''
    edge = ''
    to_node = ''
    pg_tx_by_create = lambda: None
    pg_tx_by_delete = lambda: None
    props = {}
    class _Tx:
        @classmethod
        def create(cls, tx: Transaction, pg_driver: BDW, from_rdb_id: int, to_rdb_id: int, props: dict) -> None:
            # アクション済みかを調べる Cypher
            check_cypher = (
                        f'MATCH (x:{props["from_node"]} {{rdb_id: $from_rdb_id}})-[:{props["edge"]}]->(y:{props["to_node"]} {{rdb_id: $to_rdb_id}}) '
                        'RETURN COUNT(*) AS num'
                    )
            check_result = tx.run(check_cypher, from_rdb_id=from_rdb_id, to_rdb_id=to_rdb_id).single()
            num = check_result['num']
            # アクション済みでなかったならばアクション
            if num == 0:
                create_cypher = (
                            f'MATCH (x:{props["from_node"]} {{rdb_id: $from_rdb_id}}), (y:{props["to_node"]} {{rdb_id: $to_rdb_id}}) '
                            f'CREATE (x)-[:{props["to_node"]}]->(y) '
                        )
                cypher = create_cypher
                try:
                    tx.run(cypher, from_rdb_id=from_rdb_id, to_rdb_id=to_rdb_id)
                    with transaction.atomic():
                        props['pg_tx_by_create'](from_rdb_id, to_rdb_id)
                except Exception as e:
                    raise Exception(f'Control Error: The rollback has taken place. \ndetail: {e}')
            return
        def delete(cls, tx: Transaction, pg_driver: BDW, from_rdb_id: int, to_rdb_id: int, props: dict) -> int:
            # アクション済みかを調べる Cypher
            check_cypher = (
                        f'MATCH (x:{props["from_node"]} {{rdb_id: $from_rdb_id}})-[:{props["edge"]}]->(y:{props["to_node"]} {{rdb_id: $to_rdb_id}}) '
                        'RETURN COUNT(*) AS num'
                    )
            check_result = tx.run(check_cypher, from_rdb_id=from_rdb_id, to_rdb_id=to_rdb_id).single()
            num = check_result['num']
            # アクション済みであったならばアクション取り消し
            if num > 0:
                delete_cypher = (
                            f'MATCH (x:{props["from_node"]} {{rdb_id: $from_rdb_id}})-[:{props["edge"]}]->(y:{props["to_node"]} {{rdb_id: $to_rdb_id}}) '
                            'DELETE r'
                        )
                cypher = delete_cypher
                try:
                    tx.run(cypher, from_rdb_id=from_rdb_id, to_rdb_id=to_rdb_id)
                    with transaction.atomic():
                        props['pg_tx_by_delete']
                except Exception as e:
                    raise Exception(f'Control Error: The rollback has taken place. \ndetail: {e}')
            return
    @classmethod
    def set_class_props(cls):
        cls.props['from_node'] = cls.from_node
        cls.props['edge'] = cls.edge
        cls.props['to_node'] = cls.to_node
        cls.props['pg_tx_by_create'] = cls.pg_tx_by_create
        cls.props['pg_tx_by_delete'] = cls.pg_tx_by_delete
    @classmethod
    def create(cls, session: Session, pg_driver: BDW, from_rdb_id: int, to_rdb_id: int) -> None:
        cls.set_class_props()
        try:
            session.execute_write(cls._Tx.create, pg_driver, from_rdb_id, to_rdb_id, cls.props)
        except Exception as e:
            print(f"An error occurred during the transaction: {e}")
        return   
    @classmethod
    def delete(cls, session: Session, pg_driver: BDW, from_rdb_id: int, to_rdb_id: int) -> None:
        cls.set_class_props()
        try:
            session.execute_write(cls._Tx.delete, pg_driver, from_rdb_id, to_rdb_id, cls.props)
        except Exception as e:
            print(f"An error occurred during the transaction: {e}")
        return
    

