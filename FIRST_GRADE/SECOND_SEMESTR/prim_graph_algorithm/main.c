#include <limits.h>
#include <stdio.h>
#include <stdlib.h>

#define VERTEX_MAX 5000
#define EDGE_MAX ((vertex_num * (vertex_num + 1)) / 2)


typedef struct Edge{
    int start;
    int end;
    int weight;
}Edge;


int error_check(int vertex_num, int edge_num)
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


int min_key(int edge_num, int included[], int min_edge[])
{
    int min = INT_MAX, min_index;
    for (int i = 0; i < edge_num; i++)
    {
        if (included[i] == 0 && min_edge[i] < min)
        {
            min = min_edge[i];
            min_index = i;
        }
    }
    return min_index;
}

void prim(int** graph, int edge_num)
{
    int len, min_idx, parent[edge_num], min_edge[edge_num], included[edge_num];

    for (int i = 0; i < edge_num; i++)
    {
        min_edge[i] = INT_MAX;
        included[i] = 0;
    }

    min_edge[0] = 0;
    parent[0] = -1;

    for (int i = 0; i < edge_num - 1; i++)
    {
        min_idx = min_key(edge_num, included, min_edge);
        included[min_idx] = 1;
        for (int j = 0; j < edge_num; j++)
        {
            if (graph[min_idx][j] && included[j] == 0 && graph[min_idx][j] < min_edge[j])
            {
                parent[j] = min_idx;
                min_edge[j] = graph[min_idx][j];
            }
        }
    }

    len = 0;
    for (int i = 1; i < edge_num; i++)
        len += graph[i][parent[i]];

    if (len == 0)
        puts("no spanning tree");
    else
    {
        for (int i = 1; i < edge_num; i++)
            if (parent[i] + 1 < i + 1)
                printf("%d %d\n", parent[i] + 1, i + 1);
            else
                printf("%d %d\n", i + 1, parent[i] + 1);
    }
}


int main()
{
    int string_cnt = 0, vertex_num, edge_num, edge_start, edge_end, edge_weight;
    scanf("%d", &vertex_num);
    scanf("%d", &edge_num);

    if (error_check(vertex_num, edge_num) == -1)
        return 0;

    int** graph = (int**)malloc(vertex_num * sizeof(int *));
    for (int i = 0; i < vertex_num; i++)
        graph[i] = (int *)calloc(vertex_num, sizeof(int));

    for (int i = 0; i < edge_num; i++)
    {
        scanf("%d %d %d", &edge_start, &edge_end, &edge_weight);

        if (edge_weight < 0 || edge_weight > INT_MAX)
        {
            puts("bad length");
            return 0;
        }

        if (edge_start < 1 || edge_start > vertex_num ||
        edge_end < 1 || edge_end > vertex_num)
        {
            puts("bad vertex");
            return 0;
        }

        graph[edge_start - 1][edge_end - 1] = edge_weight;
        graph[edge_end - 1][edge_start - 1] = edge_weight;

        string_cnt++;
    }

    if (string_cnt < edge_num)
    {
        puts("bad number of lines");
        return 0;
    }
    prim(graph, edge_num);

    for (int i  = 0; i < edge_num; i++)
        free(graph[i]);
    free(graph);

    return 0;
}
