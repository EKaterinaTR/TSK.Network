from neo4j import GraphDatabase

import constants
import neo4j_transactions


class Neo4JQuery:
    def __init__(self):
        self._driver = GraphDatabase.driver(**constants.NEO4J_CONNECTION_PARAMETERS)


    def get_connections(self) -> list[list[int, int, str]]:
        with self._driver.session(database=constants.NEO4J_DATABASE_NAME) as session:
            return session.execute_read(neo4j_transactions.get_connections)
