#include "graph.h"
#include "kosoraju.h"
#include <stdio.h>

#define VERTEX_MAX 2000
#define EDGE_MAX ((VERTEX_MAX * (VERTEX_MAX + 1) / 2))


// Graph input issues checking function
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
    int edge_end, edge_num, edge_start,
    vertex_num;
    Graph graph;

    scanf("%d", &vertex_num);
    scanf("%d", &edge_num);

    if (error_check(edge_num, vertex_num) == -1)
        return 0;

    init_graph(&graph, vertex_num);

    for (int i = 0; i < edge_num; i++)
    {
        scanf("%d %d", &edge_start, &edge_end);

        // Checking for cycle of a graph
        if (edge_start == edge_end)
        {
            puts("bad vertex");
            free_graph(&graph);
            return 0;
        }

        // Checking limits of vertices
        if (edge_start < 1 || edge_start > vertex_num || edge_end < 1 || edge_end > vertex_num)
        {
            puts("bad vertex");
            free_graph(&graph);
            return 0;
        }

        add_edge(&graph, edge_start - 1, edge_end - 1);
    }

    kosoraju(&graph);
    free_graph(&graph);
    return 0;
}
