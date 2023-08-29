import random
from neo4j import GraphDatabase, Transaction
from secret import LocalNeo4jDB as Neo4j


#* Neo4jデータベースに接続するための設定
driver = GraphDatabase.driver(Neo4j.uri, auth=(Neo4j.user, Neo4j.password))

class Node:
    """ ノードまたはノードの属性の作成、取得、更新、削除 """
    @classmethod
    def _delete_all(cls):
        """ 全ノード削除 `実行` """
        with driver.session() as session:
            # ノードのラベルを全種類取得する関数
            def _tx_get_node_labels(tx: Transaction):
                query = 'MATCH (n) UNWIND labels(n) AS label RETURN DISTINCT label'
                result = tx.run(query)
                return [record['label'] for record in result]
            # あるラベルのノードを全て削除する関数
            def _tx_delete_nodes_with_label(tx: Transaction, label: str):
                query = f'MATCH (u:{label}) DETACH DELETE u'
                tx.run(query)
            # ラベルを一括取得
            labels = session.execute_read(_tx_get_node_labels)
            # ラベルごとにノードを削除
            for node_labels in labels:
                session.execute_write(_tx_delete_nodes_with_label, node_labels)
            return
    class UserFF:
        """ Label: UserFF """
        class TX:
            """ トランザクションの設計 """
            @classmethod
            def create(cls, tx: Transaction, user_id: int, following: int, followers: int) -> None:
                """ ノード作成 """
                query = 'CREATE (:UserFF {user_id: $user_id, following: $following, followers: $followers})'
                tx.run(query, user_id=user_id, following=following, followers=followers)
                return 
            @classmethod
            def delete(cls, tx: Transaction, user_id):
                """ ノード削除 """
                query = 'MATCH (u:UserFF {user_id: $user_id}) DETACH DELETE u'
                tx.run(query, user_id=user_id)
                return 
            @classmethod
            def read_following_ids(cls, tx: Transaction, user_id: int) -> list[int]:
                """ フォローしているユーザーの ID 一覧を取得 """
                query = (
                    'MATCH (x:UserFF {user_id: $user_id})-[:FOLLOWS]->(y:UserFF) '
                    'RETURN y.user_id AS following_id'
                )
                result = tx.run(query, user_id=user_id)
                return [record['following_id'] for record in result]
            @classmethod
            def read_follower_ids(cls, tx: Transaction, user_id: int) -> None:
                """ フォロワーの ID 一覧を取得 """
                query = (
                    'MATCH (x:UserFF {user_id: $user_id})<-[:FOLLOWS]-(y:UserFF) '
                    'RETURN y.user_id as follower_id'
                )
                result = tx.run(query, user_id=user_id)
                return [record['follower_id'] for record in result]
        @classmethod
        def read_following_ids(cls, user_id: int):
            """ Return: フォローしているユーザーの ID 一覧 """
            with driver.session() as session:
                following_ids = session.execute_read(cls.TX.read_following_ids, user_id)
            return following_ids 
        @classmethod
        def read_follower_ids(cls, user_id: int):
            """ Return: フォロワーの ID 一覧 """
            with driver.session() as session:
                follower_ids = session.execute_read(cls.TX.read_follower_ids, user_id)
            return follower_ids  
        


