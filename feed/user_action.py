import random
from functools import partial
from secret import LocalNeo4jDB as Neo4j
from neo4j import GraphDatabase, Driver, Transaction, Session
from django.db import transaction, connection
from django.db.backends.base.base import BaseDatabaseWrapper as BDW
from supplyAuth.models import User as UserModel
from feed.models import FeedPost as FeedPostModel

#* PostgreSQL, Neo4j データベースに接続するために必要な情報を設定
pg_connection: BDW = connection['default']
driver: Driver = GraphDatabase.driver(Neo4j.uri, auth=(Neo4j.user, Neo4j.password))


class Node:
    """ ノードまたはノードの属性の作成、取得、更新、削除 """
    @staticmethod
    def _delete_all() -> None:
        """ 全ノード削除 `実行` """
        with driver.session() as session:
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
    class User:
        """ Label: User """
        class _TX:
            """ トランザクションの設計 """
            @staticmethod
            def create(tx: Transaction, user_id: int) -> None:
                """ user_id となるノードを作成 """
                cypher = 'CREATE (:User {user_id: $user_id})'
                tx.run(cypher, user_id=user_id)
                return 
            @staticmethod
            def delete(tx: Transaction, user_id: int) -> None:
                """ user_id が一致するノードを削除 """
                cypher = 'MATCH (u:User {user_id: $user_id}) DETACH DELETE u'
                tx.run(cypher, user_id=user_id)
                return 
            @staticmethod
            def read_follows_user_ids(tx: Transaction, user_id: int) -> list[int]:
                """ フォロー中のユーザー ID 一覧を取得 """
                cypher = (
                    'MATCH (x:User {user_id: $user_id})-[:FOLLOWS]->(y:User) '
                    'RETURN y.user_id AS following_id'
                )
                result = tx.run(cypher, user_id=user_id)
                return [record['following_id'] for record in result]
            @staticmethod
            def read_followed_user_ids(tx: Transaction, user_id: int) -> list[int]:
                """ フォロワーの ID 一覧を取得 """
                cypher = (
                    'MATCH (x:User {user_id: $user_id})<-[:FOLLOWS]-(y:User) '
                    'RETURN y.user_id as follower_id'
                )
                result = tx.run(cypher, user_id=user_id)
                return [record['follower_id'] for record in result]
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
        @classmethod
        def create(cls, session: Session, user_id: int) -> None:
            """ user_id となるノードを作成実行 """
            session.execute_write(cls._TX.create, user_id)       
            return
        def delete(cls, session: Session, user_id: int) -> None:
            """ user_id が一致するノードを削除実行 """
            session.execute_write(cls._TX.delete, user_id)       
            return
        @classmethod
        def read_follows_user_ids(cls, session: Session, user_id: int) -> list[int]:
            """ Return: フォロー中のユーザー ID 一覧 """
            return session.execute_read(cls._TX.read_follows_user_ids, user_id)
        @classmethod 
        def read_followed_user_ids(cls, session: Session, user_id: int) -> list[int]:
            """ Return: フォロワーの ID 一覧 """
            return session.execute_read(cls._TX.read_followed_user_ids, user_id)
        @classmethod
        def read_likes_feed_post_ids(cls, session: Session, user_id: int) -> list[int]:
            """ Return: このユーザーがいいねしている Feed 投稿の ID 一覧 (降順) """
            # 投稿 ID が大きいことを最新の投稿物と仮定して最新のそれを取得しやすいよう降順にソート
            post_ids: list[int] = session.execute_read(cls._TX.read_likes_feed_post_ids, user_id)
            return post_ids.sort(reverse=True)
        @classmethod
        def read_bookmarks_feed_post_ids(cls, session: Session, user_id: int) -> list[int]:
            """ Return: このユーザーがブックマークしている Feed 投稿の ID 一覧 (降順) """
            # 投稿 ID が大きいことを最新の投稿物と仮定して最新のそれを取得しやすいよう降順にソート
            post_ids: list[int] = session.execute_read(cls._TX.read_bookmarks_feed_post_ids, user_id)
            return post_ids.sort(reverse=True)
    class FeedPost:
        """ Label: FeedPost """
        class _TX:
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
            session.execute_write(cls._TX.create, post_id)
            return
        @classmethod
        def delete(cls, session: Session, post_id: int) -> None:
            """ post_id が一致するノードを削除実行 """
            session.execute_write(cls._TX.delete, post_id)
            return         
        @classmethod
        def read_liked_user_ids(cls, session: Session, post_id: int) -> list[int]:
            """ Return: その投稿にいいねしているユーザーの ID 一覧 """
            return session.execute_read(cls._TX.read_liked_user_ids, post_id)
        @classmethod
        def read_bookmarked_user_ids(cls, session: Session, post_id: int) -> list[int]:
            """ Return: その投稿をブックマークしているユーザーの ID 一覧 """
            return session.execute_read(cls._TX.read_bookmarked_user_ids, post_id)


