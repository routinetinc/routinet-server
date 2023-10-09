from feed.utils.graph_db.abstract_by_graph_db import AbstractNode, AbstractEdge, Option
from neo4j import Session


class Node:
    class User(AbstractNode):
        def __init__(self) -> None:
            super().__init__()
            self._Tx.from_node = Option.NodeLabel.User
            self._Tx.edge      = Option.EdgeLabel.FOLLOWS
            self._Tx.to_node   = Option.NodeLabel.User
        def read_follows_user_ids(self, session: Session, from_rdb_id: int) -> list[int]:
            self._Tx.edge, self._Tx.to_node = Option.EdgeLabel.FOLLOWS, Option.NodeLabel.User
            result = self._read_rdb_ids_of_destination(session, from_rdb_id)
            self._Tx.edge, self._Tx.to_node = Option.EdgeLabel.FOLLOWS, Option.NodeLabel.User
            return result
        def read_followed_user_ids(self, session: Session, to_rdb_id: int) -> list[int]:
            self._Tx.edge, self._Tx.to_node = Option.EdgeLabel.FOLLOWS, Option.NodeLabel.User
            result = self._read_rdb_ids_of_starting(session, to_rdb_id)
            self._Tx.edge, self._Tx.to_node = Option.EdgeLabel.FOLLOWS, Option.NodeLabel.User
            return result
        def read_likes_feed_post_ids(self, session: Session, from_rdb_id: int) -> list[int]:
            self._Tx.edge, self._Tx.to_node = Option.EdgeLabel.LIKES, Option.NodeLabel.FeedPost
            result = self._read_rdb_ids_of_destination(session, from_rdb_id)
            self._Tx.edge, self._Tx.to_node = Option.EdgeLabel.FOLLOWS, Option.NodeLabel.User
            return result
        def read_likes_task_finish_ids(self, session: Session, from_rdb_id: int) -> list[int]:
            self._Tx.edge, self._Tx.to_node = Option.EdgeLabel.LIKES, Option.NodeLabel.TaskFinish
            result = self._read_rdb_ids_of_destination(session, from_rdb_id)
            self._Tx.edge, self._Tx.to_node = Option.EdgeLabel.FOLLOWS, Option.NodeLabel.User
            return result
        def read_bookmarks_routine_ids(self, session: Session, from_rdb_id: int) -> list[int]:
            self._Tx.edge, self._Tx.to_node = Option.EdgeLabel.BOOKMARKS, Option.NodeLabel.Routine
            result = self._read_rdb_ids_of_destination(session, from_rdb_id)
            return result  
    class Routine(AbstractNode):
        def __init__(self):
            super().__init__()
            # from_node = FeedPost であるのは node_create 関数に影響を与えるためであり、 read 関数などは通常通り動作する。
            self._Tx.from_node = Option.NodeLabel.Routine
            self._Tx.edge      = Option.EdgeLabel.BOOKMARKS
            self._Tx.to_node   = Option.NodeLabel.User
        def read_bookmarks_routine_ids(self, session: Session, from_user_id: int) -> list[int]:
            self._Tx.from_node, self._Tx.to_node = Option.NodeLabel.User, Option.NodeLabel.Routine
            result = self._read_rdb_ids_of_destination(session, from_user_id)
            self._Tx.from_node, self._Tx.to_node = Option.NodeLabel.Routine, Option.NodeLabel.User
            return result
        def read_bookmarked_user_ids(self, session: Session, to_routine_id) -> list[int]:
            self._Tx.from_node, self._Tx.to_node = Option.NodeLabel.User, Option.NodeLabel.Routine
            result = self._read_rdb_ids_of_starting(session, to_routine_id)
            self._Tx.from_node, self._Tx.to_node = Option.NodeLabel.Routine, Option.NodeLabel.User
            return result
    class TaskFinish(AbstractNode):
        def __init__(self) -> None:
            super().__init__()
            # from_node = FeedPost であるのは node_create 関数に影響を与えるためであり、 read 関数などは通常通り動作する。
            self._Tx.from_node = Option.NodeLabel.TaskFinish
            self._Tx.edge      = Option.EdgeLabel.LIKES
            self._Tx.to_node   = Option.NodeLabel.User
        def read_likes_task_finish_ids(self, session: Session, from_user_id: int) -> list[int]:
            self._Tx.from_node, self._Tx.to_node = Option.NodeLabel.User, Option.NodeLabel.TaskFinish
            result = self._read_rdb_ids_of_destination(session, from_user_id)
            self._Tx.from_node, self._Tx.to_node = Option.NodeLabel.TaskFinish, Option.NodeLabel.User
            return result
        def read_liked_user_ids(self, session: Session, to_task_finish_id) -> list[int]:
            self._Tx.from_node, self._Tx.to_node = Option.NodeLabel.User, Option.NodeLabel.TaskFinish
            result = self._read_rdb_ids_of_starting(session, to_task_finish_id)
            self._Tx.from_node, self._Tx.to_node = Option.NodeLabel.TaskFinish, Option.NodeLabel.User
            return result
    class TaskFinishComment(AbstractNode):
        def __init__(self) -> None:
            super().__init__()
            # from_node = FeedPost であるのは node_create 関数に影響を与えるためであり、 read 関数などは通常通り動作する。
            self._Tx.from_node = Option.NodeLabel.TaskFinishComment
            self._Tx.edge      = Option.EdgeLabel.LIKES
            self._Tx.to_node   = Option.NodeLabel.User 
        def read_likes_task_finish_comment_ids(self, session: Session, from_user_id: int) -> list[int]:
            self._Tx.from_node, self._Tx.to_node = Option.NodeLabel.User, Option.NodeLabel.TaskFinishComment
            result = self._read_rdb_ids_of_destination(session, from_user_id)
            self._Tx.from_node, self._Tx.to_node = Option.NodeLabel.TaskFinishComment, Option.NodeLabel.User
            return result
        def read_liked_user_ids(self, session: Session, to_task_finish_id) -> list[int]:
            self._Tx.from_node, self._Tx.to_node = Option.NodeLabel.User, Option.NodeLabel.TaskFinishComment
            result = self._read_rdb_ids_of_starting(session, to_task_finish_id)
            self._Tx.from_node, self._Tx.to_node = Option.NodeLabel.TaskFinishComment, Option.NodeLabel.User
            return result  
    class FeedPost(AbstractNode):
        def __init__(self) -> None:
            super().__init__()
            # from_node = FeedPost であるのは node_create 関数に影響を与えるためであり、 read 関数などは通常通り動作する。
            self._Tx.from_node = Option.NodeLabel.FeedPost
            self._Tx.edge      = Option.EdgeLabel.LIKES
            self._Tx.to_node   = Option.NodeLabel.User
        def read_likes_feed_post_ids(self, session: Session, from_user_id: int) -> list[int]:
            self._Tx.from_node, self._Tx.to_node = Option.NodeLabel.User, Option.NodeLabel.FeedPost
            result = self._read_rdb_ids_of_destination(session, from_user_id)
            self._Tx.from_node, self._Tx.to_node = Option.NodeLabel.FeedPost, Option.NodeLabel.User
            return result
        def read_liked_user_ids(self, session: Session, to_feed_post_id) -> list[int]:
            self._Tx.from_node, self._Tx.to_node = Option.NodeLabel.User, Option.NodeLabel.FeedPost
            result = self._read_rdb_ids_of_starting(session, to_feed_post_id)
            self._Tx.from_node, self._Tx.to_node = Option.NodeLabel.FeedPost, Option.NodeLabel.User
            return result
    class FeedPostComment(AbstractNode):
        def __init__(self) -> None:
            super().__init__()
            # from_node = FeedPost であるのは node_create 関数に影響を与えるためであり、 read 関数などは通常通り動作する。
            self._Tx.from_node = Option.NodeLabel.FeedPost
            self._Tx.edge      = Option.EdgeLabel.LIKES
            self._Tx.to_node   = Option.NodeLabel.User
        def read_likes_feed_post_comment_ids(self, session: Session, from_user_id: int) -> list[int]:
            self._Tx.from_node, self._Tx.to_node = Option.NodeLabel.User, Option.NodeLabel.FeedPostComment
            result = self._read_rdb_ids_of_destination(session, from_user_id)
            self._Tx.from_node, self._Tx.to_node = Option.NodeLabel.FeedPostComment, Option.NodeLabel.User
            return result
        def read_liked_user_ids(self, session: Session, to_feed_post_id) -> list[int]:
            self._Tx.from_node, self._Tx.to_node = Option.NodeLabel.User, Option.NodeLabel.FeedPostComment
            result = self._read_rdb_ids_of_starting(session, to_feed_post_id)
            self._Tx.from_node, self._Tx.to_node = Option.NodeLabel.FeedPostComment, Option.NodeLabel.User
            return result

