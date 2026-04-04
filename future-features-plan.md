# MICC Future Features Plan

This document outlines the planned features and improvements for the next phase of the MICC project, following the Python 3 and Pybind11 modernization.

## 1. Graphical User Interface (GUI) & User Experience
- **Goal:** Develop an intuitive application with a real GUI to enhance ease of use over the current CLI.
- **Current Status:** Basic PyQt6 implementation with Fundamental Domain and 3D placeholders.
- **Pending Improvements:**
  - **Educational Onboarding:** Provide better, interactive instructions for how to represent curves numerically (Ladder and Cycle notation) for new users.
  - **Example Transparency:** Make the provided mathematical examples more transparent, showing their significance and underlying data structure clearly.
  - **Interactive Drawing:** Implement the ability to select genus ahead of time and "draw" a curve onto the model, which the software then quantifies into ladder notation automatically.

## 2. Advanced Curve Visualization
- **Fundamental Domain:** (Completed) 2D polygon with orientation arrows and Bezier-linked arcs.
- **Surface embedded in $\mathbb{R}^3$:** (In Progress) Needs fix. Integrate actual 3D surface mapping. Explore basic physics simulations on the 3D curve to ensure optimal "tight" topological placement.
- **Handlebody Model:** (In Progress) Needs fix. Implement a richer 3D model matching original documentation sketches.

## 3. Curve Neighborhoods and Rigid Expansions
- **Goal:** Visualize neighborhoods of curves to explore the exhaustion of the curve complex via rigid sets.
- **Current Status:** Conceptual NetworkX graph implemented.
- **Pending Improvements:** Make rigid body visualizations richer and more interactive, integrating the work of **Jesus Hernandez Hernandez (arXiv:1611.08010)** more deeply into the visual flow.

## 4. Parallelization
- **Goal:** Speed up computations by leveraging multi-core architectures.
- **Current Status:** `test_permutations` parallelized using `ProcessPoolExecutor`.
- **Future:** Parallelize graph search in C++ (Pybind11).

## 5. Full Algorithm Implementation (Long-term Stretch Goal)
- **Goal:** Implement the complete "Efficient Geodesic Algorithm" (EGA) from the original research paper (Birman, Margalit, Menasco, 2016).
- **Key Enhancements Needed:**
  - Implement intersection bound pruning ($|\alpha_1 \cap \gamma| \leq d-1$).
  - Expand support to systematically determine distances $d > 4$.
  - Implement complexity-reducing "surgery" operations.
