cmake_minimum_required(VERSION 3.5.0)

project(gst-colorizer LANGUAGES C)

set(CMAKE_CXX_STANDARD 14)
if (NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Debug)
endif()

set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS}")

add_subdirectory(src)
