cmake_minimum_required(VERSION 3.10)

project(CSVParser)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

set(SRC_FILES csv_parser.h tuple_printer.h main.cpp
        parser_config.h
        CSV_exceptions.h
        CSV_parser.cpp)

add_executable(lab_4 ${SRC_FILES})
enable_testing()

find_package(GTest REQUIRED)
include_directories(${GTEST_INCLUDE_DIRS})

set(TEST_FILES csv_parser.h tuple_printer.h tests.cpp
        parser_config.h
        CSV_parser.cpp)

add_executable(tests ${TEST_FILES})

target_link_libraries(tests GTest::GTest GTest::Main)

add_test(NAME CSVParserTest COMMAND tests)