import networkx as nx
import json
import matplotlib.pyplot as plt
import community as community_louvain

def visualize(G):
    # Draw the graph
    pos = nx.kamada_kawai_layout(G)  # compute graph layout
    plt.figure(figsize=(10, 8))  # image is 10 x 8 inches

    nx.draw_networkx_nodes(G, pos, node_size=500)
    nx.draw_networkx_edges(G, pos, arrowstyle='->',
                        arrowsize=10, width=2, alpha=0.5, edge_color='gray')
    nx.draw_networkx_labels(G, pos, font_size=8)  # changed font size to 8

    plt.axis('off')
    plt.show()

def unique_relations(G):
    # Print unique relations
    relations = set()
    for u, v, k in G.edges(data=True):
        relations.add(k['attr_dict']['relation_type'])
    print(f'Unique relations: {relations}')

def get_allies(G, name):
    allies = set()

    for u, v, k in G.edges(data=True):
        if k['attr_dict']['relation_type'] == 'is allied with' and u == name:
            allies.add(v)
        elif k['attr_dict']['relation_type'] == 'is allied with' and v == name:
            allies.add(u)

    return list(allies)

def get_enemies(G, name):
    enemies = set()

    for u, v, k in G.edges(data=True):
            if k['attr_dict']['relation_type'] == 'is enemy of' and u == name:
                enemies.add(v)
            elif k['attr_dict']['relation_type'] == 'is enemy of' and v == name:
                enemies.add(u)

    return list(enemies)

# Ally of an ally is also an ally
def predict_allies(G, name):
    neighbors = set(G.neighbors(name))
    potential_allies = set()

    for n in neighbors:
        for u, v, k in G.edges(n, data=True):
            if k['attr_dict']['relation_type'] == 'is allied with':
                potential_allies.add(v)

    return list(potential_allies)

# Enemy of an ally is also an enemy
def predict_enemies(G, name):
    neighbors = set(G.neighbors(name))
    potential_enemies = set()

    for n in neighbors:
        for u, v, k in G.edges(n, data=True):
            if k['attr_dict']['relation_type'] == 'is enemy of':
                potential_enemies.add(v)
    
    return list(potential_enemies)

def cluster_network(G):
    # Convert the graph to undirected
    G_undirected = G.to_undirected()

    # Compute the best partition using the Louvain method
    partition = community_louvain.best_partition(G_undirected)

    # Get the number of communities
    num_communities = len(set(partition.values()))

    print(f"Number of communities: {num_communities}")
    
    # Draw the graph
    pos = nx.kamada_kawai_layout(G_undirected)
    plt.figure(figsize=(10, 8))
    cmap = plt.cm.get_cmap('viridis', max(partition.values()) + 1)
    nx.draw_networkx_nodes(G_undirected, pos, partition.keys(), node_size=500, 
                        cmap=cmap, node_color=list(partition.values()))
    nx.draw_networkx_labels(G_undirected, pos, font_size=8)  # changed font size to 8
    nx.draw_networkx_edges(G_undirected, pos, alpha=0.5)
    plt.axis('off')
    plt.show()

# Load JSON data from a file
with open('got.json') as f:
    data = json.load(f)

# Create a directed graph
G = nx.DiGraph()

# Add nodes to the graph
characters = data['characters']

# Print how many characters there are
print(f'Number of characters: {len(characters)}')

for character in characters:
    G.add_node(character['name'], attr_dict=character)

# Add edges to the graph
relations = data['relations']

for relation in relations:
    G.add_edge(relation['source'], relation['target'], attr_dict=relation)

# unique_relations(G)
#visualize(G)

# Predict alliances
character = 'Tywin Lannister'

# Do intersection with actual allies
allies = get_allies(G, character)
predicted_allies = predict_allies(G, character)
correct_allies = set(allies).intersection(set(predicted_allies))
print(f'Correct allies of {character}: {correct_allies}')
print('Preicision: ', len(correct_allies) / len(predicted_allies))

print(f'Potential enemies of {character}:')
print(predict_enemies(G, character))

# Do intersection with actual enemies
enemies = get_enemies(G, character)
predicted_enemies = predict_enemies(G, character)
correct_enemies = set(enemies).intersection(set(predicted_enemies))
print(f'Correct enemies of {character}: {correct_enemies}')
print('Preicision: ', len(correct_enemies) / len(predicted_enemies))

# cluster_network(G)