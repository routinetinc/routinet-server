from secret import LocalNeo4jDB as Neo4j
from neo4j import GraphDatabase, Driver, Transaction, Session
from django.db import connection
from django.db.backends.base.base import BaseDatabaseWrapper as BDW
from feed.utils.graph_db.individual_edge_and_node import Node, EdgeByTargetNode

class FeedPost(Node.FeedPost):
    @classmethod
    def read_likes_feed_post_id(cls, session: Session, from_user_id: int) -> list[int]:
        Node.User.LikesFeedPost.read_rdb_id_of_destination(session, from_user_id)
        return
    class Relation(EdgeByTargetNode.FollowsUser):
        pass

class TaskFinish(Node.FeedPost):
    @classmethod
    def read_likes_task_finish_id(cls, session: Session, from_user_id: int) -> list[int]:
        Node.User.LikesTaskFinish.read_rdb_id_of_destination(session, from_user_id)
        return
    class Relation(EdgeByTargetNode.FollowsUser):
        pass

class Routine(Node.FeedPost):
    @classmethod
    def read_bookmarks_routine_id(cls, session: Session, from_user_id: int) -> list[int]:
        Node.User.BookmarksRoutine.read_rdb_id_of_destination(session, from_user_id)
    class Relation(EdgeByTargetNode.FollowsUser):
        pass
