from feed.utils.graph_db.individual_edge_and_node import Node, Edge

class User(Node.User):
    class Relation(Edge.FollowsUserAndActsOthers):
        pass