class Edge:
    class FollowsUserAndActsOthers(AbstractEdge):
        def __init__(self) -> None:
            super().__init__()
            self._Tx.from_node                          = Option.NodeLabel.User
            self._Tx.edge                               = Option.EdgeLabel.FOLLOWS
            self._Tx.to_node                            = Option.NodeLabel.User
            (pg_run := Option.PgRunSetsForEdge()).table = Option.RDBTable.User
            self._Tx.pg_tx_by_create                    = pg_run.create_follows
            self._Tx.pg_tx_by_delete                    = pg_run.delete_follows
        def create_follows_user(self, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            self._Tx.edge, self._Tx.to_node = Option.EdgeLabel.FOLLOWS, Option.NodeLabel.User
            self._create(session, from_rdb_id, to_rdb_id)  
        def delete_follows_user(self, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            self._Tx.edge, self._Tx.to_node = Option.EdgeLabel.FOLLOWS, Option.NodeLabel.User
            self._delete(session, from_rdb_id, to_rdb_id)  
        def create_likes_feed_post(self, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            self._Tx.edge, self._Tx.to_node = Option.EdgeLabel.LIKES, Option.NodeLabel.FeedPost
            self._create(session, from_rdb_id, to_rdb_id)  
        def delete_likes_feed_post(self, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            self._Tx.edge, self._Tx.to_node = Option.EdgeLabel.LIKES, Option.NodeLabel.FeedPost
            self._delete(session, from_rdb_id, to_rdb_id)  
        def create_likes_task_finish(self, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            self._Tx.edge, self._Tx.to_node = Option.EdgeLabel.LIKES, Option.NodeLabel.TaskFinish
            self._create(session, from_rdb_id, to_rdb_id)  
        def delete_likes_task_finish(self, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            self._Tx.edge, self._Tx.to_node = Option.EdgeLabel.LIKES, Option.NodeLabel.TaskFinish
            self._delete(session, from_rdb_id, to_rdb_id)  
        def create_bookmarks_routine(self, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            self._Tx.edge, self._Tx.to_node = Option.EdgeLabel.BOOKMARKS, Option.NodeLabel.Routine
            self._create(session, from_rdb_id, to_rdb_id)  
        def delete_bookmarks_routine(self, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            self._Tx.edge, self._Tx.to_node = Option.EdgeLabel.BOOKMARKS, Option.NodeLabel.Routine
            self._delete(session, from_rdb_id, to_rdb_id)  
    class BookmarksRoutine(AbstractEdge):
        def __init__(self) -> None:
            super().__init__()
            self._Tx.from_node                          = Option.NodeLabel.User
            self._Tx.edge                               = Option.EdgeLabel.BOOKMARKS
            self._Tx.to_node                            = Option.NodeLabel.Routine    
            (pg_run := Option.PgRunSetsForEdge()).table = Option.RDBTable.Routine
            self._Tx.pg_tx_by_create                    = pg_run.create_bookmarks
            self._Tx.pg_tx_by_delete                    = pg_run.delete_bookmarks   
        def create_bookmarks_routine(self, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            self._create(session, from_rdb_id, to_rdb_id)  
        def delete_bookmarks_routine(self, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            self._delete(session, from_rdb_id, to_rdb_id)  
    class LikesTaskFinish(AbstractEdge):
        def __init__(self) -> None:
            super().__init__()
            self._Tx.from_node                          = Option.NodeLabel.User
            self._Tx.edge                               = Option.EdgeLabel.LIKES
            self._Tx.to_node                            = Option.NodeLabel.TaskFinish
            (pg_run := Option.PgRunSetsForEdge()).table = Option.RDBTable.TaskFinish
            self._Tx.pg_tx_by_create                    = pg_run.create_likes
            self._Tx.pg_tx_by_delete                    = pg_run.delete_likes
        def create_likes_task_finish(self, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            self._create(session, from_rdb_id, to_rdb_id)  
        def delete_likes_task_finish(self, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            self._delete(session, from_rdb_id, to_rdb_id)
    class LikesTaskFinishComment(AbstractEdge):  
        def __init__(self) -> None:
            super().__init__()
            self._Tx.from_node                          = Option.NodeLabel.User
            self._Tx.edge                               = Option.EdgeLabel.LIKES
            self._Tx.to_node                            = Option.NodeLabel.TaskFinishComment
            (pg_run := Option.PgRunSetsForEdge()).table = Option.RDBTable.TaskFinishComment
            self._Tx.pg_tx_by_create                    = pg_run.create_likes
            self._Tx.pg_tx_by_delete                    = pg_run.delete_likes      
        def create_likes_task_finish_comment(self, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            self._create(session, from_rdb_id, to_rdb_id)  
        def delete_likes_task_finish_comment(self, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            self._delete(session, from_rdb_id, to_rdb_id)             
    class LikesFeedPost(AbstractEdge):
        def __init__(self) -> None:
            super().__init__()
            self._Tx.from_node                          = Option.NodeLabel.User
            self._Tx.edge                               = Option.EdgeLabel.LIKES
            self._Tx.to_node                            = Option.NodeLabel.FeedPost
            (pg_run := Option.PgRunSetsForEdge()).table = Option.RDBTable.FeedPost
            self._Tx.pg_tx_by_create                    = pg_run.create_likes
            self._Tx.pg_tx_by_delete                    = pg_run.delete_likes
        def create_likes_feed_post(self, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            self._create(session, from_rdb_id, to_rdb_id)  
        def delete_likes_feed_post(self, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            self._delete(session, from_rdb_id, to_rdb_id)
    class LikesFeedPostComment(AbstractEdge):
        def __init__(self) -> None:
            super().__init__()
            self._Tx.from_node                          = Option.NodeLabel.User
            self._Tx.edge                               = Option.EdgeLabel.LIKES
            self._Tx.to_node                            = Option.NodeLabel.FeedPostComment
            (pg_run := Option.PgRunSetsForEdge()).table = Option.RDBTable.FeedPostComment
            self._Tx.pg_tx_by_create                    = pg_run.create_likes
            self._Tx.pg_tx_by_delete                    = pg_run.delete_likes
        def create_likes_feed_post_comment(self, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            self._create(session, from_rdb_id, to_rdb_id)  
        def delete_likes_feed_post_comment(self, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            self._delete(session, from_rdb_id, to_rdb_id)              
     