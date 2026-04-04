import sys
import os
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTextEdit, QTabWidget, QFormLayout,
                             QMessageBox, QSplitter, QComboBox, QListWidget, QGroupBox)
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import networkx as nx

# Add parent directory to path to handle direct script execution
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from micc.cli import MiccCore
    from micc.curves import cycle_to_ladder, ladder_to_cycle
except ImportError:
    from cli import MiccCore
    from curves import cycle_to_ladder, ladder_to_cycle

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100, is_3d=False):
        fig = Figure(figsize=(width, height), dpi=dpi)
        if is_3d:
            self.axes = fig.add_subplot(111, projection='3d')
        else:
            self.axes = fig.add_subplot(111)
        super().__init__(fig)

class MiccGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.core = MiccCore()
        self.examples = {
            "Select an Example...": None,
            "Birman-Margalit-Menasco (Distance 3)": {
                "top": "4,3,3,1,0,0",
                "bottom": "5,5,4,2,2,1",
                "cycle": ""
            },
            "Hempel Example (Distance 4)": {
                "top": "21,7,8,9,10,11,22,23,24,0,1,2,3,4,5,6,12,13,14,15,16,17,18,19,20",
                "bottom": "9,10,11,12,13,14,15,1,2,3,4,5,16,17,18,19,20,21,22,23,24,0,6,7,8",
                "cycle": ""
            },
            "Rigid Seed Chain (Genus 2 Partial)": {
                "top": "5,6,7,8,3,4,11,0,1,10,11,6",
                "bottom": "7,8,9,4,5,0,1,2,3,2,9,10",
                "cycle": ""
            },
            "Georgia Example (Distance 3)": {
                "top": "2,3,7,9,10,7,8,2,4,5,0,1",
                "bottom": "10,11,0,1,8,9,11,5,6,3,4,6",
                "cycle": ""
            },
            "Simple Cycle Example": {
                "top": "",
                "bottom": "",
                "cycle": "1+2-3+"
            }
        }
        self.initUI()

    def initUI(self):
        self.setWindowTitle('MICC - Metric in the Curve Complex')
        self.setGeometry(100, 100, 1200, 900)

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Splitter to separate input/controls from visualization
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Left Panel (Controls and Results)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        splitter.addWidget(left_panel)

        # --- Example Section ---
        example_group = QGroupBox("Mathematical Examples")
        example_layout = QVBoxLayout(example_group)
        self.example_box = QComboBox()
        self.example_box.addItems(list(self.examples.keys()))
        self.example_box.currentIndexChanged.connect(self.load_example_data)
        example_layout.addWidget(self.example_box)
        left_layout.addWidget(example_group)

        # --- Input Section ---
        input_group = QGroupBox("Curve Definition")
        input_layout = QFormLayout(input_group)
        self.top_input = QLineEdit()
        self.top_input.setPlaceholderText("Ladder Top IDs")
        self.bottom_input = QLineEdit()
        self.bottom_input.setPlaceholderText("Ladder Bottom IDs")
        self.cycle_input = QLineEdit()
        self.cycle_input.setPlaceholderText("Cycle Notation (e.g. 1+2-3+)")
        input_layout.addRow("Ladder Top:", self.top_input)
        input_layout.addRow("Ladder Bottom:", self.bottom_input)
        input_layout.addRow("Cycle String:", self.cycle_input)
        self.btn_load = QPushButton("Load Curve Pair")
        self.btn_load.setStyleSheet("background-color: #e3f2fd; font-weight: bold;")
        self.btn_load.clicked.connect(self.load_curves)
        input_layout.addRow(self.btn_load)
        left_layout.addWidget(input_group)

        # --- Actions Section ---
        actions_group = QGroupBox("Calculations")
        actions_layout = QVBoxLayout(actions_group)
        btn_row = QHBoxLayout()
        self.btn_compute_genus = QPushButton("Genus")
        self.btn_compute_genus.clicked.connect(self.compute_genus)
        self.btn_compute_dist = QPushButton("Distance")
        self.btn_compute_dist.clicked.connect(self.compute_distance)
        self.btn_compute_faces = QPushButton("Faces")
        self.btn_compute_faces.clicked.connect(self.compute_faces)
        btn_row.addWidget(self.btn_compute_genus)
        btn_row.addWidget(self.btn_compute_dist)
        btn_row.addWidget(self.btn_compute_faces)
        actions_layout.addLayout(btn_row)
        
        self.btn_perms = QPushButton("Find Distance 4+ Permutations")
        self.btn_perms.clicked.connect(self.compute_perms)
        actions_layout.addWidget(self.btn_perms)
        left_layout.addWidget(actions_group)

        # --- Permutations List ---
        self.perms_group = QGroupBox("Calculated Permutations")
        perms_layout = QVBoxLayout(self.perms_group)
        self.perms_list = QListWidget()
        self.perms_list.itemClicked.connect(self.select_perm)
        perms_layout.addWidget(self.perms_list)
        left_layout.addWidget(self.perms_group)
        self.perms_group.hide()

        # --- Results Output ---
        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        self.output_console.setStyleSheet("background-color: #f5f5f5; font-family: monospace; font-size: 11px;")
        left_layout.addWidget(QLabel("<b>Output Console:</b>"))
        left_layout.addWidget(self.output_console)

        # Right Panel (Visualization)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        splitter.addWidget(right_panel)

        self.tabs = QTabWidget()
        right_layout.addWidget(self.tabs)

        # Initialize Tabs
        self.tab_guide = QTextEdit()
        self.tab_guide.setReadOnly(True)
        self.setup_guide()

        self.tab_fund_domain = QWidget()
        self.fd_layout = QVBoxLayout(self.tab_fund_domain)
        self.fund_domain_canvas = MplCanvas(self, width=5, height=4, dpi=100, is_3d=False)
        self.fd_layout.addWidget(self.fund_domain_canvas)

        self.tab_surface_3d = QWidget()
        self.s3d_layout = QVBoxLayout(self.tab_surface_3d)
        self.surface_3d_canvas = MplCanvas(self, width=5, height=4, dpi=100, is_3d=True)
        self.s3d_layout.addWidget(self.surface_3d_canvas)

        self.tab_handlebody = QWidget()
        self.hb_layout = QVBoxLayout(self.tab_handlebody)
        self.handlebody_canvas = MplCanvas(self, width=5, height=4, dpi=100, is_3d=True)
        self.hb_layout.addWidget(self.handlebody_canvas)

        self.tab_neighborhoods = QWidget()
        self.nh_layout = QVBoxLayout(self.tab_neighborhoods)
        self.neighborhoods_canvas = MplCanvas(self, width=5, height=4, dpi=100, is_3d=False)
        self.nh_layout.addWidget(self.neighborhoods_canvas)

        self.tabs.addTab(self.tab_guide, "User Guide")
        self.tabs.addTab(self.tab_fund_domain, "Fundamental Domain")
        self.tabs.addTab(self.tab_surface_3d, "Surface in R^3")
        self.tabs.addTab(self.tab_handlebody, "Handlebody Model")
        self.tabs.addTab(self.tab_neighborhoods, "Rigid Expansions")

        # Set splitter sizes
        splitter.setSizes([400, 800])

    def setup_guide(self):
        guide_text = """
        <h2 style='color: #1976d2;'>MICC - Topological Analysis</h2>
        <p>This application implements the Metric in the Curve Complex algorithm.</p>
        
        <h3>1. Input Syntax</h3>
        <p><b>Ladder Identification:</b> Reference curve &alpha; is a midline. Points 1...n on &alpha; are identified via arcs on the "top" and "bottom" sides.</p>
        <p><b>Cycle String:</b> Encodes the sequence of intersections and their crossing signs (+ for top-to-bottom, - for bottom-to-top).</p>
        
        <h3>2. Fundamental Domain Visualization</h3>
        <ul>
            <li>The surface is represented as a <b>4g-gon</b>.</li>
            <li>Edges identified by <b>a_i</b> and <b>b_i</b> are labeled with orientation arrows.</li>
            <li>The reference curve <b>&alpha;</b> is shown in <font color='red'><b>Red</b></font>.</li>
            <li>Intersections are labeled <b>1...n</b> along the &alpha; edges.</li>
            <li>The non-referential curve <b>&beta;</b> is drawn as arcs in <font color='blue'><b>Blue (Top)</b></font> and <font color='green'><b>Green (Bottom)</b></font>.</li>
        </ul>
        
        <h3>3. Analysis Tools</h3>
        <ul>
            <li><b>Genus:</b> Computes the minimal filling genus.</li>
            <li><b>Distance:</b> Computes distance between &alpha; and &beta; in the curve graph.</li>
            <li><b>Permutations:</b> Evaluates all valid curve identifications for the given intersections to find distance 4+ candidates.</li>
        </ul>
        """
        self.tab_guide.setHtml(guide_text)

    def load_example_data(self, index):
        example_name = self.example_box.currentText()
        data = self.examples.get(example_name)
        if data:
            self.top_input.setText(data["top"])
            self.bottom_input.setText(data["bottom"])
            self.cycle_input.setText(data["cycle"])

    def print_to_console(self, text):
        self.output_console.append(text)

    def correct_input(self, ladder_str):
        ladder = [s.strip() for s in ladder_str.split(',') if s.strip()]
        return [int(num) for num in ladder]

    def load_curves(self):
        cycle_str = self.cycle_input.text().strip()
        top_str = self.top_input.text().strip()
        bottom_str = self.bottom_input.text().strip()

        try:
            if cycle_str:
                success, msg = self.core.set_curve_from_cycle(cycle_str)
            else:
                if not top_str or not bottom_str:
                    QMessageBox.warning(self, "Input Error", "Provide ladder data or cycle string.")
                    return
                top = self.correct_input(top_str)
                bottom = self.correct_input(bottom_str)
                if not self.core.validate_input(top, bottom):
                    QMessageBox.warning(self, "Input Error", "Invalid ladder definition.")
                    return
                success, msg = self.core.set_curve_from_ladder(top, bottom)

            if success:
                self.print_to_console(f"<b>Loaded:</b> {msg}")
                self.perms_group.hide()
                self.update_visualizations()
            else:
                self.print_to_console(f"<font color='orange'><b>Multicurve:</b> {msg}</font>")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Load Error: {str(e)}")

    def compute_genus(self):
        if not self.core.curve: return
        genus = self.core.get_genus()
        self.print_to_console(f"Filling Genus: <b>{genus}</b>")

    def compute_distance(self):
        if not self.core.curve: return
        self.print_to_console("<i>Calculating distance...</i>")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            dist = self.core.get_distance()
            self.print_to_console(f"Computed Distance: <b>{dist}</b>")
        finally:
            QApplication.restoreOverrideCursor()

    def compute_faces(self):
        if not self.core.curve: return
        bdy = self.core.get_boundaries()
        sol = self.core.get_solution()
        if bdy:
            self.print_to_console(f"Faces: {bdy[0]}, Bigons: {bdy[1]}")
            self.print_to_console(f"Solution: {sol}")

    def compute_perms(self):
        if not self.core.ladder: return
        self.print_to_console("<i>Computing all permutations...</i>")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            perms = self.core.get_permutations()
            self.perms_list.clear()
            for idx, p in perms.items():
                self.perms_list.addItem(f"Curve {idx} (Dist: {p.distance})")
            self.perms_group.show()
            self.print_to_console(f"Found {len(perms)} permutations.")
        finally:
            QApplication.restoreOverrideCursor()

    def select_perm(self, item):
        idx = int(item.text().split(' ')[1])
        self.core.curve = self.core.perms[idx]
        self.update_visualizations()

    def draw_fundamental_domain(self):
        ax = self.fund_domain_canvas.axes
        ax.clear()
        
        if not self.core.curve:
            self.fund_domain_canvas.draw()
            return
            
        genus = int(self.core.get_genus() or 1)
        num_sides = 4 * genus
        angles = np.linspace(0, 2 * np.pi, num_sides + 1)
        vx = np.cos(angles)
        vy = np.sin(angles)
        
        # Draw edges with arrows
        for i in range(num_sides):
            ax.plot([vx[i], vx[i+1]], [vy[i], vy[i+1]], 'k-', lw=1.5)
            # Arrow
            mid_x, mid_y = (vx[i]+vx[i+1])/2, (vy[i]+vy[i+1])/2
            dx, dy = vx[i+1]-vx[i], vy[i+1]-vy[i]
            # Simple triangle arrow
            ax.arrow(mid_x - dx*0.05, mid_y - dy*0.05, dx*0.01, dy*0.01, 
                     head_width=0.04, head_length=0.08, fc='black', ec='black')
        
        # Labels
        labels = []
        for i in range(1, genus + 1):
            labels.extend([f'$a_{i}$', f'$b_{i}$', f'$a_{i}^{{-1}}$', f'$b_{i}^{{-1}}$'])
        for i in range(num_sides):
            mid_angle = (angles[i] + angles[i+1]) / 2
            ax.text(1.15 * np.cos(mid_angle), 1.15 * np.sin(mid_angle), 
                    labels[i], ha='center', va='center', fontsize=10)

        # Highlight Alpha (reference curve) on generator a1
        # In the 4g-gon, alpha corresponds to identified edges 0 and 2
        ax.plot([vx[0], vx[1]], [vy[0], vy[1]], 'r-', lw=3, alpha=0.8, label=r'$\alpha$')
        ax.plot([vx[2], vx[3]], [vy[2], vy[3]], 'r-', lw=3, alpha=0.8)

        # Map Ladder indices to points on edges
        n = self.core.curve.n
        t_vals = np.linspace(0.1, 0.9, n)
        
        # p_top are points on edge 0 (a1)
        p_top_x = vx[0] + t_vals * (vx[1] - vx[0])
        p_top_y = vy[0] + t_vals * (vy[1] - vy[0])
        
        # p_bot are points on edge 2 (a1^-1) - reversed direction
        p_bot_x = vx[2] + (1 - t_vals) * (vx[3] - vx[2])
        p_bot_y = vy[2] + (1 - t_vals) * (vy[3] - vy[2])
        
        # Draw Arcs
        top_data = self.core.curve.top
        bot_data = self.core.curve.bottom
        
        def draw_bezier(p1, p2, color):
            mx, my = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
            cx, cy = mx*0.5, my*0.5 # Control point towards center
            ts = np.linspace(0, 1, 30)
            bx = (1-ts)**2 * p1[0] + 2*(1-ts)*ts * cx + ts**2 * p2[0]
            by = (1-ts)**2 * p1[1] + 2*(1-ts)*ts * cy + ts**2 * p2[1]
            ax.plot(bx, by, color + '-', lw=1, alpha=0.6)

        seen_top = set()
        for i in range(n):
            j = int(top_data[i])
            if (i,j) not in seen_top and (j,i) not in seen_top:
                draw_bezier((p_top_x[i], p_top_y[i]), (p_top_x[j], p_top_y[j]), 'b')
                seen_top.add((i,j))
        
        seen_bot = set()
        for i in range(n):
            j = int(bot_data[i])
            if (i,j) not in seen_bot and (j,i) not in seen_bot:
                draw_bezier((p_bot_x[i], p_bot_y[i]), (p_bot_x[j], p_bot_y[j]), 'g')
                seen_bot.add((i,j))

        # Add point labels for intersection index
        for i in range(n):
            ax.text(p_top_x[i]*1.05, p_top_y[i]*1.05, str(i+1), fontsize=7, color='red')

        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(f"Fundamental Domain ($g={genus}, n={n}$)")
        self.fund_domain_canvas.draw()

    def draw_3d_surface(self):
        ax = self.surface_3d_canvas.axes
        ax.clear()
        if not self.core.curve:
            self.surface_3d_canvas.draw()
            return
        genus = int(self.core.get_genus() or 1)
        # Generate a torus manifold
        n = 50
        theta = np.linspace(0, 2.*np.pi, n)
        phi = np.linspace(0, 2.*np.pi, n)
        theta, phi = np.meshgrid(theta, phi)
        c, a = 2, 0.7
        x = (c + a*np.cos(theta)) * np.cos(phi)
        y = (c + a*np.cos(theta)) * np.sin(phi)
        z = a * np.sin(theta)
        ax.plot_surface(x, y, z, color='skyblue', alpha=0.4, edgecolor='none')
        ax.set_title(f"Genus {genus} Surface Embedding")
        ax.set_axis_off()
        self.surface_3d_canvas.draw()

    def draw_handlebody(self):
        ax = self.handlebody_canvas.axes
        ax.clear()
        if not self.core.curve:
            self.handlebody_canvas.draw()
            return
        u, v = np.mgrid[0:2*np.pi:30j, 0:np.pi:15j]
        x = np.cos(u)*np.sin(v)
        y = np.sin(u)*np.sin(v)
        z = np.cos(v)
        ax.plot_wireframe(x, y, z, color='grey', alpha=0.3, lw=0.5)
        ax.set_title("Handlebody Structural Model")
        ax.set_axis_off()
        self.handlebody_canvas.draw()

    def draw_rigid_expansions(self):
        ax = self.neighborhoods_canvas.axes
        ax.clear()
        if not self.core.curve:
            self.neighborhoods_canvas.draw()
            return
        genus = int(self.core.get_genus() or 1)
        G = nx.DiGraph()
        # Layer 0
        seeds = [f"a_{i}" for i in range(1, 2*genus + 3)] 
        for n in seeds: G.add_node(n, layer=0)
        # Layer 1
        y1 = [f"b_{i}" for i in range(1, genus + 2)]
        for n in y1:
            G.add_node(n, layer=1)
            for sn in np.random.choice(seeds, 3, replace=False): G.add_edge(sn, n)
        # Draw
        pos = nx.multipartite_layout(G, subset_key="layer")
        nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=seeds, node_color='#bbdefb', label="Y^0 Seed")
        nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=y1, node_color='#c8e6c9', label="Y^1 Expansion")
        nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.4, arrows=True)
        nx.draw_networkx_labels(G, pos, ax=ax, font_size=8)
        ax.set_title("Rigid Expansion Graph")
        ax.legend(loc='lower left', fontsize=8)
        ax.axis('off')
        self.neighborhoods_canvas.draw()

    def update_visualizations(self):
        self.draw_fundamental_domain()
        self.draw_3d_surface()
        self.draw_handlebody()
        self.draw_rigid_expansions()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = MiccGUI()
    gui.show()
    sys.exit(app.exec())
