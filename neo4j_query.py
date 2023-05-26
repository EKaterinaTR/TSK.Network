from neo4j import GraphDatabase

import constants
import neo4j_transactions


class Neo4JQuery:
    def __init__(self, graph_owner_id: int):
        self._driver = GraphDatabase.driver(**constants.NEO4J_CONNECTION_PARAMETERS)
        self._graph_owner_id = graph_owner_id


    def get_connections(self) -> list[list[int, int, str]]:
        """
        Get all connections between users
        :return: List of connections. Every connection is a list with following data: [from_id: int, to_id: int, connection_type: str]
        """
        with self._driver.session(database=constants.NEO4J_DATABASE_NAME) as session:
            return session.execute_read(neo4j_transactions.get_connections)


    def get_nodes(self) -> list[dict]:
        """
        Get properties of nodes.
        :return: List of nodes. Every node is a dict, which contains id and other properties.
        """
        with self._driver.session(database=constants.NEO4J_DATABASE_NAME) as session:
            return session.execute_read(neo4j_transactions.get_nodes)


    def page_rank(self):
        with self._driver.session(database=constants.NEO4J_DATABASE_NAME) as session:
            session.execute_write(neo4j_transactions.run_graph_algorithm, self._graph_owner_id)


    def hits(self, hits_iterations=20):
        with self._driver.session(database=constants.NEO4J_DATABASE_NAME) as session:
            session.execute_write(neo4j_transactions.run_graph_algorithm, self._graph_owner_id, 'hits', hits_iterations)
