#include "graph.h"
#include "stack.h"
#include <stdio.h>
#include <stdlib.h>

#define VERTEX_MAX 2000
#define EDGE_MAX ((VERTEX_MAX * (VERTEX_MAX + 1) / 2))


void dfs(Graph* graph, int vertex, int component, int** connections, Stack* stack)
{
    graph->visited[vertex] = component;

    for (int i = 0; i < graph->vertex_num; i++)
        if (connections[vertex][i] && !graph->visited[i])
            dfs(graph, i, component, connections, stack);

    if (stack != NULL)
        push(stack, vertex);
}


void kosaraju(Graph *graph)
{
    int paint_code = 0;
    Stack stack;
    init_stack(&stack, graph->vertex_num);

    for (int vertex = 0; vertex < graph->vertex_num; vertex++)
        if (!graph->visited[vertex])
            dfs(graph, vertex, ++paint_code, graph->connections, &stack);

    for (int i = 0; i < graph->vertex_num; i++)
        graph->visited[i] = 0;

    while (stack.top != -1)
    {
        int vertex = pop(&stack);
        if (!graph->visited[vertex])
            dfs(graph, vertex, ++paint_code, graph->transposed_connections, NULL);
    }

    free(stack.data);
}


int error_check(int edge_num, int vertex_num)
{
    if (vertex_num < 0 || vertex_num > VERTEX_MAX)
    {
        puts("bad number of vertices");
        return -1;
    }

    if (edge_num < 0 || edge_num > EDGE_MAX)
    {
        puts("bad number of edges");
        return -1;
    }

    return 0;
}


int main() {
    int component_size, component_num = 1, edge_end, edge_num, edge_start,
    max_component, vertex_num;
    Graph graph;

    scanf("%d", &vertex_num);
    scanf("%d", &edge_num);

    if (error_check(edge_num, vertex_num) == -1)
        return 0;

    init_graph(&graph, vertex_num);

    for (int i = 0; i < edge_num; i++)
    {
        scanf("%d %d", &edge_start, &edge_end);

        if (edge_start == edge_end)
        {
            puts("bad vertex");
            free_graph(&graph);
            return 0;
        }

        if (edge_start < 1 || edge_start > vertex_num || edge_end < 1 || edge_end > vertex_num)
        {
            puts("bad vertex");
            free_graph(&graph);
            return 0;
        }

        add_edge(&graph, edge_start - 1, edge_end - 1);
    }

    kosaraju(&graph);

    max_component = 0;
    for (int i = 0; i < graph.vertex_num; i++)
        if (graph.visited[i] > max_component)
            max_component = graph.visited[i];


    for (int component = 1; component <= max_component; component++)
    {
        component_size = 0;

        for (int i = 0; i < graph.vertex_num; i++)
            if (graph.visited[i] == component)
                component_size++;

        if (component_size > 0)
        {
            printf("Component %d: ", component_num++);
            for (int i = 0; i < graph.vertex_num; i++)
                if (graph.visited[i] == component)
                    printf("%d ", i + 1);
            putchar('\n');
        }
    }

    free_graph(&graph);
    return 0;
}
