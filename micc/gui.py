import sys
import os
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTextEdit, QTabWidget, QFormLayout,
                             QMessageBox, QSplitter, QComboBox)
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
        self.setGeometry(100, 100, 1100, 850)

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
        example_group = QWidget()
        example_layout = QVBoxLayout(example_group)
        example_layout.addWidget(QLabel("<b>Load Mathematical Examples:</b>"))
        self.example_box = QComboBox()
        self.example_box.addItems(list(self.examples.keys()))
        self.example_box.currentIndexChanged.connect(self.load_example_data)
        example_layout.addWidget(self.example_box)
        left_layout.addWidget(example_group)

        # --- Input Section ---
        input_group = QWidget()
        input_layout = QFormLayout(input_group)
        
        input_layout.addRow(QLabel("<b>Manual Input:</b>"), QLabel(""))
        self.top_input = QLineEdit()
        self.top_input.setPlaceholderText("Comma separated integers")
        
        self.bottom_input = QLineEdit()
        self.bottom_input.setPlaceholderText("Comma separated integers")
        
        self.cycle_input = QLineEdit()
        self.cycle_input.setPlaceholderText("e.g. 1+2-3+ (Overrides ladder)")

        input_layout.addRow("Ladder Top:", self.top_input)
        input_layout.addRow("Ladder Bottom:", self.bottom_input)
        input_layout.addRow("Cycle String:", self.cycle_input)

        self.btn_load = QPushButton("Load Curve Pair")
        self.btn_load.setStyleSheet("background-color: #e1f5fe; font-weight: bold;")
        self.btn_load.clicked.connect(self.load_curves)
        input_layout.addRow(self.btn_load)

        left_layout.addWidget(input_group)

        # --- Actions Section ---
        actions_layout = QHBoxLayout()
        self.btn_compute_genus = QPushButton("Compute Genus")
        self.btn_compute_genus.clicked.connect(self.compute_genus)
        
        self.btn_compute_dist = QPushButton("Compute Distance")
        self.btn_compute_dist.clicked.connect(self.compute_distance)
        
        self.btn_compute_faces = QPushButton("Compute Faces")
        self.btn_compute_faces.clicked.connect(self.compute_faces)

        actions_layout.addWidget(self.btn_compute_genus)
        actions_layout.addWidget(self.btn_compute_dist)
        actions_layout.addWidget(self.btn_compute_faces)
        
        left_layout.addLayout(actions_layout)

        # --- Results Output ---
        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        self.output_console.setStyleSheet("background-color: #f5f5f5; font-family: monospace;")
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

        self.tabs.addTab(self.tab_guide, "Introduction & Syntax")
        self.tabs.addTab(self.tab_fund_domain, "Fundamental Domain")
        self.tabs.addTab(self.tab_surface_3d, "Surface in R^3")
        self.tabs.addTab(self.tab_handlebody, "Handlebody Model")
        self.tabs.addTab(self.tab_neighborhoods, "Rigid Expansions")

        # Set splitter sizes
        splitter.setSizes([450, 650])

    def setup_guide(self):
        guide_text = """
        <h2>Welcome to MICC</h2>
        <p>MICC (Metric in the Curve Complex) is a tool for studying the distance between simple closed curves on surfaces.</p>
        
        <h3>1. Understanding the Syntax</h3>
        <p>There are two primary ways to define a curve in MICC:</p>
        
        <h4>A. Ladder Identifications</h4>
        <p>A curve is often represented by identifying points on a "ladder". You provide two lists of integers:</p>
        <ul>
            <li><b>Ladder Top:</b> A comma-separated list representing identifications on the top of the reference curve.</li>
            <li><b>Ladder Bottom:</b> A comma-separated list representing identifications on the bottom.</li>
        </ul>
        <p><i>Example:</i> Top: 4,3,3,1,0,0 | Bottom: 5,5,4,2,2,1</p>
        
        <h4>B. Cycle Notation</h4>
        <p>A more concise way to describe the curve's path. It uses integers and signs (+/-).</p>
        <ul>
            <li>Numbers indicate the intersection index.</li>
            <li>'+' indicates crossing the reference curve from top to bottom.</li>
            <li>'-' indicates crossing from bottom to top.</li>
        </ul>
        <p><i>Example:</i> 1+2-3+4-</p>
        
        <h3>2. Features</h3>
        <ul>
            <li><b>Compute Genus:</b> Calculates the minimal genus of the surface on which the curves fill.</li>
            <li><b>Compute Distance:</b> Determines the distance in the curve complex (up to distance 4).</li>
            <li><b>Compute Faces:</b> Analyzes the polygons in the complement of the curve pair.</li>
            <li><b>Rigid Expansions:</b> Visualizes the process of exhausting the curve graph using finite rigid sets (Hernandez 2019).</li>
        </ul>
        
        <h3>3. Getting Started</h3>
        <p>Select an entry from the <b>"Load Mathematical Examples"</b> dropdown to see how the inputs are formatted, then click <b>"Load Curve Pair"</b> to begin calculations.</p>
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
                    QMessageBox.warning(self, "Input Error", "Please provide top and bottom ladder definitions, or a cycle string.")
                    return
                
                top = self.correct_input(top_str)
                bottom = self.correct_input(bottom_str)
                
                if not self.core.validate_input(top, bottom):
                    QMessageBox.warning(self, "Input Error", "Invalid curve definition. Ensure every index appears exactly twice.")
                    return
                
                success, msg = self.core.set_curve_from_ladder(top, bottom)

            if success:
                self.print_to_console(f"<b>Loaded:</b> {msg}")
                self.update_visualizations()
            else:
                self.print_to_console(f"<font color='red'><b>Warning:</b> Loaded multicurve: {msg}</font>")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while loading curves: {str(e)}")

    def compute_genus(self):
        if not self.core.curve:
            self.print_to_console("Error: No curve loaded.")
            return
        genus = self.core.get_genus()
        self.print_to_console(f"Genus computed: <b>{genus}</b>")

    def compute_distance(self):
        if not self.core.curve:
            self.print_to_console("Error: No curve loaded.")
            return
        self.print_to_console("<i>Computing distance in curve complex...</i>")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            dist = self.core.get_distance()
            self.print_to_console(f"Distance: <b>{dist}</b>")
        finally:
            QApplication.restoreOverrideCursor()

    def compute_faces(self):
        if not self.core.curve:
            self.print_to_console("Error: No curve loaded.")
            return
        bdy = self.core.get_boundaries()
        sol = self.core.get_solution()
        if bdy:
            self.print_to_console(f"Faces components: {bdy[0]}, Bigons detected: {bdy[1]}")
            self.print_to_console(f"Vector solution: {sol}")

    def draw_fundamental_domain(self):
        ax = self.fund_domain_canvas.axes
        ax.clear()
        
        if not self.core.curve:
            self.fund_domain_canvas.draw()
            return
            
        genus = int(self.core.get_genus() or 1)
        num_sides = 4 * genus
        angles = np.linspace(0, 2 * np.pi, num_sides + 1)
        x = np.cos(angles)
        y = np.sin(angles)
        
        ax.plot(x, y, 'k-', lw=2)
        
        labels = []
        for i in range(1, genus + 1):
            labels.extend([f'$a_{i}$', f'$b_{i}$', f'$a_{i}^{{-1}}$', f'$b_{i}^{{-1}}$'])
            
        for i in range(num_sides):
            mid_angle = (angles[i] + angles[i+1]) / 2
            mid_x = 1.15 * np.cos(mid_angle)
            mid_y = 1.15 * np.sin(mid_angle)
            ax.text(mid_x, mid_y, labels[i], ha='center', va='center', fontsize=12)

        top_ladder = self.core.ladder[0]
        n = len(top_ladder)
        for i in range(min(n, num_sides)):
            start_idx = i % num_sides
            end_idx = top_ladder[i] % num_sides if top_ladder[i] is not None else (i+1)%num_sides
            start_angle = (angles[start_idx] + angles[start_idx+1]) / 2
            end_angle = (angles[end_idx] + angles[end_idx+1]) / 2
            sx, sy = np.cos(start_angle), np.sin(start_angle)
            ex, ey = np.cos(end_angle), np.sin(end_angle)
            ax.plot([sx, ex], [sy, ey], 'b-', alpha=0.6)

        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title("Fundamental Domain Representation")
        self.fund_domain_canvas.draw()

    def draw_3d_surface(self):
        ax = self.surface_3d_canvas.axes
        ax.clear()
        if not self.core.curve:
            self.surface_3d_canvas.draw()
            return
            
        genus = int(self.core.get_genus() or 1)
        n = 100
        theta = np.linspace(0, 2.*np.pi, n)
        phi = np.linspace(0, 2.*np.pi, n)
        theta, phi = np.meshgrid(theta, phi)
        
        c, a = 2, 1
        x = (c + a*np.cos(theta)) * np.cos(phi)
        y = (c + a*np.cos(theta)) * np.sin(phi)
        z = a * np.sin(theta)
        
        ax.plot_surface(x, y, z, color='cyan', alpha=0.3, edgecolor='none')
        ax.set_title(f"3D Surface (Genus {genus} Placeholder)")
        ax.axis('off')
        self.surface_3d_canvas.draw()

    def draw_handlebody(self):
        ax = self.handlebody_canvas.axes
        ax.clear()
        if not self.core.curve:
            self.handlebody_canvas.draw()
            return
            
        u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
        x = np.cos(u)*np.sin(v)
        y = np.sin(u)*np.sin(v)
        z = np.cos(v)
        
        ax.plot_wireframe(x, y, z, color='gray', alpha=0.2)
        ax.set_title("Handlebody Model (Abstract Representation)")
        ax.axis('off')
        self.handlebody_canvas.draw()

    def draw_rigid_expansions(self):
        ax = self.neighborhoods_canvas.axes
        ax.clear()
        if not self.core.curve:
            self.neighborhoods_canvas.draw()
            return

        genus = int(self.core.get_genus() or 1)
        G = nx.DiGraph()
        
        seed_nodes = [f"a_{i}" for i in range(1, 2*genus + 3)] 
        for node in seed_nodes:
            G.add_node(node, layer=0)
            
        y1_nodes = [f"b_{i}" for i in range(1, genus + 2)]
        for node in y1_nodes:
            G.add_node(node, layer=1)
            for sn in np.random.choice(seed_nodes, 3, replace=False):
                G.add_edge(sn, node)
                
        y2_nodes = [f"c_{i}" for i in range(1, genus * 2)]
        for node in y2_nodes:
            G.add_node(node, layer=2)
            for yn in np.random.choice(y1_nodes + seed_nodes, 3, replace=False):
                G.add_edge(yn, node)

        pos = nx.multipartite_layout(G, subset_key="layer")
        nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=seed_nodes, node_color='lightblue', label="Y^0 (Principal Set)")
        nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=y1_nodes, node_color='lightgreen', label="Y^1 (1st Expansion)")
        nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=y2_nodes, node_color='lightcoral', label="Y^2 (2nd Expansion)")
        nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.3, arrows=True)
        nx.draw_networkx_labels(G, pos, ax=ax, font_size=8)
        
        ax.set_title("Exhaustion via Rigid Expansions\n(Conceptual Graph based on Hernandez 2019)")
        ax.legend(loc='lower right', fontsize=8)
        ax.axis('off')
        self.neighborhoods_canvas.draw()

    def update_visualizations(self):
        self.print_to_console("Updating visualizations...")
        self.draw_fundamental_domain()
        self.draw_3d_surface()
        self.draw_handlebody()
        self.draw_rigid_expansions()

def main():
    app = QApplication(sys.argv)
    gui = MiccGUI()
    gui.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
