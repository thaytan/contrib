find_package(PkgConfig REQUIRED)
pkg_check_modules(GSTREAMER REQUIRED gstreamer-1.0)
pkg_check_modules(GSTREAMER_PLUGINS_BASE REQUIRED gstreamer-plugins-base-1.0)

set(HEADERS buffer-meta.h tags-meta.h frame-meta.h)

add_library(depth-meta SHARED buffer-meta.c tags-meta.c frame-meta.c)
target_link_libraries(depth-meta ${GSTREAMER_LDFLAGS} ${GSTREAMER_PLUGINS_BASE_LDFLAGS})
include_directories(depth-meta ${GSTREAMER_INCLUDE_DIRS} ${GSTREAMER_PLUGINS_BASE_INCLUDE_DIRS})

set(DEST_DIR "${CMAKE_INSTALL_PREFIX}")
set(GIT_PKG_VERSION "$ENV{GIT_PKG_VER}")
configure_file("depth-meta.pc.in" "depth-meta.pc" @ONLY)

install(TARGETS depth-meta
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib
        RUNTIME DESTINATION bin)
install(FILES ${HEADERS} DESTINATION include)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/depth-meta.pc" DESTINATION lib/pkgconfig)
