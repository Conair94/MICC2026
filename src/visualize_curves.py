import curver
import networkx as nx
import matplotlib.pyplot as plt

def main():
    # Load a surface, e.g., genus 2 surface with 0 punctures (S_2_0)
    # curver uses a naming convention like S_{g}_{n}
    # Note: S_2 is often used for genus 2, 0 punctures.
    try:
        S = curver.load(3, 1)
        print(f"Loaded surface: {S}")
    except Exception as e:
        print(f"Error loading surface: {e}")
        # Fallback
        S = curver.load(1, 1)
        print(f"Loaded fallback surface: {S}")

    # Let's get all named curves
    curves = list(S.curves.items())
            
    print(f"Selected curves: {[c[0] for c in curves]}")

    # Build intersection graph
    G = nx.Graph()
    for name, curve in curves:
        G.add_node(name)

    for i in range(len(curves)):
        for j in range(i + 1, len(curves)):
            name1, c1 = curves[i]
            name2, c2 = curves[j]
            # intersection_number calculates the geometric intersection number
            inter = c1.intersection(c2)
            if inter > 0:
                G.add_edge(name1, name2, weight=inter)
                print(f"Intersection between {name1} and {name2}: {inter}")
            else:
                print(f"Curves {name1} and {name2} are disjoint.")

    # Visualize the graph
    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=2000, font_size=10, font_weight='bold')
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.title("Curve Intersection Graph (Relational Structure)")
    
    output_path = "curve_intersection_graph.png"
    plt.savefig(output_path)
    print(f"Saved intersection graph to {output_path}")

if __name__ == "__main__":
    main()
