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
gst_depth_meta_lib = shared_library('depth-meta', 'buffer-meta.c', 'tags-meta.c', dependencies: depends, install:true)
gst_depth_meta_dep = declare_dependency(link_with: gst_depth_meta_lib)

pkg.generate(gst_depth_meta_lib, version:'8.0.0')
