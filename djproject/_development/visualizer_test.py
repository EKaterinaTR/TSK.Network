from djproject.graph_visualizer import GraphVisualizer

GraphVisualizer(graph_owner_id=0, algorithm='page_rank').create_visualization()
# graph = GraphVisualizer(graph_owner_id=0).load_to_networkx()
# print(graph.nodes)
# print(len(graph.nodes))
# print(graph.nodes['Гурьянов Артем'])