#pragma once

#include <stdlib.h>


typedef struct Node{
    int node_num;
    int** adjacency_list;
}Node;


typedef struct Edge{
    int start;
    int end;
    int weight;
}Edge;


