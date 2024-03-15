cmake_minimum_required(VERSION 3.26)
project(prim_graph_algorithm C)

set(CMAKE_C_STANDARD 23)

add_executable(prim_graph_algorithm main.c
        graph.h)
