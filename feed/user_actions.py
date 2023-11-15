from feed.utils.graph_db.individual_edge_and_node import Node, Edge

class Routine(Node.Routine):
    class Relation(Edge.BookmarksRoutine):
        pass
    
class TaskFinish(Node.TaskFinish):
    class Relation(Edge.LikesTaskFinish):
        pass

class TaskFinishComment(Node.TaskFinishComment):
    class Relation(Edge.LikesTaskFinishComment):
        pass

class FeedPost(Node.FeedPost):
    class Relation(Edge.LikesFeedPost):
        pass

class FeedPostComment(Node.FeedPostComment):
    class Relation(Edge.LikesFeedPostComment):
        pass