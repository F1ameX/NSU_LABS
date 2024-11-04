cmake_minimum_required(VERSION 3.28)
project(lab_2b)

set(CMAKE_CXX_STANDARD 20)

find_package(GTest REQUIRED)

add_executable(lab_2b main.cpp
        game.cpp game.h
        console_parser.cpp console_parser.h
        cell.cpp cell.h)

add_executable(game_tests game_test.cpp game.cpp game.h
        console_parser.cpp console_parser.h
        cell.cpp cell.h)

target_link_libraries(game_tests GTest::GTest GTest::Main pthread)
target_link_libraries(lab_2b)