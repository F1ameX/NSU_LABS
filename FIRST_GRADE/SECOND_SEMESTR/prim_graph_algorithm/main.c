#include "graph.h"
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>

#define VERTEX_MAX 5000
#define EDGE_MAX ((vertex_num * (vertex_num + 1)) / 2)


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


int main()
{
    int string_cnt = 0, vertex_num, edge_num, edge_start, edge_end, edge_len;
    scanf("%d", &vertex_num);
    scanf("%d", &edge_num);

    if (error_check(vertex_num, edge_num) == -1)
        return 0;

    for (int i = 0; i < edge_num; i++)
    {
        scanf("%d %d %d", &edge_start, &edge_end, &edge_len);

        if (edge_len < 0 || edge_len > INT_MAX)
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

        string_cnt++;
    }

    if (string_cnt < edge_num)
    {
        puts("bad number of lines");
        return 0;
    }

    return 0;
}
