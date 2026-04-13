from flask import Flask, render_template, request, jsonify
import networkx as nx
import json

app = Flask(__name__, template_folder='../frontend', static_folder='../frontend/static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    edges = data['edges']
    
    # Build graph
    G = nx.DiGraph()
    for e in edges:
        G.add_edge(e['from'], e['to'], weight=e['weight'])
    
    # Find cycles using NetworkX
    from networkx.algorithms.cycles import simple_cycles
    cycles_raw = list(simple_cycles(G))
    
    cycles = []
    for cycle in cycles_raw:
        if len(cycle) >= 3:
            # Compute extent (average weight of edges in cycle)
            cycle_edges = []
            for i in range(len(cycle)):
                u = cycle[i]
                v = cycle[(i+1) % len(cycle)]
                if G.has_edge(u, v):
                    cycle_edges.append(G[u][v]['weight'])
            if cycle_edges:
                extent = sum(cycle_edges) / len(cycle_edges)
                cycles.append({'path': cycle, 'extent': extent})
    
    # Sort by extent descending
    cycles.sort(key=lambda x: x['extent'], reverse=True)
    
    # Nodes and edges for viz
    nodes = [{'id': node} for node in G.nodes()]
    edges_viz = [{'from': u, 'to': v, 'weight': d['weight']} for u, v, d in G.edges(data=True)]
    
    bias = len(cycles) > 0
    
    return jsonify({'nodes': nodes, 'edges': edges_viz, 'cycles': cycles, 'bias': bias})

if __name__ == '__main__':
    app.run(debug=True)