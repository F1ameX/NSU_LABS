cmake_minimum_required(VERSION 3.28)
project(lab_1a)

set(CMAKE_CXX_STANDARD 26)

add_executable(lab_1a main.cpp
        bit_array.cpp
        bit_array.h
        bit_array_test.cpp
        bit_array_test.cpp)

find_package(GTest REQUIRED)
target_link(bit_array_tests GTest::gtest_main)

enable_testing()
add_test(NAME BitArrayTests COMMAND bit_array_tests)
