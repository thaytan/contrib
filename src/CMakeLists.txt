set(HEADERS color-meta.h)

add_library(depth-meta SHARED color-meta.c)
target_link_libraries(depth-meta CONAN_PKG::gstreamer CONAN_PKG::gstreamer CONAN_PKG::gstreamer-plugins-base)

set(DEST_DIR "${CMAKE_INSTALL_PREFIX}")
configure_file("depth-meta.pc.in" "depth-meta.pc" @ONLY)

install(TARGETS depth-meta
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib
        RUNTIME DESTINATION bin)
install(FILES ${HEADERS} DESTINATION include)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/depth-meta.pc" DESTINATION lib/pkgconfig)
