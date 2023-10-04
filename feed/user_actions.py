from neo4j import Session
from feed.utils.graph_db.individual_edge_and_node import Node, Edge

class FeedPost(Node.FeedPost):
    class Relation(Edge.LikesFeedPost):
        pass

class TaskFinish(Node.TaskFinish):
    class Relation(Edge.LikesTaskFinish):
        pass

class Routine(Node.Routine):
    class Relation(Edge.BookmarksRoutine):
        pass