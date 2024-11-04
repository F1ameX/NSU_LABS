cmake_minimum_required(VERSION 3.28)
project(lab_3)

set(CMAKE_CXX_STANDARD 20)


add_executable(lab_3 main.cpp
        tick.h
        input_parser.cpp
        input_parser.h)
