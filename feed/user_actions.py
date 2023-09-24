from neo4j import Session
from feed.utils.graph_db.individual_edge_and_node import Node, Edge

class FeedPost(Node.FeedPost):
    class Relation(Edge.LikesFeedPost):
        pass

class TaskFinish(Node.FeedPost):
    class Relation(Edge.LikesTaskFinish):
        pass

class Routine(Node.FeedPost):
    class Relation(Edge.BookmarksRoutine):
        pass