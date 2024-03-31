cmake_minimum_required(VERSION 3.26)
project(kosoraju_graph_algorithm C)

set(CMAKE_C_STANDARD 23)

add_executable(kosoraju_graph_algorithm main.c
        stack.h
        stack.c
        graph.h
        graph.c)
