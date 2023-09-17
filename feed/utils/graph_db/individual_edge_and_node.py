from feed.utils.graph_db.abstract_by_graph_db import AbstractNode, AbstractEdge, Option
from neo4j import Session


class _Restricted:
    class User:
        class FollowsUser(AbstractNode):
            from_node = Option.NodeLabel.User
            edge = Option.EdgeLabel.FOLLOWS
            to_node = Option.NodeLabel.User
        class LikesFeedPost(AbstractNode):
            from_node = Option.NodeLabel.User
            edge = Option.EdgeLabel.LIKES
            to_node = Option.NodeLabel.FeedPost
        class LikesTaskFinish(AbstractNode):
            from_node = Option.NodeLabel.User
            edge = Option.EdgeLabel.LIKES
            to_node = Option.NodeLabel.TaskFinish
        class BookmarksRoutine(AbstractNode):
            from_node = Option.NodeLabel.User
            edge = Option.EdgeLabel.BOOKMARKS
            to_node = Option.NodeLabel.Routine
    
class Node:
    class User(_Restricted.User, AbstractNode):
        from_node = Option.NodeLabel.User
        edge = Option.EdgeLabel.FOLLOWS
        to_node = Option.NodeLabel.User
        @classmethod
        def read_follows_user_id(cls, session: Session, from_rdb_id: int) -> list[int]:
            cls.FollowsUser.read_rdb_id_of_destination(session, from_rdb_id)
            return
        @classmethod
        def read_followed_user_id(cls, session: Session, to_rdb_id: int) -> list[int]:
            cls.FollowsUser.read_rdb_id_of_starting(session, to_rdb_id)
            return
        @classmethod
        def read_likes_feed_post_id(cls, session: Session, from_rdb_id: int) -> list[int]:
            cls.LikesFeedPost.read_rdb_id_of_destination(session, from_rdb_id)
            return
        @classmethod
        def read_likes_task_finish_id(cls, session: Session, from_rdb_id: int) -> list[int]:
            cls.LikesTaskFinish.read_rdb_id_of_destination(session, from_rdb_id)
            return
        @classmethod
        def read_bookmarks_routine_id(cls, session: Session, from_rdb_id: int) -> list[int]:
            cls.BookmarksRoutine.read_rdb_id_of_destination(session, from_rdb_id)
            return
    class FeedPost(AbstractNode):
        from_node = Option.NodeLabel.FeedPost
        edge = Option.EdgeLabel.LIKES
        to_node = Option.NodeLabel.User
        @classmethod
        def read_liked_by_user_id(cls, session: Session, feed_post_id):
            cls.edge = Option.EdgeLabel.LIKES
            cls.read_rdb_id_of_starting(session, feed_post_id)
            return
    class TaskFinish(AbstractNode):
        from_node = Option.NodeLabel.FeedPost
        edge = Option.EdgeLabel.LIKES
        to_node = Option.NodeLabel.User
        @classmethod
        def read_liked_by_user_id(cls, session: Session, feed_post_id):
            cls.read_rdb_id_of_starting(session, feed_post_id)
            return
    class Routine(AbstractNode):
        from_node = Option.NodeLabel.FeedPost
        edge = Option.EdgeLabel.BOOKMARKS
        to_node = Option.NodeLabel.User
        @classmethod
        def read_bookmarked_by_user_id(cls, session: Session, feed_post_id):
            cls.read_rdb_id_of_starting(session, feed_post_id)
            return

class _RestrictedAbstractEdge:
    class AbstractFOLLOWS(AbstractEdge):
        from_node = Option.NodeLabel.User
        edge = Option.EdgeLabel.LIKES
        to_node = Option.NodeLabel.User
        pg_tx_by_create = Option.PgRunSetsForEdge.create_follows
        pg_tx_by_delete = Option.PgRunSetsForEdge.delete_follows
    class AbstractLIKES(AbstractEdge):
        from_node = Option.NodeLabel.User
        edge = Option.EdgeLabel.LIKES
        pg_tx_by_create = Option.PgRunSetsForEdge.create_likes
        pg_tx_by_delete = Option.PgRunSetsForEdge.delete_likes
    class AbstractBOOKMARKS(AbstractEdge):
        from_node = Option.NodeLabel.User
        edge = Option.EdgeLabel.BOOKMARKS
        pg_tx_by_create = Option.PgRunSetsForEdge.create_bookmarks
        pg_tx_by_delete = Option.PgRunSetsForEdge.delete_bookmarks      

class EdgeByTargetNode:
    class FollowsUser(_RestrictedAbstractEdge.AbstractFOLLOWS):
        pass        
    class LikesFeedPost(_RestrictedAbstractEdge.AbstractLIKES):
        to_node = Option.NodeLabel.FeedPost
    class LikesTaskFinish(_RestrictedAbstractEdge.AbstractLIKES):
        to_node = Option.NodeLabel.TaskFinish
    class BookmarksRoutine(_RestrictedAbstractEdge.AbstractBOOKMARKS):
        to_node = Option.NodeLabel.Routine    
     