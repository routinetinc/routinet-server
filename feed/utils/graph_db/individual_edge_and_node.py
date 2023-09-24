from feed.utils.graph_db.abstract_by_graph_db import AbstractNode, AbstractEdge, Option
from neo4j import Session


class Node:
    class User(AbstractNode):
        AbstractNode._Tx.from_node = Option.NodeLabel.User
        @classmethod
        def read_follows_user_ids(cls, session: Session, from_rdb_id: int) -> list[int]:
            cls._Tx.edge, cls._Tx.to_node = Option.EdgeLabel.FOLLOWS, Option.NodeLabel.User
            cls._read_rdb_ids_of_destination(session, from_rdb_id)
            return
        @classmethod
        def read_followed_user_ids(cls, session: Session, to_rdb_id: int) -> list[int]:
            cls._Tx.edge, cls._Tx.to_node = Option.EdgeLabel.FOLLOWS, Option.NodeLabel.User
            cls._read_rdb_ids_of_starting(session, to_rdb_id)
            return
        @classmethod
        def read_likes_feed_post_ids(cls, session: Session, from_rdb_id: int) -> list[int]:
            cls._Tx.edge, cls._Tx.to_node = Option.EdgeLabel.LIKES, Option.NodeLabel.FeedPost
            cls._read_rdb_ids_of_destination(session, from_rdb_id)
            return
        @classmethod
        def read_likes_task_finish_ids(cls, session: Session, from_rdb_id: int) -> list[int]:
            cls._Tx.edge, cls._Tx.to_node = Option.EdgeLabel.LIKES, Option.NodeLabel.TaskFinish
            cls._read_rdb_ids_of_destination(session, from_rdb_id)
            return
        @classmethod
        def read_bookmarks_routine_ids(cls, session: Session, from_rdb_id: int) -> list[int]:
            cls._Tx.edge, cls._Tx.to_node = Option.EdgeLabel.BOOKMARKS, Option.NodeLabel.Routine
            cls._read_rdb_ids_of_destination(session, from_rdb_id)
            return
        
    class FeedPost(AbstractNode):
        AbstractNode._Tx.from_node = Option.NodeLabel.FeedPost
        AbstractNode._Tx.edge      = Option.EdgeLabel.LIKES
        AbstractNode._Tx.to_node   = Option.NodeLabel.User
        @classmethod
        def read_likes_feed_post_ids(cls, session: Session, from_user_id: int) -> list[int]:
            cls._read_rdb_ids_of_destination(session, from_user_id)
            return
        @classmethod
        def read_liked_user_ids(cls, session: Session, to_feed_post_id) -> list[int]:
            cls._read_rdb_ids_of_starting(session, to_feed_post_id)
            return

    class TaskFinish(AbstractNode):
        AbstractNode._Tx.from_node = Option.NodeLabel.TaskFinish
        AbstractNode._Tx.edge      = Option.EdgeLabel.LIKES
        AbstractNode._Tx.to_node   = Option.NodeLabel.User
        @classmethod
        def read_likes_task_finish_ids(cls, session: Session, from_user_id: int) -> list[int]:
            cls._read_rdb_ids_of_destination(session, from_user_id)
            return        
        @classmethod
        def read_liked_user_ids(cls, session: Session, to_task_finish_id) -> list[int]:
            cls._read_rdb_ids_of_starting(session, to_task_finish_id)
            return
        
    class Routine(AbstractNode):
        AbstractNode._Tx.from_node = Option.NodeLabel.Routine
        AbstractNode._Tx.edge      = Option.EdgeLabel.BOOKMARKS
        AbstractNode._Tx.to_node   = Option.NodeLabel.User
        @classmethod
        def read_bookmarks_routine_ids(cls, session: Session, from_user_id: int) -> list[int]:
            cls._read_rdb_ids_of_destination(session, from_user_id)
            return
        @classmethod
        def read_bookmarked_user_ids(cls, session: Session, to_routine_id) -> list[int]:
            cls._read_rdb_ids_of_starting(session, to_routine_id)
            return

