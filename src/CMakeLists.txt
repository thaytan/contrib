find_package(PkgConfig REQUIRED)
pkg_check_modules(GSTREAMER REQUIRED gstreamer-1.0)
pkg_check_modules(GSTREAMER_PLUGINS_BASE REQUIRED gstreamer-plugins-base-1.0)

set(HEADERS gst-colorizer.h)

add_library(gst-colorizer SHARED gst-colorizer.c)
target_link_libraries(gst-colorizer ${GSTREAMER_LDFLAGS} ${GSTREAMER_PLUGINS_BASE_LDFLAGS})
include_directories(gst-colorizer ${GSTREAMER_INCLUDE_DIRS} ${GSTREAMER_PLUGINS_BASE_INCLUDE_DIRS})

set(DEST_DIR "${CMAKE_INSTALL_PREFIX}")
set(GIT_PKG_VERSION "$ENV{GIT_PKG_VER}")
configure_file("gst-colorizer.pc.in" "gst-colorizer.pc" @ONLY)

install(TARGETS gst-colorizer
        LIBRARY DESTINATION lib/gstreamer-1.0
        ARCHIVE DESTINATION lib/gstreamer-1.0
        RUNTIME DESTINATION bin)
install(FILES ${HEADERS} DESTINATION include/gstreamer-1.0/colorizer)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/gst-colorizer.pc" DESTINATION lib/pkgconfig)
