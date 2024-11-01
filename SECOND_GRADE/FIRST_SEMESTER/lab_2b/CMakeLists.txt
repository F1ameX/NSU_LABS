cmake_minimum_required(VERSION 3.28)
project(lab_2b)

set(CMAKE_CXX_STANDARD 20)

add_executable(lab_2b main.cpp
               game.cpp game.h
               file_manager.cpp file_manager.h
               console_parser.cpp console_parser.h
               cell.cpp cell.h)
target_link_libraries(lab_2b)