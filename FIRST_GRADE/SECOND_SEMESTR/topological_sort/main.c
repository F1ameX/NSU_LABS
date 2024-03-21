#include <stdio.h>
#include <stdlib.h>

#define VERTEX_MAX 2000
#define EDGE_MAX ((vertex_num * (vertex_num + 1)) / 2)


typedef struct Graph {
    int vertex_num;
    int* adjacency_list;
    int* indegree;
} Graph;


int error_check(int edge_num, int vertex_num) {

    if (vertex_num < 0 || vertex_num > VERTEX_MAX) {
        puts("bad number of vertices");
        return -1;
    }

    if (edge_num < 0 || edge_num > EDGE_MAX) {
        puts("bad number of edges");
        return -1;
    }

    return 0;
}


int topological_sort(Graph* graph, int* result, int vertex_num) {
    int* indegree = graph->indegree;
    int* adjacency_list = graph->adjacency_list;
    int result_index = 0;
    int* queue = (int*)malloc(vertex_num * sizeof(int));
    int front = 0, rear = -1;

    for (int i = 0; i < vertex_num; i++) {
        if (indegree[i] == 0)
            queue[++rear] = i;
    }

    while (front <= rear) {
        int node = queue[front++];

        result[result_index++] = node;

        for (int i = 0; i < vertex_num; i++) {
            if (adjacency_list[node * vertex_num + i] == 1) {
                indegree[i]--;

                if (indegree[i] == 0)
                    queue[++rear] = i;
            }
        }
    }

    free(queue);

    if (result_index != vertex_num) {
        return -1;
    }

    return 0;
}

int main() {
    int edge_end, edge_num, edge_start, vertex_num;
    FILE* input_file = fopen("/Users/andrewf1amex/Documents/Lab tests/in.txt", "r");

    fscanf(input_file, "%d", &vertex_num);
    fscanf(input_file, "%d", &edge_num);

    if (error_check(edge_num, vertex_num) == -1)
        return 0;

    Graph graph;
    graph.vertex_num = vertex_num;
    graph.adjacency_list = (int*)calloc(vertex_num * vertex_num, sizeof(int));
    graph.indegree = (int*)calloc(vertex_num, sizeof(int));


    for (int i = 0; i < edge_num; i++) {

        if (fscanf(input_file, "%d %d", &edge_start, &edge_end) != 2) {
            fclose(input_file);
            puts("bad number of lines");
            return 0;
        }
        if (edge_start == edge_end)
        {
            puts("bad number of edges");
            return 0;
        }
        if (edge_start < 1 || edge_start > vertex_num || edge_end < 1 || edge_end > vertex_num) {
            puts("bad vertex");
            return 0;
        }

        graph.adjacency_list[(edge_start - 1) * vertex_num + (edge_end - 1)] = 1;
        graph.indegree[edge_end - 1]++;
    }

    int* result = (int*)malloc(vertex_num * sizeof(int));
    int sort_status = topological_sort(&graph, result, vertex_num);

    if (sort_status == 0) {
        for (int i = 0; i < vertex_num; i++)
            printf("%d ", result[i] + 1);
        printf("\n");
    }
    else
        puts("impossible to sort");

    free(graph.adjacency_list);
    free(graph.indegree);
    free(result);

    fclose(input_file);
    return 0;
}
