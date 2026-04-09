import tkinter as tk
from tkinter import ttk, messagebox
import curver
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re

class RigidSeedGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Rigid Seed Visualization")
        self.root.geometry("1200x800")

        # Data
        self.surface = None
        self.curves_dict = {}

        self.setup_ui()
        self.load_surface()

    def setup_ui(self):
        # Main Layout
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left Pane: Controls
        left_pane = ttk.Frame(main_frame, width=300)
        left_pane.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Surface Config
        surf_group = ttk.LabelFrame(left_pane, text="Surface Configuration", padding="5")
        surf_group.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(surf_group, text="Genus:").grid(row=0, column=0, sticky=tk.W)
        self.genus_var = tk.StringVar(value="3")
        self.genus_spin = ttk.Spinbox(surf_group, from_=0, to=10, textvariable=self.genus_var, width=5, command=self.load_surface)
        self.genus_spin.grid(row=0, column=1, sticky=tk.W, pady=2)

        ttk.Label(surf_group, text="Punctures:").grid(row=1, column=0, sticky=tk.W)
        self.punc_var = tk.StringVar(value="1")
        self.punc_spin = ttk.Spinbox(surf_group, from_=0, to=10, textvariable=self.punc_var, width=5, command=self.load_surface)
        self.punc_spin.grid(row=1, column=1, sticky=tk.W, pady=2)

        # Curve Selection
        curve_group = ttk.LabelFrame(left_pane, text="Curve Selection", padding="5")
        curve_group.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        ttk.Label(curve_group, text="Enter curves (comma separated):").pack(anchor=tk.W)
        self.curve_input = tk.Text(curve_group, height=10, width=35)
        self.curve_input.pack(fill=tk.BOTH, expand=True, pady=5)
        self.curve_input.insert(tk.END, "a_0, b_0, a_1, b_1, c_0")

        btn_frame = ttk.Frame(curve_group)
        btn_frame.pack(fill=tk.X)
        
        self.viz_btn = ttk.Button(btn_frame, text="Visualize Graph", command=self.visualize)
        self.viz_btn.pack(side=tk.LEFT, padx=2)

        self.clear_btn = ttk.Button(btn_frame, text="Clear", command=lambda: self.curve_input.delete('1.0', tk.END))
        self.clear_btn.pack(side=tk.LEFT, padx=2)

        # Examples
        ex_group = ttk.LabelFrame(left_pane, text="Rigid Seed Examples", padding="5")
        ex_group.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(ex_group, text="Aramayona-Leininger (G3)", command=self.load_al_example).pack(fill=tk.X, pady=2)
        ttk.Button(ex_group, text="Humphries Chain (G3)", command=self.load_humphries_example).pack(fill=tk.X, pady=2)

        # Instructions
        inst_group = ttk.LabelFrame(left_pane, text="Instructions", padding="5")
        inst_group.pack(fill=tk.X)
        
        inst_text = (
            "1. Select Genus and Punctures.\n"
            "2. Curver provides standard curves:\n"
            "   a_0, a_1, ... b_0, b_1, ...\n"
            "   c_0, c_1, ... (Humphries)\n"
            "3. Specify curves in the text box,\n"
            "   separated by commas.\n"
            "4. You can also use expressions:\n"
            "   'a_0 + b_0' or 'a_0 * b_0'\n"
            "   (if supported by Curver lamination)."
        )
        ttk.Label(inst_group, text=inst_text, justify=tk.LEFT, wraplength=250).pack()

        # Right Pane: Visualization
        right_pane = ttk.Frame(main_frame)
        right_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_pane)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def load_surface(self):
        try:
            g = int(self.genus_var.get())
            n = int(self.punc_var.get())
            self.surface = curver.load(g, n)
            self.curves_dict = self.surface.curves
            print(f"Loaded S_{g}_{n}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load surface: {e}")

    def load_al_example(self):
        self.genus_var.set("3")
        self.punc_var.set("1")
        self.load_surface()
        # Approximate AL seed for G3 using available curves
        # Real AL seed needs closed chain, which curver has in naming
        al_curves = "a_0, b_0, a_1, b_1, a_2, b_2, c_0, c_1"
        self.curve_input.delete('1.0', tk.END)
        self.curve_input.insert(tk.END, al_curves)
        self.visualize()

    def load_humphries_example(self):
        self.genus_var.set("3")
        self.punc_var.set("1")
        self.load_surface()
        # Standard Humphries chain
        h_curves = "a_0, b_0, a_1, b_1, a_2, b_2, c_1"
        self.curve_input.delete('1.0', tk.END)
        self.curve_input.insert(tk.END, h_curves)
        self.visualize()

    def parse_curves(self, input_text):
        names = [n.strip() for n in input_text.split(",") if n.strip()]
        selected_curves = []
        for name in names:
            try:
                # Basic safety check for eval
                if not re.match(r'^[a-z0-9_+\-*() ]+$', name):
                    raise ValueError(f"Invalid characters in curve name: {name}")
                
                # Try to evaluate as curver expression within the surface's context
                # We can use S(name) which parses curver words/expressions
                curve = self.surface(name)
                selected_curves.append((name, curve))
            except Exception as e:
                print(f"Could not parse '{name}': {e}")
                # Try direct lookup if it's a simple name
                if name in self.curves_dict:
                    selected_curves.append((name, self.curves_dict[name]))
                else:
                    messagebox.showwarning("Warning", f"Curve '{name}' not found or invalid.")
        return selected_curves

    def visualize(self):
        self.ax.clear()
        input_text = self.curve_input.get('1.0', tk.END).strip()
        if not input_text:
            self.canvas.draw()
            return

        curves = self.parse_curves(input_text)
        if not curves:
            self.canvas.draw()
            return

        G = nx.Graph()
        for name, _ in curves:
            G.add_node(name)

        for i in range(len(curves)):
            for j in range(i + 1, len(curves)):
                name1, c1 = curves[i]
                name2, c2 = curves[j]
                try:
                    inter = c1.intersection(c2)
                    if inter > 0:
                        G.add_edge(name1, name2, weight=inter)
                except:
                    pass

        pos = nx.spring_layout(G)
        nx.draw(G, pos, ax=self.ax, with_labels=True, node_color='lightgreen', 
                node_size=1500, font_size=8, font_weight='bold')
        
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, ax=self.ax, edge_labels=edge_labels)
        
        self.ax.set_title(f"Curve Intersection Graph on S_{self.genus_var.get()}_{self.punc_var.get()}")
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = RigidSeedGUI(root)
    root.mainloop()
