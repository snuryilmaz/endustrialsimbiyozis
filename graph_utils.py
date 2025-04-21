import networkx as nx
import matplotlib.pyplot as plt

def draw_network_graph(suppliers, buyer, assignments, objective_type):
    G = nx.DiGraph()

    # Add supplier and buyer nodes
    for supplier in suppliers:
        G.add_node(f"Supplier_{supplier['id']}", role='supplier', capacity=supplier['capacity'])
    G.add_node("Buyer", role='buyer', demand=buyer['demand'])

    # Add edges based on assignments
    for supplier_id, quantity in assignments.items():
        supplier = next(s for s in suppliers if s['id'] == supplier_id)
        G.add_edge(f"Supplier_{supplier['id']}", "Buyer",
                   weight=supplier[objective_type], quantity=quantity)

    # Draw graph
    pos = nx.spring_layout(G)
    edge_labels = {(u, v): f"{data['quantity']} units" for u, v, data in G.edges(data=True)}

    nx.draw(G, pos, with_labels=True, node_color="lightblue", node_size=3000, font_size=10, font_weight="bold")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.title("Optimal Assignment Network")
    plt.show()