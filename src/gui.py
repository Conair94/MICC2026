import tkinter as tk
from tkinter import ttk, messagebox
import curver
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re

import itertools

class RigidSeedGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Rigid Seed Visualization")
        self.root.geometry("1400x900")

        # Data
        self.surface = None
        self.curves_dict = {}
        self.expanded_curves = [] # List of (name, curve, generation)

        self.setup_ui()
        self.load_surface()

    def setup_ui(self):
        # Main Layout
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left Pane: Controls
        left_pane = ttk.Frame(main_frame, width=350)
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
        curve_group = ttk.LabelFrame(left_pane, text="Curve Selection (The Seed)", padding="5")
        curve_group.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(curve_group, text="Enter curves (comma separated):").pack(anchor=tk.W)
        self.curve_input = tk.Text(curve_group, height=6, width=40)
        self.curve_input.pack(fill=tk.X, pady=5)
        self.curve_input.insert(tk.END, "a_0, b_0, c_0")

        # Expansion Controls
        exp_group = ttk.LabelFrame(left_pane, text="Rigid Expansion & Graph Style", padding="5")
        exp_group.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(exp_group, text="Generations (n):").grid(row=0, column=0, sticky=tk.W)
        self.exp_gen_var = tk.IntVar(value=1)
        self.exp_gen_spin = ttk.Spinbox(exp_group, from_=1, to=5, textvariable=self.exp_gen_var, width=5)
        self.exp_gen_spin.grid(row=0, column=1, sticky=tk.W, pady=2)

        ttk.Label(exp_group, text="Edge Type:").grid(row=1, column=0, sticky=tk.W)
        self.edge_type_var = tk.StringVar(value="Disjoint (Curve Graph)")
        self.edge_type_combo = ttk.Combobox(exp_group, textvariable=self.edge_type_var, 
                                            values=["Disjoint (Curve Graph)", "Intersect (Intersection Graph)"],
                                            state="readonly", width=22)
        self.edge_type_combo.grid(row=1, column=1, pady=2, sticky=tk.W)
        self.edge_type_combo.bind("<<ComboboxSelected>>", lambda e: self.visualize_expanded())

        self.compute_btn = ttk.Button(exp_group, text="Compute n-th Expansion", command=self.compute_expansion)
        self.compute_btn.grid(row=2, column=0, columnspan=2, pady=5, sticky=tk.EW)

        self.viz_btn = ttk.Button(exp_group, text="Visualize Current Seed", command=self.visualize_seed)
        self.viz_btn.grid(row=3, column=0, columnspan=2, pady=2, sticky=tk.EW)

        # Examples
        ex_group = ttk.LabelFrame(left_pane, text="Rigid Seed Examples", padding="5")
        ex_group.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(ex_group, text="Aramayona-Leininger (G3)", command=self.load_al_example).pack(fill=tk.X, pady=2)
        ttk.Button(ex_group, text="Short Chain (G2)", command=self.load_g2_chain).pack(fill=tk.X, pady=2)

        # Instructions
        inst_group = ttk.LabelFrame(left_pane, text="Instructions", padding="5")
        inst_group.pack(fill=tk.BOTH, expand=True)
        
        self.inst_scroll = tk.Scrollbar(inst_group)
        self.inst_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.inst_text = tk.Text(inst_group, wrap=tk.WORD, height=10, width=40, yscrollcommand=self.inst_scroll.set)
        self.inst_text.pack(fill=tk.BOTH, expand=True)
        self.inst_scroll.config(command=self.inst_text.yview)
        
        help_msg = (
            "Specifying Curves:\n"
            "• Use standard names like a_0, b_0, c_0.\n"
            "• Separate with commas.\n\n"
            "Rigid Expansion:\n"
            "• E(X) adds curves γ such that γ is the UNIQUE curve disjoint from some subset of X.\n"
            "• This GUI checks subsets of size 2 and 3.\n"
            "• Generation 0 (Green): Original Seed.\n"
            "• Generation n (Blue/Cyan/etc): Expanded curves.\n\n"
            "Warning: Expansion can be slow for many curves or generations."
        )
        self.inst_text.insert(tk.END, help_msg)
        self.inst_text.config(state=tk.DISABLED)

        # Right Pane: Visualization
        right_pane = ttk.Frame(main_frame)
        right_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_pane)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def load_surface(self):
        try:
            g = int(self.genus_var.get())
            n = int(self.punc_var.get())
            if g < 0 or n < 0: raise ValueError("Must be non-negative")
            # Curver requires g+n >= 1 usually
            self.surface = curver.load(g, n)
            self.curves_dict = self.surface.curves
            self.expanded_curves = [] # Clear expansion data
            print(f"Loaded S_{g}_{n}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load surface S_{self.genus_var.get()}_{self.punc_var.get()}: {e}")

    def load_al_example(self):
        self.genus_var.set("3")
        self.punc_var.set("1")
        self.load_surface()
        al_curves = "a_0, b_0, a_1, b_1, a_2, b_2, c_0, c_1"
        self.curve_input.delete('1.0', tk.END)
        self.curve_input.insert(tk.END, al_curves)
        self.visualize_seed()

    def load_g2_chain(self):
        self.genus_var.set("2")
        self.punc_var.set("1")
        self.load_surface()
        # Chain of 3 curves in S2,1
        # a0 intersects b0, b0 intersects c1
        chain = "a_0, b_0, c_1"
        self.curve_input.delete('1.0', tk.END)
        self.curve_input.insert(tk.END, chain)
        self.visualize_seed()

    def parse_seed(self):
        input_text = self.curve_input.get('1.0', tk.END).strip()
        names = [n.strip() for n in input_text.split(",") if n.strip()]
        seed = []
        for name in names:
            try:
                if not re.match(r'^[a-z0-9_+\-*() ]+$', name): continue
                curve = self.surface(name)
                seed.append((name, curve, 0)) # name, curve object, generation 0
            except:
                if name in self.curves_dict:
                    seed.append((name, self.curves_dict[name], 0))
        return seed

    def compute_expansion(self):
        seed = self.parse_seed()
        if not seed:
            messagebox.showwarning("Warning", "Please specify a valid seed first.")
            return

        n_gen = self.exp_gen_var.get()
        current_curves = seed[:]
        
        progress = tk.Toplevel(self.root)
        progress.title("Computing Expansion...")
        progress.geometry("300x100")
        prog_label = ttk.Label(progress, text="Starting...")
        prog_label.pack(pady=20)
        self.root.update()

        try:
            for gen in range(1, n_gen + 1):
                prog_label.config(text=f"Computing Generation {gen}...")
                self.root.update()
                
                new_curves_in_gen = []
                # Current collection of unique curves (objects)
                X_objs = [c[1] for c in current_curves]
                
                # Check subsets of current_curves
                # To keep it fast, we only check subsets of size 2 and 3
                # Size 2 subsets
                subsets = list(itertools.combinations(X_objs, 2)) + list(itertools.combinations(X_objs, 3))
                
                for subset in subsets:
                    gamma = self.uniquely_determined_curve(subset)
                    if gamma:
                        # Check if it's already in our collection
                        is_new = True
                        for _, existing_curve, _ in current_curves + new_curves_in_gen:
                            if gamma == existing_curve:
                                is_new = False
                                break
                        
                        if is_new:
                            name = f"E{gen}_{len(current_curves) + len(new_curves_in_gen)}"
                            new_curves_in_gen.append((name, gamma, gen))
                            print(f"Found new curve: {name}")

                if not new_curves_in_gen:
                    print("No more curves found in this expansion step.")
                    break
                
                current_curves.extend(new_curves_in_gen)

            self.expanded_curves = current_curves
            progress.destroy()
            self.visualize_expanded()
        except Exception as e:
            progress.destroy()
            messagebox.showerror("Expansion Error", str(e))

    def uniquely_determined_curve(self, Y):
        # Y is a tuple of Curve objects
        try:
            lam = sum(Y[1:], Y[0])
            B = lam.boundary()
            
            # Essential unique components
            essential = []
            for comp in B.parallel_components().keys():
                if not comp.is_peripheral():
                    essential.append(comp)
            
            if len(essential) != 1:
                return None
            
            gamma = essential[0]
            
            # Check if complement is pants/disks
            encoding = gamma.crush()
            target = encoding.target_triangulation
            
            # target.surface() returns dictionary of surfaces
            for surf in target.surface().values():
                # Pants: g=0, p=3
                if surf.g > 0 or surf.p > 3:
                    return None
            
            return gamma
        except:
            return None

    def visualize_seed(self):
        self.expanded_curves = self.parse_seed()
        self.visualize_expanded()

    def visualize_expanded(self):
        self.ax.clear()
        if not self.expanded_curves:
            self.canvas.draw()
            return

        curves = self.expanded_curves
        G = nx.Graph()
        node_colors = []
        color_map = {0: 'lightgreen', 1: 'skyblue', 2: 'orange', 3: 'pink', 4: 'violet', 5: 'yellow'}
        
        show_disjoint = "Disjoint" in self.edge_type_var.get()

        for name, _, gen in curves:
            G.add_node(name)
            node_colors.append(color_map.get(gen, 'gray'))

        for i in range(len(curves)):
            for j in range(i + 1, len(curves)):
                name1, c1, _ = curves[i]
                name2, c2, _ = curves[j]
                try:
                    inter = c1.intersection(c2)
                    if show_disjoint:
                        if inter == 0:
                            G.add_edge(name1, name2)
                    else:
                        if inter > 0:
                            G.add_edge(name1, name2, weight=inter)
                except:
                    pass

        pos = nx.spring_layout(G, k=0.5, iterations=50)
        nx.draw(G, pos, ax=self.ax, with_labels=True, node_color=node_colors, 
                node_size=1200, font_size=8, font_weight='bold', edge_color='gray', alpha=0.9)
        
        if not show_disjoint:
            edge_labels = nx.get_edge_attributes(G, 'weight')
            nx.draw_networkx_edge_labels(G, pos, ax=self.ax, edge_labels=edge_labels, font_size=7)
        
        title_type = "Curve Graph (Edges = Disjoint)" if show_disjoint else "Intersection Graph (Edges = Intersect)"
        self.ax.set_title(f"{title_type} on S_{self.genus_var.get()}_{self.punc_var.get()}")
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = RigidSeedGUI(root)
    root.mainloop()
