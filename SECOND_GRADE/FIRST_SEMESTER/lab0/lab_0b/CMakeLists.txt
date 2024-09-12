cmake_minimum_required(VERSION 3.28)
project(cpp_test)

set(CMAKE_CXX_STANDARD 26)

add_executable(lab_0b main.cpp
        word_data.cpp
        word_data.h
        csv_writer.cpp
        csv_writer.h)
