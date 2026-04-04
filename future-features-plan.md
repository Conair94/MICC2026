# MICC Future Features Plan

This document outlines the planned features and improvements for the next phase of the MICC project, following the Python 3 and Pybind11 modernization.

## 1. Graphical User Interface (GUI)
- **Goal:** Develop an intuitive application with a real GUI to enhance ease of use over the current CLI.
- **Approach:** Utilize PyQt6 or PySide6 to build the frontend. The `MiccCore` class has already been decoupled from the CLI to serve as the backend engine.

## 2. Curve Visualization
- **Goal:** Provide visual representations of curves using a variety of topological models.
- **Essential Models:**
  - **Fundamental Domain:** A 2D polygon representation showing boundary identifications and curve arcs.
  - **Surface embedded in $\mathbb{R}^3$:** A 3D view of the closed surface with the curves mapped onto it.
  - **Handlebody Model:** A 3D handlebody visualization similar to the sketches found in the original algorithm documentation notes.

## 3. Curve Neighborhoods and Rigid Expansions
- **Goal:** Visualize neighborhoods of curves to explore the exhaustion of the curve complex via rigid sets.
- **Concept:** Given a full multiset of curves (e.g., a filling set or a pants decomposition), visualize the family of curves that are "one away" (disjoint) from a sub-family of $n-1$ curves in the set.
- **Academic Foundation:**
  - Based on the concept of rigid sets by Aramayona and Leininger (2014).
  - Incorporates the work of **Jesus Hernandez Hernandez (arXiv:1611.08010)**, whose approach to exhaustion via rigid expansions is particularly amenable to topological visualization.
- **Significance:** By iteratively expanding the set of curves through these neighborhoods, the tool can simulate the finite exhaustion of the infinite curve complex.
- **Visual implementation:**
  - Highlight the sub-family of $n-1$ curves on the chosen topological model.
  - Dynamically generate and overlay all possible disjoint curves (the link of the sub-family) that exist within the remaining sub-surface (e.g., a four-holed sphere or one-holed torus).

## 4. Parallelization
- **Goal:** Speed up computations by leveraging multi-core architectures.
- **Approach:**
  - Parallelize the graph search and DFS algorithms (potentially within the Pybind11 C++ module using OpenMP or C++ threads).
  - Parallelize the Python-level processing, such as iterating over permutations or independent distance evaluations.

## 5. Full Algorithm Implementation (Long-term Stretch Goal)
- **Goal:** Implement the complete "Efficient Geodesic Algorithm" (EGA) from the original research paper (Birman, Margalit, Menasco, 2016).
- **Key Enhancements Needed:**
  - Implement intersection bound pruning ($|\alpha_1 \cap \gamma| \leq d-1$) to efficiently generate candidates for the next geodesic step.
  - Expand support to systematically determine distances $d > 4$.
  - Implement complexity-reducing "surgery" operations for non-efficient geodesics, replacing the current exponential exhaustive search with the effective finite search.
