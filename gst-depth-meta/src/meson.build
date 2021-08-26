pkg = import('pkgconfig')

gst_req = '>= 1.14.0'
depends = []

deps = [
  # name, subproject name, subproject dep, library object
  ['gstreamer-1.0', 'gstreamer', 'gst_dep', 'libgst'],
  ['gstreamer-base-1.0', 'gstreamer', 'gst_base_dep', 'gst_base'],
  ['gstreamer-video-1.0', 'gst-plugins-base', 'video_dep', 'gstvideo'],

]

foreach d: deps
  depends += dependency(d[0], version : gst_req,
    fallback : [d[1], d[2]])
endforeach


headers = ['buffer-meta.h', 'tags-meta.h']
depth_meta_lib = shared_library('depth-meta', 'buffer-meta.c', 'tags-meta.c', dependencies: depends, install:true)
# - done - target_link_libraries(['depth-meta', gstreamer_ldflags, gstreamer_plugins_base_ldflags])
# - done - include_directories(['depth-meta', gstreamer_include_dirs, gstreamer_plugins_base_include_dirs])
# dest_dir = '${CMAKE_INSTALL_PREFIX}'
# git_pkg_version = '$ENV{CONAN_BRANCH}'

pkg.generate(depth_meta_lib, version:'8.0.0')

# configure_file(['depth-meta.pc.in', 'depth-meta.pc', '@ONLY'])
# install(['TARGETS', 'depth-meta', 'LIBRARY', 'DESTINATION', 'lib', 'ARCHIVE', 'DESTINATION', 'lib', 'RUNTIME', 'DESTINATION', 'bin'])
# install(['FILES', headers, 'DESTINATION', 'include'])
# install(['FILES', '${CMAKE_CURRENT_BINARY_DIR}/depth-meta.pc', 'DESTINATION', 'lib/pkgconfig'])
