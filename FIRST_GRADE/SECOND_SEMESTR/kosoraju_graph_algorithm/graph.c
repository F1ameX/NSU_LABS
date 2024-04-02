#include "graph.h"
#include "stack.h"
#include <stdlib.h>


void add_edge(Graph* graph, int start, int end)
{
    graph->edge[start][end] = 1;
    graph->transposed_edge[end][start] = 1;
}


// DFS function with component handler
void dfs(Graph* graph, int vertex, int component, int** connections, Stack* stack)
{
    graph->visited[vertex] = component;

    for (int i = 0; i < graph->vertex_num; i++)
        if (connections[vertex][i] && !graph->visited[i])
            dfs(graph, i, component, connections, stack);

    // Condition to direct(first) DFS
    if (stack != NULL)
        push(stack, vertex);
}


// Free graph memory function
void free_graph(Graph *graph)
{
    for (int i = 0; i < graph->vertex_num; i++) {
        free(graph->edge[i]);
        free(graph->transposed_edge[i]);
    }

    free(graph->edge);
    free(graph->transposed_edge);
    free(graph->visited);
}


// Graph initialization function
void init_graph(Graph* graph, int vertex_num) {
    graph->vertex_num = vertex_num;
    graph->edge = (int **)malloc(vertex_num * sizeof(int *));
    graph->transposed_edge = (int **)malloc(vertex_num * sizeof(int *));

    for (int i = 0; i < vertex_num; i++) {
        graph->edge[i] = (int *)calloc(vertex_num, sizeof(int));
        graph->transposed_edge[i] = (int *)calloc(vertex_num, sizeof(int));
    }

    graph->visited = (int *)calloc(vertex_num, sizeof(int));
}
