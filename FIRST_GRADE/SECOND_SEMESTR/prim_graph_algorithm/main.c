#include <limits.h>
#include <stdio.h>
#include <stdlib.h>

#define VERTEX_MAX 5000
#define EDGE_MAX ((vertex_num * (vertex_num + 1)) / 2)
#define SHORTEST_VALUE min(vertex_num, edge_num)


typedef struct Edge{
    int start;
    int end;
    int weight;
}Edge;


int check_span(long long int** graph, int edge_num, int vertex_num)
{
    if (vertex_num - edge_num == 1)
    {
        for (int i = 0; i < edge_num + 1; i++)
            for (int j = i + 1; j < edge_num + 1; j++)
                if (graph[i][j] != 0)
                    printf("%d %d\n", i + 1, j + 1);
        return 1;
    }
    return -1;
}


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

    if (vertex_num == 1)
        return -1;

    return 0;
}


int min(int num_1, int num_2)
{
    if (num_1 < num_2)
        return num_1;
    return num_2;
}


long long int min_key(int edge_num, int included[], long long int min_edge[])
{
    int min_index;
    long long int min_weight = LONG_LONG_MAX;

    for (int i = 0; i < edge_num; i++)
    {
        if (included[i] == 0 && min_edge[i] < min_weight)
        {
            min_weight = min_edge[i];
            min_index = i;
        }
    }
    return min_index;
}


void prim(long long int** graph, int edge_num, int vertex_num)
{
    int included[edge_num];
    long long int len = 0, min_idx, min_edge[edge_num], parent[edge_num];

    for (int i = 0; i < edge_num; i++)
    {
        min_edge[i] = UINT_MAX;
        included[i] = 0;
    }

    min_edge[0] = 0;
    parent[0] = -1;

    for (int i = 0; i < SHORTEST_VALUE; i++)
    {
        min_idx = min_key(edge_num, included, min_edge);
        included[min_idx] = 1;
        for (int j = 1; j < SHORTEST_VALUE + 1; j++)
        {
            if (graph[min_idx][j] && included[j] == 0 && graph[min_idx][j] <= min_edge[j])
            {
                parent[j] = min_idx;
                min_edge[j] = graph[min_idx][j];
            }
        }
    }

    for (int i = 1; i < SHORTEST_VALUE; i++)
        len += graph[i][parent[i]];

    if (len == 0)
        puts("no spanning tree");
    else
    {
        for (int i = 1; i < vertex_num; i++)
            if (parent[i] + 1 < i + 1)
                printf("%lld %d\n", parent[i] + 1, i + 1);
            else
                printf("%d %lld\n", i + 1, parent[i] + 1);
    }
}


int main()
{
    FILE* file = fopen("in.txt", "r");
    int cnt = 0, edge_end, edge_num, edge_start, vertex_num;
    long long int edge_weight;
    fscanf(file, "%d", &vertex_num);
    fscanf(file, "%d", &edge_num);

    if (error_check(vertex_num, edge_num) == -1)
        return 0;

    long long int** graph = (long long int**)malloc(vertex_num * sizeof(long long int*));

    for (int i = 0; i < vertex_num; i++)
        graph[i] = (long long int*)calloc(vertex_num, sizeof(long long int));

    for (int i = 0; i < edge_num; i++)
    {
        if (fscanf(file, "%d %d %lld", &edge_start, &edge_end, &edge_weight) != 3)
        {
            fclose(file);
            puts("bad number of lines");
            return 0;
        }

        else if (edge_weight < 0 || edge_weight > INT_MAX)
        {
            fclose(file);
            puts("bad length");
            return 0;
        }

        else if (edge_start < 1 || edge_start > vertex_num ||
                 edge_end < 1 || edge_end > vertex_num)
        {
            fclose(file);
            puts("bad vertex");
            return 0;
        }

        if (edge_end == vertex_num || edge_start == vertex_num)
            cnt++;

        graph[edge_start - 1][edge_end - 1] = edge_weight;
        graph[edge_end - 1][edge_start - 1] = edge_weight;
    }

    if (cnt == 0)
    {
        puts("no spanning tree");
        return 0;
    }

    if (check_span(graph, edge_num, vertex_num) == 1)
        return 0;

    prim(graph, edge_num, vertex_num);

    for (int i = 0; i < vertex_num; i++)
        free(graph[i]);
    free(graph);

    fclose(file);
    return 0;
}
