cmake_minimum_required(VERSION 3.28)
project(lab_0a)

set(CMAKE_CXX_STANDARD 17)

add_executable(lab_0a main.cpp
        module1.h
        module2.h
        module1.cpp
        module2.cpp
        module3.h
        module3.cpp)
