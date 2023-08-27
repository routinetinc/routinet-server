import random
from neo4j import GraphDatabase, Transaction
from secret import LocalNeo4jDB as Neo4j

""" [命名規則]
    トランザクションを定義する関数は名前に <tx_> という接頭辞を持つ
    ノードの作成、更新、削除を定義する関数は名前に <create, update, delete> という単語を持つ
    エッジの紐づけ、解除を定義する関数は名前に <set, unset> という単語を持つ
    読み取りのための関数は名前に <read> という単語を持つ
    関数は関連するノードまたはエッジのラベル名を名前に持つ
"""

#* Neo4jデータベースに接続
driver = GraphDatabase.driver(Neo4j.uri, auth=(Neo4j.user, Neo4j.password))

#* 全ノード削除関数
def _delete_all_nodes():
    with driver.session() as session:
        # ノードのラベルを全種類取得する関数
        def _tx_get_node_labels(tx: Transaction):
            query = "MATCH (n) UNWIND labels(n) AS label RETURN DISTINCT label"
            result = tx.run(query)
            return [record["label"] for record in result]
        # あるラベルのノードを全て削除する関数
        def _tx_delete_nodes_with_label(tx: Transaction, label):
            query = f"MATCH (u:{label}) DETACH DELETE u"
            tx.run(query)
        # ラベルを一括取得
        labels = session.execute_read(_tx_get_node_labels)
        # ラベルごとにノードを削除
        for node_labels in labels:
            session.execute_write(_tx_delete_nodes_with_label, node_labels)

#* ノード :UserFF 作成関数
def tx_create_userff(tx: Transaction, user_id: int, following: int, followers: int):
    query = "CREATE (:UserFF {user_id: $user_id, following: $following, followers: $followers})"
    tx.run(query, user_id=user_id, following=following, followers=followers)

#* FOLLOWS 関係付け関数
def tx_set_follows(tx: Transaction, from_user_id: int, to_user_id: int):
    # フォロー関係の存在を確認するクエリ
    check_query = (
        "MATCH (x:UserFF {user_id: $from_user_id})-[:FOLLOWS]->(y:UserFF {user_id: $to_user_id}) "
        "RETURN COUNT(*) AS follow_count"
    )
    check_result = tx.run(check_query, from_user_id=from_user_id, to_user_id=to_user_id).single()
    follow_count = check_result["follow_count"]
    # フォローしていなかった場合
    if follow_count == 0:
        # フォローする
        create_query = (
            "MATCH (x:UserFF {user_id: $from_user_id}), (y:UserFF {user_id: $to_user_id}) "
            "CREATE (x)-[:FOLLOWS]->(y) "
        )
        # 自身のフォロー人数、相手のフォロワー人数をカウントアップ
        update_query = (
            "WITH x, y "
            "MATCH (u:UserFF {user_id: $from_user_id}) "
            "SET u.following = u.following + 1 "
            "WITH u "
            "MATCH (v:UserFF {user_id: $to_user_id}) "
            "SET v.followers = v.followers + 1 "
        )
        query = create_query + update_query
        tx.run(query, from_user_id=from_user_id, to_user_id=to_user_id)
    

#* FOLLOWS 関係解除関数
def tx_unset_follows(tx: Transaction, from_user_id: int, to_user_id: int):
    # フォロー関係が存在するかを確認するクエリ
    check_query = (
        "MATCH (x:UserFF {user_id: $from_user_id})-[:FOLLOWS]->(y:UserFF {user_id: $to_user_id}) "
        "RETURN COUNT(*) AS follow_count"
    )
    check_result = tx.run(check_query, from_user_id=from_user_id, to_user_id=to_user_id).single()
    follow_count = check_result["follow_count"]
    # フォローしていた場合
    if follow_count > 0:
        # フォロー解除
        delete_query = (
            "MATCH (x:UserFF {user_id: $from_user_id})-[:FOLLOWS]->(y:UserFF {user_id: $to_user_id}) "
            "DELETE r"
        )
        # 自身のフォロー人数、相手のフォロワー人数をカウントダウン
        update_query = (
            "WITH x, y "
            "MATCH (u:UserFF {user_id: $from_user_id}) "
            "SET u.following = u.following - 1 "
            "WITH u "
            "MATCH (v:UserFF {user_id: $to_user_id}) "
            "SET v.followers = v.followers - 1 "
        )
        query = delete_query + update_query
        tx.run(query, from_user_id=from_user_id, to_user_id=to_user_id)



#* あるユーザーのフォロー先のユーザーIDを一覧取得
def tx_get_following_ids(tx: Transaction, user_id: int):
    query = (
        "MATCH (x:UserFF {user_id: $user_id})-[:FOLLOWS]->(y:UserFF) "
        "RETURN y.user_id AS following_id"
    )
    result = tx.run(query, user_id=user_id)
    return [record["following_id"] for record in result]
def get_following_ids(user_id: int):
    with driver.session() as session:
        following_ids = session.execute_read(tx_get_following_ids, user_id)
    return following_ids 


#* あるユーザーのフォロワーのユーザーIDを一覧取得
def tx_get_follower_ids(tx: Transaction, user_id: int):
    query = (
        "MATCH (x:UserFF {user_id: $user_id})<-[:FOLLOWS]-(y:UserFF) "
        "RETURN y.user_id as follower_id"
    )
    result = tx.run(query, user_id=user_id)
    return [record["follower_id"] for record in result]
def get_follower_ids(user_id: int):
    with driver.session() as session:
        follower_ids = session.execute_read(tx_get_follower_ids, user_id)
    return follower_ids      



n = 15
if __name__ == "__main__":
    def _create_node_and_set_edge(n: int):
        txs  = [(tx_create_userff, i, 0, 0) for i in range(1, n + 1)]
        txs += [(tx_set_follows, *random.sample(tuple(range(1, n - 10)), 2)) for _ in range(1, 5 + 1)]
        with driver.session() as session:
            for tx in txs:
                session.execute_write(*tx)
    def _read_edge(n: int):
        for user_id in range(1, n):
            # get_following_ids 関数の仕様上、毎回 driver.session() が発生していることに留意
            print(str(user_id) + " -> " + str(get_following_ids(user_id)))
        for user_id in range(1, n):
            print(str(user_id) + " <- " + str(get_follower_ids(user_id)))

    # _delete_all_nodes()
    # _create_node_and_set_edge(n)
    _read_edge(n)

    pass



