cmake_minimum_required(VERSION 3.26)
project(avl_tree C)

set(CMAKE_C_STANDARD 17)

add_executable(avl_tree main.c
        avl_tree.h)
