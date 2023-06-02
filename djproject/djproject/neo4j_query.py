from neo4j import GraphDatabase

from djproject import constants
from djproject import neo4j_transactions


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
            return session.execute_read(neo4j_transactions.get_connections, self._graph_owner_id)


    def get_nodes(self) -> list[dict]:
        """
        Get properties of all nodes.
        :return: List of nodes. Every node is a dict, which contains id and other properties.
        """
        with self._driver.session(database=constants.NEO4J_DATABASE_NAME) as session:
            return session.execute_read(neo4j_transactions.get_nodes, self._graph_owner_id)


    def page_rank(self):
        """
        Runs Page Rank algorighm.
        Page Rank results are written to node properties called "page_rank_result".
        """
        with self._driver.session(database=constants.NEO4J_DATABASE_NAME) as session:
            session.execute_write(neo4j_transactions.run_graph_algorithm, self._graph_owner_id)


    def hits(self, hits_iterations=3):
        """
        Runs HITS algorighm.
        HITS results are written to node properties called "hits_result_hub" (hub score) and "hits_result_auth" (authority score).
        """
        with self._driver.session(database=constants.NEO4J_DATABASE_NAME) as session:
            session.execute_write(neo4j_transactions.run_graph_algorithm, self._graph_owner_id, 'hits', hits_iterations)


    def get_page_rank_important_nodes(self, threshold: float):
        with self._driver.session(database=constants.NEO4J_DATABASE_NAME) as session:
            return session.execute_read(neo4j_transactions.get_page_rank_important_nodes, threshold, self._graph_owner_id)

    def get_page_rank_connections_of_important_nodes(self, threshold: float):
        with self._driver.session(database=constants.NEO4J_DATABASE_NAME) as session:
            return session.execute_read(neo4j_transactions.get_page_rank_connections_of_important_nodes, threshold, self._graph_owner_id)

    def get_hits_important_nodes(self, threshold: float):
        with self._driver.session(database=constants.NEO4J_DATABASE_NAME) as session:
            return session.execute_read(neo4j_transactions.get_hits_important_nodes, threshold, self._graph_owner_id)

    def get_hits_connections_of_important_nodes(self, threshold: float):
        with self._driver.session(database=constants.NEO4J_DATABASE_NAME) as session:
            return session.execute_read(neo4j_transactions.get_hits_connections_of_important_nodes, threshold, self._graph_owner_id)

    def get_top_nodes(self, property_name: str, count: int):
        with self._driver.session(database=constants.NEO4J_DATABASE_NAME) as session:
            return session.execute_read(neo4j_transactions.get_top_nodes, property_name, count, self._graph_owner_id)


