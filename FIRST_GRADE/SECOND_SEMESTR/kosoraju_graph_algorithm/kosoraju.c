#include "graph.h"
#include "kosoraju.h"
#include "stack.h"
#include <stdio.h>
#include <stdlib.h>


void print_result(Graph* graph)
{
    int component_num = 1, component_size, max_component = 0;

    for (int i = 0; i < graph->vertex_num; i++)
        if (graph->visited[i] > max_component)
            max_component = graph->visited[i];

    for (int component = 1; component <= max_component; component++)
    {
        component_size = 0;

        for (int i = 0; i < graph->vertex_num; i++)
            if (graph->visited[i] == component)
                component_size++;

        if (component_size > 0)
        {
            printf("Component %d: ", component_num++);
            for (int i = 0; i < graph->vertex_num; i++)
                if (graph->visited[i] == component)
                    printf("%d ", i + 1);
            putchar('\n');
        }
    }
}


void kosoraju(Graph *graph)
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
    print_result(graph);
}
