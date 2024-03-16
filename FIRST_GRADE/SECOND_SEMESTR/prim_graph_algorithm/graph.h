#pragma once

#include <stdlib.h>


typedef struct Edge{
    int start;
    int end;
    int weight;
    int passed;
}Edge;


typedef struct Graph{
    int vertex_num;
    int passed;
    Edge** adjacency_list;
}Graph;
