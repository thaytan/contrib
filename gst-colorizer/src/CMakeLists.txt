find_package(PkgConfig REQUIRED)
pkg_check_modules(GSTREAMER REQUIRED gstreamer-1.0)
pkg_check_modules(GSTREAMER_PLUGINS_BASE REQUIRED gstreamer-plugins-base-1.0)
pkg_check_modules(GSTREAMER_VIDEO REQUIRED gstreamer-video-1.0)

set(HEADERS gst-colorizer.h)

add_library(colorizer SHARED gst-colorizer.c)
target_link_libraries(colorizer ${GSTREAMER_LDFLAGS} ${GSTREAMER_PLUGINS_BASE_LDFLAGS} ${GSTREAMER_VIDEO_LDFLAGS})
include_directories(colorizer ${GSTREAMER_INCLUDE_DIRS} ${GSTREAMER_PLUGINS_BASE_INCLUDE_DIRS} ${GSTREAMER_VIDEO_INCLUDE_DIRS})

install(TARGETS colorizer
        LIBRARY DESTINATION lib/gstreamer-1.0
        ARCHIVE DESTINATION lib/gstreamer-1.0
        RUNTIME DESTINATION bin)
install(FILES ${HEADERS} DESTINATION include/gstreamer-1.0/colorizer)
