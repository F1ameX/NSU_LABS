#include <limits.h>
#include <stdio.h>
#include <stdlib.h>

#define VERTEX_MAX 5000
#define EDGE_MAX ((vertex_num * (vertex_num + 1)) / 2)
#define SHORTEST_VALUE min(vertex_num, edge_num)


typedef struct Edge {
    int start;
    int end;
    long long weight;
} Edge;


int compare_edges(const void* a, const void* b)
{
    return ((Edge *) a)->weight - ((Edge *) b)->weight;
}


int error_check(int vertex_num, int edge_num)
{
    if (vertex_num < 0 || vertex_num > 5000)
    {
        puts("bad number of vertices");
        return -1;
    }

    if (edge_num < 0 || edge_num > ((vertex_num * (vertex_num + 1)) / 2))
    {
        puts("bad number of edges");
        return -1;
    }

    if (vertex_num == 1)
        return -1;

    return 0;
}


int find_parent(int vertex, int parent[])
{
    if (parent[vertex] == -1)
        return vertex;
    return find_parent(parent[vertex], parent);
}


void kruskal(Edge* edges, int edge_num, int vertex_num)
{
    int idx = 0, included_edges = 0,
    *parent = (int*)malloc(vertex_num * sizeof(int));

    for (int i = 0; i < vertex_num; ++i)
        parent[i] = -1;

    Edge* result = (Edge*)malloc((vertex_num - 1) * sizeof(Edge));
    qsort(edges, edge_num, sizeof(Edge), compare_edges);

    while (included_edges < vertex_num - 1 && idx < edge_num)
    {
        Edge current_edge = edges[idx++];
        int start_parent = find_parent(current_edge.start, parent),
        end_parent = find_parent(current_edge.end, parent);

        if (start_parent != end_parent)
        {
            result[included_edges++] = current_edge;
            parent[start_parent] = end_parent;
        }
    }

    if (included_edges < vertex_num - 1)
        puts("no spanning tree");
    else
    {
        for (int i = 0; i < vertex_num - 1; i++)
        {
            if (result[i].start < result[i].end)
                printf("%d %d\n", result[i].start + 1, result[i].end + 1);
            else
                printf("%d %d\n", result[i].end + 1, result[i].start + 1);
        }
    }
    free(parent);
    free(result);
}


int main()
{
    FILE* file = fopen("in.txt", "r");
    int cnt = 0, edge_num, vertex_num;

    fscanf(file, "%d %d", &vertex_num, &edge_num);

    if (error_check(vertex_num, edge_num) == -1)
        return 0;

    Edge* edges = (Edge*)malloc(edge_num * sizeof(Edge));

    for (int i = 0; i < edge_num; i++)
    {
        if (fscanf(file, "%d %d %lld", &edges[i].start, &edges[i].end, &edges[i].weight) != 3)
        {
            fclose(file);
            puts("bad number of lines");
            return 0;
        }

        if (edges[i].weight < 0 || edges[i].weight > INT_MAX)
        {
            puts("bad length");
            return 0;
        }

        if (edges[i].start < 1 || edges[i].start > vertex_num ||
            edges[i].end< 1 || edges[i].end > vertex_num)
        {
            puts("bad vertex");
            return 0;
        }

        if (edges[i].end == vertex_num || edges[i].start == vertex_num)
            cnt++;

        edges[i].start--;
        edges[i].end--;
    }

    if (cnt == 0)
    {
        puts("no spanning tree");
        return 0;
    }
    kruskal(edges, edge_num, vertex_num);
    free(edges);
    fclose(file);
    return 0;
}