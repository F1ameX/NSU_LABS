cmake_minimum_required(VERSION 3.28)
project(lab_1a)

set(CMAKE_CXX_STANDARD 20)

find_package(GTest REQUIRED)

add_executable(lab_1a main.cpp bit_array.cpp)
add_executable(my_tests bit_array_test.cpp bit_array.cpp)

target_link_libraries(my_tests GTest::GTest GTest::Main pthread)
target_link_libraries(lab_1a)
