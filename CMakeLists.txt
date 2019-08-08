cmake_minimum_required(VERSION 3.5.0)

project(gst-depth-meta LANGUAGES C)
set(CMAKE_CXX_STANDARD 14)

if (NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Debug)
endif()

execute_process(COMMAND conan install -g=cmake -s build_type=${CMAKE_BUILD_TYPE} -if ${CMAKE_BINARY_DIR} ${CMAKE_SOURCE_DIR})

add_subdirectory(src)
