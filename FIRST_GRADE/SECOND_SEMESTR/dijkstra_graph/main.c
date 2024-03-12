#include "graph.h"
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>

#define EDGE_LIMIT (vertex * (vertex - 1) / 2)


int min_weight(Node* queue, Visited* visited)
{
    int current_vertex, min_weight = -1;
    long int min_distance = LONG_MAX;
    Node* currentNode = queue;

    if (!queue)
        return -1;

    while (currentNode)
    {
        current_vertex = currentNode->vertex;
        if (!visited[current_vertex].passed && visited[current_vertex].distance <= min_distance)
        {
            min_distance = visited[current_vertex].distance;
            min_weight = current_vertex;
        }
        currentNode = currentNode->next;
    }
    return min_weight;
}



void dijkstra(Graph* graph, int start, int end)
{
    int path_len = 0, min_edge, adjacency_vertex, path[graph->vertex], current;
    int path_checker = 0, overflow_checker = 0;
    long int similar_path;
    Visited* visited = (Visited*)malloc(graph->vertex *sizeof(Visited));
    Node* queue = NULL, *node = (Node*)malloc(sizeof(Node)), *temp;

    for (int i = 0; i < graph->vertex; i++)
    {
        visited[i].distance = LONG_MAX;
        visited[i].passed = 0;
        visited[i].ancestor = -1;
    }
    visited[start - 1].distance = 0;

    node->vertex = start - 1;
    node->weight = 0;
    node->next = NULL;
    queue = node;

    while (queue != NULL)
    {
        min_edge = min_weight(queue, visited);

        if (min_edge == -1)
            break;


        visited[min_edge].passed = 1;
        temp = graph->adjacency_list[min_edge];

        while (temp)
        {
            adjacency_vertex = temp->vertex - 1;
            similar_path = visited[min_edge].distance + temp->weight;

            if (similar_path <= visited[adjacency_vertex].distance)
            {
                visited[adjacency_vertex].distance = similar_path;
                visited[adjacency_vertex].ancestor = min_edge;

                node = (Node*)malloc(sizeof(Node));
                node->vertex = adjacency_vertex;
                node->weight = similar_path;
                node->next = queue;

                queue = node;
            }
            temp = temp->next;
        }
    }

    current = end - 1;

    while (current != -1)
    {
        path[path_len++] = current + 1;
        current = visited[current].ancestor;
    }

    for (int i = 0; i < graph->vertex; i++)
    {
        if (visited[i].distance == LONG_MAX)
            printf("oo ");

        else if (visited[i].distance > INT_MAX)
            printf("INT_MAX+ ");

        else
            printf("%ld ", visited[i].distance - visited[start - 1].distance);
    }
    putchar('\n');



    for (int i = 0; i < path_len; i++)
    {
        if (path[i] == start || path[i] == end)
            path_checker++;
        if (visited[i + 1].distance >= INT_MAX &&
            visited[i + 1].distance != LONG_MAX)
            overflow_checker++;
    }

    if (path_checker != 2 && start != end)
    {
        puts("no path");
        return;
    }

    else if (visited[path_len - 1].distance > INT_MAX && overflow_checker > 2)
    {
        puts("overflow");
        return;
    }

    for (int i = 0; i < path_len; i++)
        printf("%d ", path[i]);

    putchar('\n');
}


int error_check(int vertex, int edge, int start, int end)
{
    if (vertex < 0 || vertex > 5000)
    {
        puts("bad number of vertices");
        return -1;
    }

    if (edge < 0 || edge > EDGE_LIMIT)
    {
        puts("bad number of edges");
        return -1;
    }

    if (start < 1 || start > vertex || end < 1 || end > vertex)
    {
        puts("bad vertex");
        return -1;
    }
    return 0;
}


int main()
{
    int string_cnt = 0, vertex, start, end, edge, edge_start, edge_end;
    long int weight;
    scanf("%d", &vertex);
    scanf("%d %d", &start, &end);
    scanf("%d", &edge);

    if (error_check(vertex, edge, start, end) == -1)
        return 0;

    Graph *graph = create_graph(vertex);

    for (int i = 0; i < edge; i++)
    {
        scanf("%d %d %ld", &edge_start, &edge_end, &weight);

        if (weight < 0 || weight > INT_MAX)
        {
            puts("bad length");
            return 0;
        }
        add_edge(graph, edge_start, edge_end, weight);
        string_cnt++;
    }

    if (string_cnt < edge)
    {
        puts("bad number of lines");
        return 0;
    }

    dijkstra(graph, start, end);
    free(graph);
    return 0;
}