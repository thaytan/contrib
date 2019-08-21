# gst-realsense

GStreamer plugin containing `video/rgbd` source for a RealSense device.

## `video/rgbd`
The `video/rgbd` caps always contain the following fields
- **streams** - This field contains selected streams with priority `depth > infra1 > infra2 > color`. The first stream in this comma separated string, e.g. "depth,infra2,color", is considered to be the main stream and is therefore transported in the main buffer. There must always be at least one stream enabled. All additional buffers are attached as meta to the main buffer.
- **%s_format** - Format for each selected stream, e.g. depth_format="Gray16Le".
- **%s_width** - Width for each selected stream, e.g. depth_width=1280.
- **%s_height** - Height for each selected stream, e.g. depth_height=720.
- **framerate** - Common framerate for all selected streams.

## Building
Execute the following commands.
```
cd gst-realsense
conan install -if build . aivero/stable
source build/env.sh 
cargo build --release
export GST_PLUGIN_PATH=`pwd`/target/release:${GST_PLUGIN_PATH}
```
> Note: `conan install -if build . aivero/stable` might require you to build extra packages. Just follow the instructions in the error message. 

Now you should see the plugin's element `realsensesrc`.
```
gst-inspect-1.0 realsensesrc
```

## Running in combination with [`depthdemux`](https://gitlab.com/aivero/streaming/gst-depth-demux)

Source and export `GST_PLUGIN_PATH` in a single terminal for both `realsensesrc` and `depthdemux` (if not done before).
```
source gst-realsense/build/env.sh --extend
export GST_PLUGIN_PATH=gst-realsense/target/release:${GST_PLUGIN_PATH}

source gst-depth-demux/build/env.sh --extend
export GST_PLUGIN_PATH=gst-depth-demux/target/release:${GST_PLUGIN_PATH}
```

An example of a pipeline:

```
gst-launch-1.0 \
realsensesrc serial=XXXXXXXXXXXX json_location=configuration.json enable_depth=true enable_infra1=false enable_infra2=true enable_color=true depth_width=1280 depth_height=720 color_width=848 color_height=480 framerate=30 ! \
depthdemux name=realsense_demux \
realsense_demux.src_depth ! queue ! glimagesink  \
realsense_demux.src_infra2 ! queue ! glimagesink \
realsense_demux.src_color ! queue ! glimagesink 
```

## Troubleshooting

- *The `realsensesrc` does not play the entire rosbag file.* -> Make sure that all streams contained in the given rosbag file are enabled by setting the properties **enable_%s** to **true**.
- *The `realsensesrc` panic while plaing from a rosbag file.* -> Make sure that only the streams contained in the given rosbag file are enabled by setting the properties **enable_%s** to **true** and the rest to **false**.