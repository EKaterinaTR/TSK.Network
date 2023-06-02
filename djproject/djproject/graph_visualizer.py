from pathlib import Path
import math

import networkx as nx

from djproject.neo4j_query import Neo4JQuery
from py_linq import Enumerable
from pyvis.network import Network


NODE_SIZE_MIN = 5
NODE_SIZE_MAX = 50


class GraphVisualizer:
    def __init__(self, graph_owner_id: int, algorithm: str = None):
        self._graph_owner_id = graph_owner_id
        self._algorithm = algorithm
        self._algorithm_metrics_stats = None


    def _load_to_networkx(self):
        neo4j_query = Neo4JQuery(self._graph_owner_id)
        nodes = neo4j_query.get_nodes()
        edges = neo4j_query.get_connections()
        graph = nx.Graph()
        self._compute_algorithm_metrics_stats(nodes)
        prepared_nodes = list(map(self._node_to_networkx_format, nodes))
        graph.add_nodes_from(prepared_nodes)
        graph.add_edges_from(_prepare_edges(edges))
        return graph


    def create_visualization(self):
        graph = self._load_to_networkx()
        network = Network(height='800px')
        #network.show_buttons(filter_=['physics'])
        network.repulsion()
        network.from_nx(graph)
        graph_path = str(Path(__file__).parent.joinpath(f'../templates/pyvis_generated/graph_{self._graph_owner_id}.html'))
        network.save_graph(graph_path)


    def _compute_algorithm_metrics_stats(self, nodes: list):
        self._algorithm_metrics_stats = {}
        if self._algorithm == 'page_rank':
            self._algorithm_metrics_stats['page_rank_min'] = min(nodes, key=lambda x: x['page_rank_result'])['page_rank_result']
            self._algorithm_metrics_stats['page_rank_max'] = max(nodes, key=lambda x: x['page_rank_result'])['page_rank_result']
        if self._algorithm == 'hits':
            self._algorithm_metrics_stats['hits_hub_min'] = min(nodes, key=lambda x: x['hits_result_hub'])['hits_result_hub']
            self._algorithm_metrics_stats['hits_hub_max'] = max(nodes, key=lambda x: x['hits_result_hub'])['hits_result_hub']

            self._algorithm_metrics_stats['hits_auth_min'] = min(nodes, key=lambda x: x['hits_result_auth'])['hits_result_auth']
            self._algorithm_metrics_stats['hits_auth_max'] = max(nodes, key=lambda x: x['hits_result_auth'])['hits_result_auth']


    def _node_to_networkx_format(self, node: dict) -> (str, dict):
        name = node['surname'] + ' ' + node['name']
        node_id = node['id']

        new_node_data = {}
        new_node_data['label'] = name # Node label
        # Корень, чтобы метрика была пропорциональна площади вершины. Множитель нужно брать такой, чтобы граф выглядел красиво
        if self._algorithm == 'page_rank':
            new_node_data['title'] = f"Page Rank: {node['page_rank_result']}" # Text on hover
            new_node_data['size'] = _normalize(node['page_rank_result'], self._algorithm_metrics_stats['page_rank_min'], self._algorithm_metrics_stats['page_rank_max'],
                                    NODE_SIZE_MIN, NODE_SIZE_MAX)
        if self._algorithm == 'hits':
            new_node_data['title'] = f"HITS hub: {node['hits_result_hub']}" + '\n' + f"HITS authority: {node['hits_result_auth']}" # Text on hover
            new_node_data['size'] = _normalize(node['hits_result_hub'], self._algorithm_metrics_stats['hits_hub_min'], self._algorithm_metrics_stats['hits_hub_max'],
                                    NODE_SIZE_MIN, NODE_SIZE_MAX)
            color = 255 - int(_normalize(node['hits_result_auth'], self._algorithm_metrics_stats['hits_auth_min'], self._algorithm_metrics_stats['hits_auth_max'], 0, 255))

            new_node_data['color'] = '#%02x%02x%02x' % (color, color, color) # Source: https://stackoverflow.com/a/3380739

        return (node_id, new_node_data)





def _prepare_edges(edges: list):
    # Edge type is currently ignored
    # Sorting and creation of set are needed to remove duplicate edges
    return set(map(lambda x: tuple(sorted(x[0:2])), edges))


def _normalize(value, source_min, source_max, destination_min, destination_max):
    if source_min == source_max: # If will be division by zero
        return (destination_max - destination_min) / 2
    normalized = (value - source_min) / (source_max - source_min)
    return normalized * (destination_max - destination_min) + destination_min