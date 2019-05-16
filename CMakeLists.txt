cmake_minimum_required(VERSION 3.5.0)

project(gst-depth-meta LANGUAGES C)
set(CMAKE_CXX_STANDARD 14)

if (NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Debug)
endif()

If(CMAKE_BUILD_TYPE STREQUAL "Release")
    set(CONAN_REFERENCE "aivero/stable")
else()
    set(CONAN_REFERENCE "aivero/testing")
endif()

execute_process(COMMAND conan install -s build_type=${CMAKE_BUILD_TYPE} -if ${CMAKE_BINARY_DIR} -g=cmake ${CMAKE_SOURCE_DIR} ${CONAN_REFERENCE})
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_subdirectory(src)
