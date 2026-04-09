# Rigid Seed Visualization

Focused on visualizing strongly rigid finite seeds and their rigid expansions in the curve complex, as described in arXiv:1611.08010v1 "Exhaustion of the curve graph via rigid expansions" by Jesús Hernández Hernández.

## Project Goals
- **Relational Structure Visualization:** Visualizing the intersection graph of curves using graph-theoretic tools like `networkx`.
- **Surface Depiction:** Accurately depicting curves inside a surface using `flipper` or `curver`.
- **Rigid Seed Analysis:** Exploring and visualizing the rigid expansion process.

## Modern Tooling
- **[curver](https://markcbell.co.uk/software.html#curver-software):** Efficient calculations in the curve complex.
- **[flipper](https://markcbell.co.uk/software.html#flipper-software):** Dynamics of mapping classes and laminations on surfaces. Use `python3 -m flipper.app` to launch the GUI for interactive curve depiction.

## Dependencies
- `curver`
- `flipper`
- `networkx`
- `matplotlib`
- `scipy`

## Usage

### Relational Structure GUI
Launch the custom GUI to visualize intersection graphs of curve seeds:
```bash
python3 src/gui.py
```
- **Surface Selection:** Adjust Genus and Punctures.
- **Curve Input:** Enter comma-separated curve names (e.g., `a_0, b_0, c_0`).
- **Examples:** Click buttons like "Aramayona-Leininger (G3)" to load classic rigid seeds.

### Surface Depiction
Use `flipper`'s built-in GUI for high-quality surface rendering:
```bash
python3 -m flipper.app
```