class _UtilityAboutEdge:
    class PGRun:
        def create_follows(from_user_id: int, to_user_id: int) -> None:
            from_u: UserModel = UserModel.objects.get(id=from_user_id)
            to_u:   UserModel = UserModel.objects.get(id=to_user_id)
            from_u.following += 1 
            to_u.follower    += 1 
            from_u.save()
            to_u.save()
            return
        def delete_follows(from_user_id: int, to_user_id: int) -> None:
            from_u: UserModel = UserModel.objects.get(id=from_user_id)
            to_u:   UserModel = UserModel.objects.get(id=to_user_id)
            from_u.following -= 1 
            to_u.follower    -= 1 
            from_u.save()
            to_u.save()
            return
        def create_likes(to_feed_post_id: int) -> None:
            p: FeedPostModel = FeedPostModel.objects.get(id=to_feed_post_id)
            p.like_num      += 1 
            p.save()
            return
        def delete_likes(to_feed_post_id: int) -> None:
            p: FeedPostModel = FeedPostModel.objects.get(id=to_feed_post_id)
            p.like_num      -= 1 
            p.save()
            return
        def create_bookmarks(to_feed_post_id: int) -> None:
            p: FeedPostModel = FeedPostModel.objects.get(id=to_feed_post_id)
            p.bookmark_num  += 1
            p.save
            return
        def delete_bookmarks(to_feed_post_id: int):
            p: FeedPostModel = FeedPostModel.objects.get(id=to_feed_post_id)
            p.bookmark_num  -= 1
            p.save
            return
    @classmethod
    def create_by_user_action(cls, tx: Transaction, from_user_id: int, to_id: int, label: str) -> None:
        """ `rdb_tx` is the RDB transaction function to be linked. `label` is the edge label name. """
        # 必要な値をセット
        if(label=='FOLLOWS'):
            to_node_label = 'User' 
            to_id_name = 'user_id' 
            pg_tx = partial(cls.PGRun.create_follows, from_user_id=from_user_id, to_user_id=to_id)
        elif(label=='LIKES'):
            to_node_label = 'FeedPost'
            to_id_name = 'post_id'
            pg_tx = partial(cls.PGRun.create_likes, to_feed_post_id=to_id)
        elif(label=='BOOKMARKS'):
            to_node_label = 'FeedPost'
            to_id_name = 'post_id'
            pg_tx = partial(cls.PGRun.create_bookmarks, to_feed_post_id=to_id)
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
    def delete_by_user_action(cls, tx: Transaction, from_user_id: int, to_id: int, label: str) -> int:
        """ `rdb_tx` is the RDB transaction function to be linked. `label` is the edge label name. """
        # 必要な値をセット
        if(label=='FOLLOWS'):
            to_node_label = 'User' 
            to_id_name = 'user_id' 
            pg_tx = partial(cls.PGRun.delete_follows, from_user_id=from_user_id, to_user_id=to_id)
        elif(label=='LIKES'):
            to_node_label = 'FeedPost'
            to_id_name = 'post_id'
            pg_tx = partial(cls.PGRun.delete_likes, to_feed_post_id=to_id)
        elif(label=='BOOKMARKS'):
            to_node_label = 'FeedPost'
            to_id_name = 'post_id'
            pg_tx = partial(cls.PGRun.delete_bookmarks, to_feed_post_id=to_id)
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


