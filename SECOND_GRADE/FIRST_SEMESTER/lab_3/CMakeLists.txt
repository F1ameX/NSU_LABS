cmake_minimum_required(VERSION 3.28)
project(lab_3)

set(CMAKE_CXX_STANDARD 20)

enable_testing()
find_package(GTest REQUIRED)
include_directories(${GTEST_INCLUDE_DIRS})

add_executable(lab_3 main.cpp
        tick.h
        input_parser.cpp
        input_parser.h
        WAV_file.cpp
        WAV_file.h
        audio_converters.cpp
        audio_converters.h
        sound_processor.cpp
        sound_processor.h)

add_executable(app_tests app_tests.cpp
       tick.h
       input_parser.cpp
        input_parser.h
        WAV_file.cpp
        WAV_file.h
        audio_converters.cpp
        audio_converters.h
        sound_processor.cpp
        sound_processor.h
       exceptions.h)

target_link_libraries(app_tests GTest::gtest GTest::gtest_main pthread)
target_link_libraries(lab_3 pthread)