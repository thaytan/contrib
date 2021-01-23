cmake_minimum_required(VERSION 3.5.0)

project(gst-depth-meta LANGUAGES C)
set(CMAKE_CXX_STANDARD 14)

if (NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Debug)
endif()

add_subdirectory(src)