class Edge:
    class FollowsUser(AbstractEdge):
        AbstractEdge._Tx.from_node                = Option.NodeLabel.User
        AbstractEdge._Tx.edge                     = Option.EdgeLabel.LIKES
        AbstractEdge._Tx.to_node                  = Option.NodeLabel.User
        (pg_run := Option.PgRunSetsForEdge).table = Option.RDBTable.User
        AbstractEdge._Tx.pg_tx_by_create          = pg_run.create_follows
        AbstractEdge._Tx.pg_tx_by_delete          = pg_run.delete_follows
        @classmethod
        def create_follows_user(cls, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            AbstractEdge._Tx.to_node, AbstractEdge._Tx.to_node = Option.EdgeLabel.FOLLOWS, Option.NodeLabel.User
            cls._create(session, from_rdb_id, to_rdb_id)  
            return
        @classmethod
        def delete_follows_user(cls, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            AbstractEdge._Tx.to_node, AbstractEdge._Tx.to_node = Option.EdgeLabel.FOLLOWS, Option.NodeLabel.User
            cls._delete(session, from_rdb_id, to_rdb_id)  
            return     
        @classmethod
        def create_likes_feed_post(cls, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            AbstractEdge._Tx.to_node, AbstractEdge._Tx.to_node = Option.EdgeLabel.LIKES, Option.NodeLabel.FeedPost
            cls._create(session, from_rdb_id, to_rdb_id)  
            return 
        @classmethod
        def delete_likes_feed_post(cls, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            AbstractEdge._Tx.to_node, AbstractEdge._Tx.to_node = Option.EdgeLabel.LIKES, Option.NodeLabel.FeedPost
            cls._delete(session, from_rdb_id, to_rdb_id)  
            return         
        @classmethod
        def create_likes_task_finish(cls, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            AbstractEdge._Tx.to_node, AbstractEdge._Tx.to_node = Option.EdgeLabel.LIKES, Option.NodeLabel.TaskFinish
            cls._create(session, from_rdb_id, to_rdb_id)  
            return 
        @classmethod
        def delete_likes_task_finish(cls, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            AbstractEdge._Tx.to_node, AbstractEdge._Tx.to_node = Option.EdgeLabel.LIKES, Option.NodeLabel.TaskFinish
            cls._delete(session, from_rdb_id, to_rdb_id)  
            return            
        @classmethod
        def create_bookmarks_routine(cls, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            AbstractEdge._Tx.to_node, AbstractEdge._Tx.to_node = Option.EdgeLabel.BOOKMARKS, Option.NodeLabel.Routine
            cls._create(session, from_rdb_id, to_rdb_id)  
            return 
        @classmethod
        def delete_bookmarks_routine(cls, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            AbstractEdge._Tx.to_node, AbstractEdge._Tx.to_node = Option.EdgeLabel.BOOKMARKS, Option.NodeLabel.Routine
            cls._delete(session, from_rdb_id, to_rdb_id)  
            return                            
    class LikesFeedPost(AbstractEdge):
        AbstractEdge._Tx.from_node                = Option.NodeLabel.User
        AbstractEdge._Tx.edge                     = Option.EdgeLabel.LIKES
        AbstractEdge._Tx.to_node                  = Option.NodeLabel.FeedPost
        (pg_run := Option.PgRunSetsForEdge).table = Option.RDBTable.FeedPost
        AbstractEdge._Tx.pg_tx_by_create          = pg_run.create_likes
        AbstractEdge._Tx.pg_tx_by_delete          = pg_run.delete_likes
        @classmethod
        def create_likes_feed_post(cls, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            cls._create(session, from_rdb_id, to_rdb_id)  
            return 
        @classmethod
        def delete_likes_feed_post(cls, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            cls._delete(session, from_rdb_id, to_rdb_id)  
            return        
    class LikesTaskFinish(AbstractEdge):
        AbstractEdge._Tx.from_node                = Option.NodeLabel.User
        AbstractEdge._Tx.edge                     = Option.EdgeLabel.LIKES
        AbstractEdge._Tx.to_node                  = Option.NodeLabel.TaskFinish
        (pg_run := Option.PgRunSetsForEdge).table = Option.RDBTable.TaskFinish
        AbstractEdge._Tx.pg_tx_by_create          = pg_run.create_likes
        AbstractEdge._Tx.pg_tx_by_delete          = pg_run.delete_likes
        @classmethod
        def create_likes_task_finish(cls, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            cls._create(session, from_rdb_id, to_rdb_id)  
            return 
        @classmethod
        def delete_likes_task_finish(cls, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            cls._delete(session, from_rdb_id, to_rdb_id)         
            return
    class BookmarksRoutine(AbstractEdge):
        AbstractEdge._Tx.from_node                = Option.NodeLabel.User
        AbstractEdge._Tx.edge                     = Option.EdgeLabel.BOOKMARKS
        AbstractEdge._Tx.to_node                  = Option.NodeLabel.Routine    
        (pg_run := Option.PgRunSetsForEdge).table = Option.RDBTable.Routine
        AbstractEdge._Tx.pg_tx_by_create          = pg_run.create_bookmarks
        AbstractEdge._Tx.pg_tx_by_delete          = pg_run.delete_bookmarks   
        @classmethod
        def create_bookmarks_routine(cls, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            cls._create(session, from_rdb_id, to_rdb_id)  
            return 
        @classmethod
        def delete_bookmarks_routine(cls, session: Session, from_rdb_id: int, to_rdb_id: int) -> None:
            cls._delete(session, from_rdb_id, to_rdb_id)  
            return              
     
     