from feed.utils.graph_db.individual_edge_and_node import Node, EdgeByTargetNode

class User(Node.User):
    class Relation(EdgeByTargetNode.FollowsUser):
        pass