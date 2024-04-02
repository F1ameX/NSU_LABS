#include "graph.h"
#include "kosoraju.h"
#include "stack.h"
#include <stdio.h>
#include <stdlib.h>


void print_result(Graph* graph)
{
    int component_num = 1, component_size, max_component = 0;

    // Find first component by the number in visited array
    for (int i = 0; i < graph->vertex_num; i++)
        if (graph->visited[i] > max_component)
            max_component = graph->visited[i];

    // Printing result
    for (int component = 1; component <= max_component; component++)
    {
        component_size = 0;
        // If component found increasing size
        for (int i = 0; i < graph->vertex_num; i++)
            if (graph->visited[i] == component)
                component_size++;

        // By the size find all component vertices and print
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

    // Making a DFS with all non-visited vertices
    for (int vertex = 0; vertex < graph->vertex_num; vertex++)
        if (!graph->visited[vertex])
            dfs(graph, vertex, ++paint_code, graph->edge, &stack);

    // Reset visited array before transposed DFS check
    for (int i = 0; i < graph->vertex_num; i++)
        graph->visited[i] = 0;

    // With already formed from first DFS stack making component
    while (stack.top != -1)
    {
        int vertex = pop(&stack);
        if (!graph->visited[vertex])
            dfs(graph, vertex, ++paint_code, graph->transposed_edge, NULL);
    }

    free(stack.data);
    print_result(graph);
}