class Edge:
    """ エッジの作成、取得、更新、削除 """
    class FOLLOWS:
        """ Label: FOLLOWS """
        class TX:
            """ トランザクションの設計 """
            @classmethod
            def create(cls, tx: Transaction, from_user_id: int, to_user_id: int):
                """ フォロー """
                check_query = (
                    'MATCH (x:UserFF {user_id: $from_user_id})-[:FOLLOWS]->(y:UserFF {user_id: $to_user_id}) '
                    'RETURN COUNT(*) AS follow_count'
                )
                check_result = tx.run(check_query, from_user_id=from_user_id, to_user_id=to_user_id).single()
                follow_count = check_result['follow_count']
                # フォローしていなかった場合
                if follow_count == 0:
                    # フォローする
                    create_query = (
                        'MATCH (x:UserFF {user_id: $from_user_id}), (y:UserFF {user_id: $to_user_id}) '
                        'CREATE (x)-[:FOLLOWS]->(y) '
                    )
                    # 自身のフォロー人数、相手のフォロワー人数をカウントアップ
                    update_query = (
                        'WITH x, y '
                        'MATCH (u:UserFF {user_id: $from_user_id}) '
                        'SET u.following = u.following + 1 '
                        'WITH u '
                        'MATCH (v:UserFF {user_id: $to_user_id}) '
                        'SET v.followers = v.followers + 1 '
                    )
                    query = create_query + update_query
                    tx.run(query, from_user_id=from_user_id, to_user_id=to_user_id)
                return
            @classmethod
            def delete(cls, tx: Transaction, from_user_id: int, to_user_id: int):
                """ フォロー解除 """
                # フォロー関係が存在するかを確認するクエリ
                check_query = (
                    'MATCH (x:UserFF {user_id: $from_user_id})-[:FOLLOWS]->(y:UserFF {user_id: $to_user_id}) '
                    'RETURN COUNT(*) AS follow_count'
                )
                check_result = tx.run(check_query, from_user_id=from_user_id, to_user_id=to_user_id).single()
                follow_count = check_result['follow_count']
                # フォローしていた場合
                if follow_count > 0:
                    # フォロー解除
                    delete_query = (
                        'MATCH (x:UserFF {user_id: $from_user_id})-[:FOLLOWS]->(y:UserFF {user_id: $to_user_id}) '
                        'DELETE r'
                    )
                    # 自身のフォロー人数、相手のフォロワー人数をカウントダウン
                    update_query = (
                        'WITH x, y '
                        'MATCH (u:UserFF {user_id: $from_user_id}) '
                        'SET u.following = u.following - 1 '
                        'WITH u '
                        'MATCH (v:UserFF {user_id: $to_user_id}) '
                        'SET v.followers = v.followers - 1 '
                    )
                    query = delete_query + update_query
                    tx.run(query, from_user_id=from_user_id, to_user_id=to_user_id)
                return

class Execute:
    """ 一回のセッションで複数のトランザクションを実行 """
    @classmethod
    def write_multi(cls, txs: list[tuple]):
        with driver.session() as session:
            for tx in txs:
                session.execute_write(*tx)
        return 
    @classmethod
    def read_multi(cls, txs: list[tuple]):
        stores = []
        with driver.session() as session:
            for tx in txs:
                stores.append = session.execute_read(*tx)
        return stores
    @classmethod
    def write_single(cls, *tx):
        with driver.session() as session:
            session.execute_write(*tx)
        return 
    @classmethod
    def read_single(cls, *tx):
        with driver.session() as session:
            store = session.execute_write(*tx)
        return store

#* テスト
n = 15
if __name__ == '__main__':
    txs  = [(Node.UserFF.TX.create, i, 0, 0) for i in range(1, n + 1)]
    txs += [(Edge.FOLLOWS.TX.create, *random.sample(tuple(range(1, n - 10)), 2)) for _ in range(1, 5 + 1)]
    def __read_edge(n: int):
        for user_id in range(1, n):
            try: 
                # get_following_ids 関数の仕様上、毎回 driver.session() が発生していることに留意
                print(str(user_id) + ' -> ' + str(Node.UserFF.read_following_ids(user_id)))
            except:
                pass
        for user_id in range(1, n):
            try:
                print(str(user_id) + ' <- ' + str(Node.UserFF.read_follower_ids(user_id)))
            except:
                pass

    Node._delete_all()
    Execute.write_multi(txs)
    Execute.write_single(Node.UserFF.TX.delete, 5)
    __read_edge(n)

    pass



