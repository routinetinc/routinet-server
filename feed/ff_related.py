from feed.utils.graph_db.individual_edge_and_node import Node as BaseNode, Edge

class User(BaseNode.User):
    class Relation(Edge.FollowsUserAndActsOthers):
        pass