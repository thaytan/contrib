set(HEADERS gstcolorizer.h)

add_library(colorizer SHARED gstcolorizer.c)
target_link_libraries(colorizer CONAN_PKG::gstreamer CONAN_PKG::gstreamer-plugins-base)

set(DEST_DIR "${CMAKE_INSTALL_PREFIX}")
set(GIT_PKG_VERSION "$ENV{GIT_PKG_VER}")
configure_file("gstcolorizer.pc.in" "gstcolorizer.pc" @ONLY)

install(TARGETS colorizer
        LIBRARY DESTINATION lib/gstreamer-1.0
        ARCHIVE DESTINATION lib/gstreamer-1.0
        RUNTIME DESTINATION bin)
install(FILES ${HEADERS} DESTINATION include/gstreamer-1.0/colorizer)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/gstcolorizer.pc" DESTINATION lib/pkgconfig)
