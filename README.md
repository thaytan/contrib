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

## Running in combination with `depthdemux`

Source and export `GST_PLUGIN_PATH` in a single terminal (if not done before).
```
cd gst-realsense
source build/env.sh 
export GST_PLUGIN_PATH=`pwd`/target/release:${GST_PLUGIN_PATH}
```

Example of a pipeline in combination with `depthdemux`:

```
TODO
```

## Troubleshooting

- *The `realsensesrc` does not play the entire rosbag file.* -> Make sure that all streams contained in the given rosbag file are enabled by setting the properties **enable_%s** to **true**.
- *The `realsensesrc` panic while plaing from a rosbag file.* -> Make sure that only the streams contained in the given rosbag file are enabled by setting the properties **enable_%s** to **true** and the rest to **false**.