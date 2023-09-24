from neo4j import Session, Transaction
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
            p: FeedPostModel | TaskFinishModel = cls.table.objects.get(id=rdb_id[0])
            p.like_num += 1 
            p.save()
            return
        @classmethod
        def delete_likes(cls, *rdb_id: int) -> None:
            """ いいね数を減算 """
            p: FeedPostModel | TaskFinishModel = cls.table.objects.get(id=rdb_id[0])
            p.like_num -= 1 
            p.save()
            return
        @classmethod
        def create_bookmarks(cls, *rdb_id: int) -> None:
            """ ブックマーク数を加算 """
            p: RoutineModel = cls.table.objects.get(id=rdb_id[0])
            p.bookmark_num += 1
            p.save
            return
        @classmethod
        def delete_bookmarks(cls, *rdb_id: int) -> None:
            """ ブックマーク数を減算 """
            p: RoutineModel = cls.table.objects.get(id=rdb_id[0])
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
    class _Tx:
        """ トランザクションの設計 """
        from_node = ''
        edge = ''
        to_node = ''
        @classmethod
        def create(cls, tx: Transaction, rdb_id: int) -> None:
            cypher = f'CREATE (:{cls.from_node} {{rdb_id: $rdb_id}})'
            tx.run(cypher, rdb_id=rdb_id)
            return 
        @classmethod
        def delete(cls, tx: Transaction, rdb_id: int) -> None:
            cypher = f'MATCH (u:{cls.from_node} {{rdb_id: $rdb_id}}) DETACH DELETE u'
            tx.run(cypher, rdb_id=rdb_id)
            return 
        @classmethod
        def _read_rdb_ids_of_destination(cls, tx: Transaction, from_rdb_id: int) -> list[int]:
            """ あるノードに対して、そのノードからエッジを方向づけられているノードの RDB 特定用 id を一覧取得するトランザクション """
            cypher = (
                f'MATCH (x:{cls.from_node} {{rdb_id: $from_rdb_id}})-[:{cls.edge}]->(y:{cls.to_node}) '
                'RETURN y.rdb_id as rdb_id'
            )
            result = tx.run(cypher, from_rdb_id=from_rdb_id)
            return [record['rdb_id'] for record in result]
        @classmethod
        def _read_rdb_ids_of_starting(cls, tx: Transaction, to_rdb_id: int) -> list[int]:
            """ あるノードに対して、エッジを方向づけているノードの RDB 特定用 id を一覧取得するトランザクション"""
            cypher = (
                f'MATCH (x:{cls.from_node})-[:{cls.from_node}]->(y:{cls.to_node} {{rdb_id: $to_rdb_id}}) '
                f'RETURN x.rdb_id AS rdb_id'
            )
            result = tx.run(cypher, to_rdb_id=to_rdb_id)
            return [record['rdb_id'] for record in result]
    @classmethod
    def create(cls, session: Session, rdb_id: int) -> None:
        session.execute_write(cls._Tx.create, rdb_id)       
        return
    @classmethod
    def delete(cls, session: Session, rdb_id: int) -> None:
        session.execute_write(cls._Tx.delete, rdb_id)       
        return
    @classmethod 
    def _read_rdb_ids_of_destination(cls, session: Session, from_rdb_id: int) -> list[int]:
        """ (e.g.) IF (X {rdb_id: 1}) -[F]-> (X {rdb_id: 2}) THEN RETURN [2] """
        return session.execute_read(cls._Tx._read_rdb_ids_of_destination, from_rdb_id)  
    @classmethod
    def _read_rdb_ids_of_starting(cls, session: Session, to_rdb_id: int) -> list[int]:
        """ (e.g.) IF (X {rdb_id: 1}) -[F]-> (X {rdb_id: 2}) THEN RETURN [1] """
        return session.execute_read(cls._Tx._read_rdb_ids_of_starting, to_rdb_id)


class AbstractEdge:
    """ エッジを用いた汎用的な操作を行うための関数群を持った抽象クラス

    Attributes:

        from_node (String): 対象となるノード、もしくは関係付け時の発生点となるノードのラベル名 \n
        edge (String): 関係付け時のエッジのラベル名 \n
        to_node (String): 関係付け時の目的点となるノードのラベル名 \n
        pg_tx_by_create (Function): エッジ作成時に必要となる RDB 操作用のトランザクション関数 \n
        pg_tx_by_delete (Function): エッジ削除時に必要となる RDB 操作用のトランザクション関数 \n
    """
    class _Tx:
        from_node = ''
        edge = ''
        to_node = ''
        pg_tx_by_create = lambda: None
        pg_tx_by_delete = lambda: None
        props = {}
        @classmethod
        def _create(cls, tx: Transaction, from_rdb_id: int, to_rdb_id: int) -> None:
            # アクション済みかを調べる Cypher
            check_cypher = (
                        f'MATCH (x:{cls.from_node} {{rdb_id: $from_rdb_id}})-[:{cls.edge}]->(y:{cls.to_node} {{rdb_id: $to_rdb_id}}) '
                        'RETURN COUNT(*) AS num'
                    )
            check_result = tx.run(check_cypher, from_rdb_id=from_rdb_id, to_rdb_id=to_rdb_id).single()
            num = check_result['num']
            # アクション済みでなかったならばアクション
            if num == 0:
                create_cypher = (
                            f'MATCH (x:{cls.from_node} {{rdb_id: $from_rdb_id}}), (y:{cls.to_node} {{rdb_id: $to_rdb_id}}) '
                            f'CREATE (x)-[:{cls.edge}]->(y) '
                        )
                cypher = create_cypher
                tx.run(cypher, from_rdb_id=from_rdb_id, to_rdb_id=to_rdb_id)
                cls.pg_tx_by_create(from_rdb_id, to_rdb_id)
            return
        def _delete(cls, tx: Transaction, from_rdb_id: int, to_rdb_id: int) -> int:
            # アクション済みかを調べる Cypher
            check_cypher = (
                        f'MATCH (x:{cls.from_node} {{rdb_id: $from_rdb_id}})-[:{cls.edge}]->(y:{cls.to_node} {{rdb_id: $to_rdb_id}}) '
                        'RETURN COUNT(*) AS num'
                    )
            check_result = tx.run(check_cypher, from_rdb_id=from_rdb_id, to_rdb_id=to_rdb_id).single()
            num = check_result['num']
            # アクション済みであったならばアクション取り消し
            if num > 0:
                delete_cypher = (
                            f'MATCH (x:{cls.from_node} {{rdb_id: $from_rdb_id}})-[:{cls.edge}]->(y:{cls.to_node} {{rdb_id: $to_rdb_id}}) '
                            'DELETE r'
                        )
                cypher = delete_cypher
                tx.run(cypher, from_rdb_id=from_rdb_id, to_rdb_id=to_rdb_id)
                cls.pg_tx_by_delete(from_rdb_id, to_rdb_id)
            return
    @classmethod
    def _create(cls, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
        session.execute_write(cls._Tx._create, from_rdb_id, to_rdb_id)
        return   
    @classmethod
    def _delete(cls, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
        session.execute_write(cls._Tx._delete, from_rdb_id, to_rdb_id)
        return
    