class Edge:
    """ エッジの作成、取得、更新、削除 """
    class FOLLOWS:
        """ Label: FOLLOWS """
        class _TX:
            """ トランザクションの設計 """
            @staticmethod
            def create(tx: Transaction, from_user_id: int, to_user_id: int) -> None:
                """ フォロー """
                _UtilityAboutEdge.create_by_user_action(tx, from_user_id, to_user_id, label='FOLLOWS')
                return
            @staticmethod
            def delete(tx: Transaction, from_user_id: int, to_user_id: int) -> None:
                """ フォロー解除 """
                _UtilityAboutEdge.delete_by_user_action(tx, from_user_id, to_user_id, label='FOLLOWS')
                return
        @classmethod
        def create(cls, session: Session, from_user_id: int, to_user_id: int) -> None:
            """ フォロー実行 """
            session.execute_write(cls._TX.create, from_user_id, to_user_id)
            return 
        @classmethod
        def delete(cls, session: Session, from_user_id: int, to_user_id: int) -> None:
            """ フォロー解除実行 """
            session.execute_write(cls._TX.create, from_user_id, to_user_id)
            return
    class LIKES:
        """ Label: LIKES """
        class _TX:
            """ トランザクションの設計 """
            @staticmethod
            def create_to_feed(tx: Transaction, from_user_id: int, to_feed_post_id: int) -> None:
                """ いいね """
                _UtilityAboutEdge.create_by_user_action(tx, from_user_id, to_feed_post_id, label='LIKES')
                return
            @staticmethod
            def delete_to_feed(tx: Transaction, from_user_id: int, to_feed_post_id: int) -> None:
                """ いいね取り消し """
                _UtilityAboutEdge.delete_by_user_action(tx, from_user_id, to_feed_post_id, label='LIKES')
                return
        @classmethod
        def create_to_feed(cls, session: Session, from_user_id: int, to_user_id: int) -> None:
            """ いいね実行 """
            session.execute_write(cls._TX.create_to_feed, from_user_id, to_user_id)
            return
        @classmethod
        def delete_to_feed(cls, session: Session, from_user_id: int, to_user_id: int) -> None:
            """ いいね取り消し実行 """
            session.execute_write(cls._TX.create_to_feed, from_user_id, to_user_id)
            return
    class BOOKMARKS:
        """ Label: BOOKMARKS """
        class _TX:
            """ トランザクションの設計 """
            @staticmethod
            def create_to_feed(tx: Transaction, from_user_id: int, to_feed_post_id: int) -> None:
                """ ブックマークへ追加 """
                _UtilityAboutEdge.create_by_user_action(tx, from_user_id, to_feed_post_id, label='BOOKMARKS')
                return
            @staticmethod
            def delete_to_feed(tx: Transaction, from_user_id: int, to_feed_post_id: int) -> None:
                """ ブックマーク削除 """
                _UtilityAboutEdge.delete_by_user_action(tx, from_user_id, to_feed_post_id, label='BOOKMARKS')
                return
        @classmethod
        def create_to_feed(cls, session: Session, to_feed_post_id: int) -> None:
            """ ブックマークへ追加実行 """
            session.execute_write(cls._TX.create_to_feed, to_feed_post_id)
            return
        @classmethod
        def delete_to_feed(cls, session: Session, to_feed_post_id: int) -> None:
            """ ブックマーク削除実行 """
            session.execute_write(cls._TX.create_to_feed, to_feed_post_id)
            return
        

#* テスト
if __name__ == '__main__':
    with driver.session() as session: 
        n = 15
        for i in range(1, n + 1):
            Node.User.create(session, i)
            Node.FeedPost.create(session, i)
            Edge.FOLLOWS.create(session, *random.sample(tuple(range(1, n - 10)), 2))            
            Edge.LIKES.create_to_feed(session, *random.sample(tuple(range(1, n - 10)), 2))            
            Edge.BOOKMARKS.create_to_feed(session, *random.sample(tuple(range(1, n - 10)), 2))   

        def __read_edge(n: int):
            #WARNING 存在しないノードを対象に探索していたとしてもエラーは吐かない
            for user_id in range(1, n):
                print(f'{user_id} -> {Node.User.read_follows_user_ids(session, user_id)}')
            for user_id in range(1, n):
                print(f'{user_id} <- {Node.User.read_followed_user_ids(session, user_id)}')

        Node._delete_all()
        __read_edge(n)


    YELLOW, RESET = '\033[93m', '\033[0m'    
    print(f'{YELLOW} succeeded {RESET}')
    pass
