# gst-realsense

GStreamer element providing librealsense2 capabilities

> Note: If you want to play from rosbag file, make sure that you enable all streams this file contains. Otherwise, it usually does not play the entire file if contained streams are disabled. And it usually panics at unwrap() if there are streams enabled that the file does not contain.

> Note: Only infra1 stream is currently supported

> Note: All streams, i.e. depth, color and infra, must share the same framerate in the current implementation

## Building

This is how I build it on my local system.

```
cd gst-realsense
conan install -if build . aivero/stable
source build/activate.sh && source build/activate_run.sh 
cargo build --release
export GST_PLUGIN_PATH=`pwd`/target/release:${GST_PLUGIN_PATH}
```
> Note: `conan install -if build . aivero/stable` might require you to build extra packages. Just follow the instructions in the error message. 

Now you should see the plugin `realsense` as well as its element `realsensesrc` by running the following.
```
gst-inspect-1.0 realsense
gst-inspect-1.0 realsensesrc
```

## Running

Source and export `GST_PLUGIN_PATH` in a single terminal (if not done before).
```
cd gst-realsense
source build/activate.sh && source build/activate_run.sh 
export GST_PLUGIN_PATH=`pwd`/target/release:${GST_PLUGIN_PATH}
```

Build any of the plugins if you made any changes. And test the pipeline with `gst-launch`, using either rosbag or a connected camera.

```
gst-launch-1.0 realsensesrc serial=728312070031 ! glimagesink
```

You can also change the properties, see `gst-inspect-1.0 realsensesrc`, as such:
```
gst-launch-1.0 realsensesrc location=/ABSOLUTE_PATH/20190322_123122.bag framerate=6 depth_width=848 depth_height=480 enable_infra1=true enable_infra2=false enable_color=true color_width=320 color_height=180 ! glimagesink
```