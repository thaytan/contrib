# gst-rgbd

GStreamer plugin for demuxing and muxing `video/rgbd` streams using `rgbddemux` and `rgbdmux` respectively.

## `rgbddemux`

GStreamer element for demuxing a single `video/rgbd` stream that creates a `src_%s` pad with `video/x-raw` caps for each detected stream.

## `rgbdmux`

GStreamer element for muxing multiple `video/x-raw` on its `sink_%s` sink pads into a single `video/rgbd`.

>TODO: As of now, src `video/rgbd` caps of `rgbdmux` are not correct and require re-negotiation each time a new src pad is connected. The `aggregator.negotiate()` function is present in GStreamer v1_18.


## `video/rgbd`
The `video/rgbd` caps always contain the following fields
- **streams** - This field contains selected streams. The first stream in this comma separated string, e.g. "depth,color", is considered to be the main stream and must therefore be located in the main buffer. There must always be at least one stream enabled. All additional buffers are attached as meta to the main buffer.
- **%s_format** - Format for each selected stream, e.g. depth_format="Gray16Le".
- **%s_width** - Width for each selected stream, e.g. depth_width=1280.
- **%s_height** - Height for each selected stream, e.g. depth_height=720.
- **framerate** - Common framerate for all selected streams.


## Building
Execute the following commands.
```
cd gst-rgbd
conan install -if build . aivero/stable
source build/env.sh 
cargo build --release
export GST_PLUGIN_PATH=`pwd`/target/release:${GST_PLUGIN_PATH}
```
>Note: `conan install -if build . aivero/stable` might require you to build extra packages. Just follow the instructions in the error message. 

Now you should see the plugin's elements `rgbddemux` and `rgbdmux`.
```
gst-inspect-1.0 rgbddemux
gst-inspect-1.0 rgbdmux
```

## Running `rgbddemux` in combination with [`realsensesrc`](https://gitlab.com/aivero/public/gstreamer/gst-realsense)

Source and export `GST_PLUGIN_PATH` in a single terminal for both `realsensesrc` and `rgbddemux` (if not done before).
```
source gst-realsense/build/env.sh --extend
export GST_PLUGIN_PATH=gst-realsense/target/release:${GST_PLUGIN_PATH}

source gstrgbdd/build/env.sh --extend
export GST_PLUGIN_PATH=gst-rgbd/target/release:${GST_PLUGIN_PATH}
```

An example of a pipeline:

```
gst-launch-1.0 \
realsensesrc serial=XXXXXXXXXXXX json_location=configuration.json enable_depth=true enable_infra1=false enable_infra2=true enable_color=true depth_width=1280 depth_height=720 color_width=848 color_height=480 framerate=30 ! \
rgbddemux name=realsense_demux \
realsense_demux.src_depth ! queue ! glimagesink  \
realsense_demux.src_infra2 ! queue ! glimagesink \
realsense_demux.src_color ! queue ! glimagesink 
```

## Example of a pipeline with `depthmux`

>TODO: Wait until downstream re-negotiation is fixed

video/rgbd,streams=\"depth,color,infra1,infra2\",framerate=30/1,depth_format=GRAY16_LE,depth_width=1280,depth_height=720,idmap_format=GRAY8,idmap_width=1280,idmap_height=720,layer_format=RGB,layer_width=2560,layer_height=720,color_format=RGB,color_width=1280,color_height=720,infra1_format=GRAY8,infra1_width=1280,infra1_height=720,infra2_format=GRAY8,infra2_width=1280,infra2_height=720