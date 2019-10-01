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
**Sending:**
```
gst-launch-1.0 \
realsensesrc serial=${SERIAL} enable_depth=true enable_color=true enable_infra1=true enable_infra2=true ! \
dddqencbin video_encoder=vaapih264enc video_encoder_parse=h264parse mpegtsmux_properties="pat-interval:=9000000;pmt-interval:=9000;si-interval:=9000" ! \
rtpmp2tpay ! rtpbin autoremove=true drop-on-latency=false ! \
udpsink host=127.0.0.1 port=9000
```
**Receiving:**
```
gst-launch-1.0 tsdemux name=mpegts_demux rgbdmux name=decoded_mux rgbddemux name=decoded_demux \
udpsrc address=127.0.0.1 port=9000 caps="application/x-rtp,media=video,payload=33,clock-rate=90000,encoding-name=MP2T" ! \
queue max-size-time=100000000 ! rtpbin ! rtpmp2tdepay ! \
mpegts_demux.sink \
mpegts_demux.video_0_0000 ! queue ! h264parse ! vaapidecodebin ! videoconvert ! video/x-raw,format=GRAY8 ! decoded_mux.sink_depth \
mpegts_demux.video_0_0001 ! queue ! h264parse ! vaapidecodebin ! videoconvert ! video/x-raw,format=RGB ! decoded_mux.sink_layer \
mpegts_demux.video_0_0002 ! queue ! h264parse ! vaapidecodebin ! videoconvert ! video/x-raw,format=RGB ! decoded_mux.sink_color \
mpegts_demux.video_0_0003 ! queue ! h264parse ! vaapidecodebin ! videoconvert ! video/x-raw,format=GRAY8 ! decoded_mux.sink_infra1 \
mpegts_demux.video_0_0004 ! queue ! h264parse ! vaapidecodebin ! videoconvert ! video/x-raw,format=GRAY8 ! decoded_mux.sink_infra2 \
decoded_mux.src ! dddqdec ! \
decoded_demux.sink \
decoded_demux.src_depth ! queue ! glimagesink \
decoded_demux.src_color ! queue ! glimagesink \
decoded_demux.src_infra1 ! queue ! glimagesink \
decoded_demux.src_infra2 ! queue ! glimagesink
```