#define UNTITLED_GRAPH_H

#include <stdlib.h>
#pragma once


typedef struct Node
{
    int vertex;
    long int weight;
    struct Node* next;
}Node;


typedef struct Graph
{
    int vertex;
    struct Node** adjacency_list;
}Graph;


typedef struct Visited
{
    int ancestor;
    int passed;
    long int distance;
}Visited;


Graph* create_graph(int vertex)
{
    Graph* graph = (Graph*)malloc(sizeof(Graph));
    graph->vertex = vertex;
    graph->adjacency_list = (Node**)malloc(vertex * sizeof(Node*));

    for (int i = 0; i < vertex; i++)
        graph->adjacency_list[i] = NULL;

    return graph;
}


Node* create_node(int vertex, long int weight)
{
    Node* node = (Node*)malloc(sizeof(Node));
    node->vertex = vertex;
    node->weight = weight;
    node->next = NULL;
    return node;
}


void add_edge(Graph* graph, int start, int end, long int weight)
{
    Node* node = create_node(end, weight);
    node->next = graph->adjacency_list[start - 1];
    graph->adjacency_list[start - 1] = node;
    node = create_node(start, weight);
    node->next = graph->adjacency_list[end -  1];
    graph->adjacency_list[end - 1] = node;
}