#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <map>
#include <set>
#include <algorithm>
#include <climits>

namespace py = pybind11;

using std::map;
using std::vector;

// Reusing logic from util-dfs.cpp

void shift(vector<int> &path) {
    if (path.empty()) return;
    int min_val = INT_MAX;
    int min_at = 0;
    for (size_t i = 0; i < path.size(); i++) {
        if (path[i] < min_val) {
            min_val = path[i];
            min_at = i;
        }
    }
    vector<int> ret;
    for (size_t i = 0; i < path.size(); i++) {
        ret.push_back(path[(min_at + i) % path.size()]);
    }
    path = ret;
}

int count_val(const vector<int> &path, int val) {
    int count = 0;
    for (int p : path) {
        if (p == val) count++;
    }
    return count;
}

void remove_from_graph(map<int, vector<int>> &graph, int key, int val_to_remove) {
    vector<int> &adj_list = graph[key];
    adj_list.erase(std::remove(adj_list.begin(), adj_list.end(), val_to_remove), adj_list.end());
}

void dfs(int current_node, int start_node, vector<int> &current_path,
         map<int, vector<int>> &graph, map<int, vector<int>> &nodes_to_faces,
         vector<vector<int>> &loops) {
    
    if (current_path.size() >= 3) {
        map<int, int> intersection;
        for (int i = 0; i < 3; i++) {
            int node = current_path[current_path.size() - 3 + i];
            if (nodes_to_faces.count(node)) {
                for (int value : nodes_to_faces[node]) {
                    intersection[value]++;
                }
            }
        }
        int intersection_size = 0;
        for (auto const& [face, count] : intersection) {
            if (count == 3) {
                intersection_size++;
            }
            if (intersection_size == 2) {
                return;
            }
        }
    }

    if (current_node == start_node) {
        vector<int> path = current_path;
        shift(path);
        loops.push_back(path);
        return;
    } else {
        vector<int> current_adjacencies = graph[current_node];
        std::set<int> adj_list(current_adjacencies.begin(), current_adjacencies.end());
        
        for (int adjacent_node : adj_list) {
            if (count_val(current_path, adjacent_node) < 1) {
                current_path.push_back(adjacent_node);
                remove_from_graph(graph, current_node, adjacent_node);
                remove_from_graph(graph, adjacent_node, current_node);

                dfs(adjacent_node, start_node, current_path, graph, nodes_to_faces, loops);

                graph[current_node].push_back(adjacent_node);
                graph[adjacent_node].push_back(current_node);
                current_path.pop_back();
            }
        }
    }
}

vector<vector<int>> run_dfs(int current_node, int start_node, vector<int> current_path,
                            map<int, vector<int>> graph, map<int, vector<int>> nodes_to_faces) {
    vector<vector<int>> loops;
    
    // In util-dfs.cpp's main, it iterates over the graph if start_node is not provided or something.
    // Wait, let's check the original cdfs in cgraph.py or util-dfs.cpp's main.
    
    // Original util-dfs.cpp main:
    /*
    for(map<int, vector<int> >::iterator it =graph.begin(); it != graph.end(); it++){
        int start_node = it->first;
        vector<int> adjs = it->second;
        for(int i = 0; i < adjs.size();i++){
            current_node = adjs[i];
            vector<int> current_path;
            current_path.push_back(current_node);
            dfs(current_node, start_node, current_path, graph, nodes_to_faces, loops);
        }
    }
    */
    
    // Wait, the python cdfs function in cgraph.py passes arguments:
    // return dumps([current_node, start_node, current_path, graph, nodes_to_faces])
    
    // If current_path is provided (it's often [current_node]), we should use it.
    
    dfs(current_node, start_node, current_path, graph, nodes_to_faces, loops);
    return loops;
}

PYBIND11_MODULE(_micc_dfs, m) {
    m.doc() = "Pybind11 DFS module for MICC";
    m.def("cdfs", &run_dfs, "Perform DFS to find loops",
          py::arg("current_node"), py::arg("start_node"), py::arg("current_path"),
          py::arg("graph"), py::arg("nodes_to_faces"));
}
