#pragma once
#include "stack.h"


typedef struct Graph {
    int** connections;
    int** transposed_connections;
    int vertex_num;
    int* visited;
} Graph;


void add_edge(Graph* graph, int start, int end);
void dfs(Graph* graph, int vertex, int component, int** connections, Stack* stack);
void free_graph(Graph *graph);
void init_graph(Graph* graph, int vertex_num);
