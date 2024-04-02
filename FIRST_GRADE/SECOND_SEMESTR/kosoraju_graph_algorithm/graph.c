#include "graph.h"
#include "stack.h"
#include <stdlib.h>


void add_edge(Graph* graph, int start, int end)
{
    graph->connections[start][end] = 1;
    graph->transposed_connections[end][start] = 1;
}


void dfs(Graph* graph, int vertex, int component, int** connections, Stack* stack)
{
    graph->visited[vertex] = component;

    for (int i = 0; i < graph->vertex_num; i++)
        if (connections[vertex][i] && !graph->visited[i])
            dfs(graph, i, component, connections, stack);

    if (stack != NULL)
        push(stack, vertex);
}


void free_graph(Graph *graph)
{
    for (int i = 0; i < graph->vertex_num; i++) {
        free(graph->connections[i]);
        free(graph->transposed_connections[i]);
    }

    free(graph->connections);
    free(graph->transposed_connections);
    free(graph->visited);
}


void init_graph(Graph* graph, int vertex_num) {
    graph->vertex_num = vertex_num;
    graph->connections = (int **)malloc(vertex_num * sizeof(int *));
    graph->transposed_connections = (int **)malloc(vertex_num * sizeof(int *));

    for (int i = 0; i < vertex_num; i++) {
        graph->connections[i] = (int *)calloc(vertex_num, sizeof(int));
        graph->transposed_connections[i] = (int *)calloc(vertex_num, sizeof(int));
    }

    graph->visited = (int *)calloc(vertex_num, sizeof(int));
}
