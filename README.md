# gst-k4a

GStreamer plugin containing `video/rgbd` source for a Azure Kinect device.

## `video/rgbd`

The `video/rgbd` caps always contain the following fields
- **streams** - This field contains selected streams with priority `depth > infra1 > infra2 > color`. The first stream in this comma separated string, e.g. "depth,infra2,color", is considered to be the main stream and is therefore transported in the main buffer. There must always be at least one stream enabled. All additional buffers are attached as meta to the main buffer.
- **%s_format** - Format for each selected stream, e.g. depth_format="GRAY16_LE".
- **%s_width** - Width for each selected stream, e.g. depth_width=1280.
- **%s_height** - Height for each selected stream, e.g. depth_height=720.
- **framerate** - Common framerate for all selected streams.

# Getting started

## Setup

First you need to install and setup conan, as we use that to handle our dependencies. Before you start, please make sure
that your default python version is 3.X and that pip installs packages for python 3. Then run:

```bash
pip install conan --user
# You may need to source ~/.profile here, please see https://docs.conan.io/en/latest/installation.html#known-installation-issues-with-pip
conan remote add aivero https://conan.aa.aivero.dev/artifactory/api/conan/aivero-public
# And to ensure that the remote is configured properly:
conan search -r aivero gst-k4a
# You should now see a list of all the releases of gst-realsense
```

## Install a tagged release

You may use conan to install a pre-built release of the gst-k4a package:

**NOTE:** This does not work yet, as the `k4asrc` has not yet been released.

```bash
conan install gst-k4a/0.1.0@aivero/stable -if installation
export GST_PLUGIN_PATH=$GST_PLUGIN_PATH:$PWD/installation
# And validate that the realsensesrc is properly installed
gst-inspect-1.0 realsensesrc
```

## Build your own

If you have made changes to the `k4asrc` that you wish to try, you may want to build the project locally:

```
cd gst-k4a
conan install -if build . aivero/stable
source build/env.sh
cargo build --release
export GST_PLUGIN_PATH=$GST_PLUGIN_PATH:$PWD/target/release
```

> Note: `conan install -if build . aivero/stable` might require you to build extra packages. Just follow the instructions in the error message. 

Now you should see the plugin's element `k4asrc`.
```
gst-inspect-1.0 k4asrc
```

## Running in combination with [`rgbddemux`](https://gitlab.com/aivero/public/gstreamer/gst-rgbd)

Source and export `GST_PLUGIN_PATH` in a single terminal for both `realsensesrc` and `rgbddemux` (if not done before).
```
source gst-realsense/build/env.sh --extend
export GST_PLUGIN_PATH=gst-realsense/target/release:${GST_PLUGIN_PATH}

source gst-rgbd/build/env.sh --extend
export GST_PLUGIN_PATH=gst-rgbd/target/release:${GST_PLUGIN_PATH}
```

An example of a pipeline:

```bash
# Please replace XXXXXXXX with the serial on your RealSense camera
gst-launch-1.0 \
k4asrc enable-depth=true enable-color=true ! \
rgbddemux name=realsense_demux \
realsense_demux.src_depth ! queue ! glimagesink  \
realsense_demux.src_infra2 ! queue ! glimagesink \
realsense_demux.src_color ! queue ! glimagesink 
```

# Contributing

Please see [the contribution guidelines](CONTRIBUTING.md) for instructions on how to contribute.

# License

This project is licensed under the [GNU Lesser General Public License, version 2.1](LICENSE). Copyright 2019 Aivero.