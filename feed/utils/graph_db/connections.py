from secret import LocalNeo4jDB as Neo4j
from django.db.backends.base.base import BaseDatabaseWrapper as BDW
from django.db import connections
from neo4j import GraphDatabase, Driver

# DjangoのデータベースドライバとNeo4jのドライバを取得
pg_driver: BDW = connections['default']
neo4j_driver: Driver = GraphDatabase.driver(Neo4j.uri, auth=(Neo4j.user, Neo4j.password))