cmake_minimum_required(VERSION 3.28)
project(lab_4)

set(CMAKE_CXX_STANDARD 20)

add_executable(lab_4 main.cpp
        tuple_printer.h
        CSV_parser.cpp
        CSV_parser.h)
