# gst-rgbd

GStreamer plugin for demuxing and muxing `video/rgbd` streams using `rgbddemux` and `rgbdmux` respectively.

## `rgbddemux`

GStreamer element for demuxing a single `video/rgbd` stream that creates a `src_%s` pad with `video/x-raw` caps for each detected stream.

## `rgbdmux`

GStreamer element for muxing multiple `video/x-raw` on its `sink_%s` sink pads into a single `video/rgbd`.

## `video/rgbd`
The `video/rgbd` caps always contain the following fields
- **streams** - This field contains selected streams. The first stream in this comma separated string, e.g. "depth,color", is considered to be the main stream and must therefore be located in the main buffer. There must always be at least one stream enabled. All additional buffers are attached as meta to the main buffer.
- **%s_format** - Format for each selected stream, e.g. depth_format="Gray16Le".
- **%s_width** - Width for each selected stream, e.g. depth_width=1280.
- **%s_height** - Height for each selected stream, e.g. depth_height=720.
- **framerate** - Common framerate for all selected streams.


## Building
Execute the following commands.
```bash
cd gst-rgbd
conan install -if build . aivero/stable
source build/env.sh 
cargo build --release
export GST_PLUGIN_PATH=`pwd`/target/release:${GST_PLUGIN_PATH}
```

Now you should see the plugin's elements `rgbddemux` and `rgbdmux`.
```
gst-inspect-1.0 rgbddemux
gst-inspect-1.0 rgbdmux
```

Or alternatively:
```bash
conan create . aivero/stable
```

And add the requirement in another `conanfile.py`:
```python
def requirements(self):
    self.requires("gst-rgbd/*YOUR_BRANCH*@%s/stable" % self.user)
```

Where `*YOUR_BRANCH*` could be e.g. `master`.


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

## Example of a pipeline with `rgbdmux`
**Sending:**
```
gst-launch-1.0 \
realsensesrc serial=${SERIAL} enable_depth=true enable_color=true enable_infra1=true enable_infra2=true ! \
dddqencbin video_encoder=vaapih264enc video_encoder_parse=h264parse mpegtsmux_properties="pat-interval:=9000000;pmt-interval:=9000;si-interval:=9000" ! \
rtpmp2tpay ! rtpbin autoremove=true drop-on-latency=false ! \
udpsink host=127.0.0.1 port=9000
```

**Receiving:**

This pipeline is taken from the `receiver-cli`. It is very nice for debugging all element in one go. 
You can run the pipeline with `GST_DEBUG=3` and optionally `GST_DEBUG="3,dddqdec:6"` (or any other element).

```
tsdemux name=demuxer identity name=enc_id_map identity name=enc_layer_data \
identity name=enc_infra1 identity name=dec_id_map identity name=dec_layer_data identity name=dec_infra1 \
rgbddemux name=decoded_demux rgbdmux name=decoded_mux \
dddqdec name=adc bit-depth=8 number-of-layers=6 near-cut=300 far-cut=700 idmap-correction=1 decoding-strategy=saurus \
identity name=decoded_but_muxed \
rtpbin name=rtpbin udpsrc name=udpsrc port=9000 caps=application/x-rtp,media=video,payload=33,clock-rate=90000,encoding-name=MP2T ! \
queue max-size-time=100000000 ! rtpbin.recv_rtp_sink_0 rtpbin. ! rtpmp2tdepay name=mpegts_depay ! demuxer.sink \
demuxer.video_0_0000 ! queue ! enc_id_map.sink \
demuxer.video_0_0001 ! queue ! enc_layer_data.sink \
demuxer.video_0_0003 ! queue ! enc_infra1.sink \
enc_id_map.src ! queue ! h264parse ! avdec_h264 ! dec_id_map.sink \
enc_layer_data.src ! queue ! h264parse ! avdec_h264 ! dec_layer_data.sink \
enc_infra1.src ! queue ! h264parse ! avdec_h264 ! dec_infra1.sink \
dec_id_map.src ! queue ! videoconvert name=one ! video/x-raw,format=GRAY8 ! decoded_mux.sink_depth \
dec_layer_data.src ! queue ! videoconvert name=two ! video/x-raw,format=RGB ! decoded_mux.sink_layer \
dec_infra1.src ! queue ! videoconvert name=three ! video/x-raw,format=RGB ! decoded_mux.sink_infra1 \
decoded_mux.src ! video/rgbd,streams=\"layer,idmap,infra1\",framerate=30/1,idmap_format=GRAY8,idmap_width=1280,idmap_height=720,layer_format=RGB,layer_width=2560,layer_height=720,infra1_format=RGB,infra1_width=1280,infra1_height=720 ! adc.sink adc.src ! decoded_but_muxed.sink \
decoded_but_muxed.src ! decoded_demux.sink \
decoded_demux.src_depth ! queue name=queue_decoded_demux_src_depth ! colorizer preset=1 near-cut=300 far-cut=700 ! glimagesink \
decoded_demux.src_infra1 ! queue name=queue_decoded_demux_src_infra1 ! glimagesink 
```

