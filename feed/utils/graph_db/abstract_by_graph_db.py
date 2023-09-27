from neo4j import Session, Transaction
from supply_auth.models import User as UserModel
from feed.models import FeedPost as FeedPostModel
from routine.models import TaskFinish as TaskFinishModel
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
        def __init__(self) -> None:
            self.table: UserModel | FeedPostModel | TaskFinishModel | RoutineModel = None
        def create_follows(self, *rdb_id: tuple[int]) -> None:
            """ フォロー・フォロワー数を加算 (rdb_id[0] = from_user_id, rdb_id[1] = to_user_id) """
            from_u: UserModel = UserModel.objects.get(id=rdb_id[0])
            to_u:   UserModel = UserModel.objects.get(id=rdb_id[1])
            from_u.following += 1 
            to_u.follower    += 1 
            from_u.save()
            to_u.save()
        def delete_follows(self, *rdb_id: tuple[int]) -> None:
            """ フォロー・フォロワー数を減算 (rdb_id[0] = from_user_id, rdb_id[1] = to_user_id) """
            from_u: UserModel = self.table.objects.get(id=rdb_id[0])
            to_u:   UserModel = self.table.objects.get(id=rdb_id[1])
            from_u.following -= 1 
            to_u.follower    -= 1 
            from_u.save()
            to_u.save()
        def create_likes(self, *rdb_id: tuple[int]) -> None:
            """ いいね数を加算 """
            p: FeedPostModel | TaskFinishModel = self.table.objects.get(id=rdb_id[0])
            p.like_num += 1 
            p.save()
        def delete_likes(self, *rdb_id: tuple[int]) -> None:
            """ いいね数を減算 """
            p: FeedPostModel | TaskFinishModel = self.table.objects.get(id=rdb_id[0])
            p.like_num -= 1 
            p.save()
        def create_bookmarks(self, *rdb_id: tuple[int]) -> None:
            """ ブックマーク数を加算 """
            p: RoutineModel = self.table.objects.get(id=rdb_id[0])
            p.bookmark_num += 1
            p.save
        def delete_bookmarks(self, *rdb_id: tuple[int]) -> None:
            """ ブックマーク数を減算 """
            p: RoutineModel = self.table.objects.get(id=rdb_id[0])
            p.bookmark_num -= 1
            p.save
        
class AbstractNode:
    """ ノードを用いた汎用的な操作を行うための関数群を持った抽象クラス

    Attributes:
        from_node (String): 対象となるノード、もしくは関係付け時の発生点となるノードのラベル名 \n
        edge (String): 関係付け時のエッジのラベル名 \n
        to_node (String): 関係付け時の目的点となるノードのラベル名 \n
    """
    def __init__(self) -> None:
        self._Tx.from_node = ''
        self._Tx.edge = ''
        self._Tx.to_node = ''
    class _Tx:
        """ トランザクションの設計 """
        from_node = ''
        edge = ''
        to_node = ''
        @classmethod
        def create(cls, tx: Transaction, rdb_id: int) -> None:
            check_cypher = f'MATCH (n:{cls.from_node} {{rdb_id: $rdb_id}}) RETURN n'
            result = tx.run(check_cypher, rdb_id=rdb_id).single()
            # すでに作成済みのノードである場合
            if result is not None:
                cypher = 'MATCH (n) WHERE n.rdb_id = $rdb_id AND false RETURN n '
                tx.run(cypher, rdb_id=rdb_id)
            else:
                cypher = f'CREATE (:{cls.from_node} {{rdb_id: $rdb_id}})'
                tx.run(cypher, rdb_id=rdb_id)
        @classmethod
        def delete(cls, tx: Transaction, rdb_id: int) -> None:
            check_cypher = f'MATCH (n:{cls.from_node} {{rdb_id: $rdb_id}}) RETURN n'
            result = tx.run(check_cypher, rdb_id=rdb_id).single()
            # すでに消去済みのノードである場合
            if result is None:
                cypher = 'MATCH (n) WHERE n.rdb_id = $rdb_id AND false RETURN n '
                tx.run(cypher, rdb_id=rdb_id)
            else:
                cypher = f'MATCH (u:{cls.from_node} {{rdb_id: $rdb_id}}) DETACH DELETE u '
                tx.run(cypher, rdb_id=rdb_id)
        @classmethod
        def _read_rdb_ids_of_destination(cls, tx: Transaction, from_rdb_id: int) -> list[int]:
            """あるノード X に対して、その X からエッジを方向づけている全てのノードの rdb_id を取得するトランザクション"""
            print(f'{cls.from_node}, {cls.edge}, {cls.to_node}')
            cypher = f'MATCH (x:{cls.from_node} {{rdb_id: $from_rdb_id}})-[f:{cls.edge}]->(y:{cls.to_node}) RETURN y.rdb_id'
            result = tx.run(cypher, from_rdb_id=from_rdb_id)
            return [record['y.rdb_id'] for record in result]
        @classmethod
        def _read_rdb_ids_of_starting(cls, tx: Transaction, to_rdb_id: int) -> list[int]:
            """あるノード X に対して、その X にエッジを方向づけている全てのノードの rdb_id を取得するトランザクション"""
            print(f'{cls.from_node}, {cls.edge}, {cls.to_node}')
            cypher = f'MATCH (x:{cls.from_node} {{rdb_id: $to_rdb_id}})<-[f:{cls.edge}]-(y:{cls.to_node}) RETURN y.rdb_id'
            result = tx.run(cypher, to_rdb_id=to_rdb_id)
            return [record['y.rdb_id'] for record in result]
    def create(self, session: Session, rdb_id: int) -> None:
        session.execute_write(self._Tx.create, rdb_id)       
    def delete(self, session: Session, rdb_id: int) -> None:
        session.execute_write(self._Tx.delete, rdb_id)       
    def _read_rdb_ids_of_destination(cls, session: Session, from_rdb_id: int) -> list[int]:
        """ (e.g.) IF (X {rdb_id: 1}) -[F]-> (X {rdb_id: 2}) THEN RETURN [2] """
        return session.execute_read(cls._Tx._read_rdb_ids_of_destination, from_rdb_id)  
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
    def __init__(self) -> None:
        self._Tx.from_node = ''
        self._Tx.edge = ''
        self._Tx.to_node = ''
        self._Tx.pg_tx_by_create = lambda *args: args
        self._Tx.pg_tx_by_delete = lambda *args: args
    class _Tx:
        from_node = ''
        edge = ''
        to_node = ''
        pg_tx_by_create = lambda *args: args
        pg_tx_by_delete = lambda *args: args
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
        @classmethod
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
                    f'MATCH (x:{cls.from_node} {{rdb_id: $from_rdb_id}})-[r:{cls.edge}]->(y:{cls.to_node} {{rdb_id: $to_rdb_id}}) '
                    f'DELETE r'
                )
                cypher = delete_cypher
                tx.run(cypher, from_rdb_id=from_rdb_id, to_rdb_id=to_rdb_id)
                cls.pg_tx_by_delete(from_rdb_id, to_rdb_id)
    def _create(self, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
        session.execute_write(self._Tx._create, from_rdb_id, to_rdb_id)
    def _delete(self, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
        session.execute_write(self._Tx._delete, from_rdb_id, to_rdb_id)
    

