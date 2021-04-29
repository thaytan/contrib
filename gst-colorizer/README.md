# gst-colorizer

GStreamer plugin containing a colorizer, which converts 16-bit depth video into RGB.

# Getting started

## Setup

First you need to install and setup conan, as we use that to handle our dependencies. Before you start, please make sure
that your default python version is 3.X and that pip installs packages for python 3. Then run:

```bash
pip install conan --user
# You may need to source ~/.profile here, please see https://docs.conan.io/en/latest/installation.html#known-installation-issues-with-pip
conan config install https://github.com/aivero/conan-config.git
# And to ensure that the remote is configured properly:
conan search -r aivero gst-colorizer
# You should now see a list of all the releases of gst-colorizer
```

## Install a tagged release

You may use conan to install a pre-built release of the gst-realsense package:

```bash
conan install gst-colorizer/0.1.1@aivero/stable -if installation
export GST_PLUGIN_PATH=$GST_PLUGIN_PATH:$PWD/installation
# And validate that the colorizer is properly installed
gst-inspect-1.0 colorizer
```

## Build your own

If you have made changes to the `colorizer` that you wish to try, you may want to build the project locally:

```
cd gst-colorizer
conan install -if build . aivero/stable
source build/env.sh
cargo build --release
export GST_PLUGIN_PATH=$GST_PLUGIN_PATH:$PWD/target/release
```

> Note: `conan install -if build . aivero/stable` might require you to build extra packages. Just follow the instructions in the error message. 

Now you should see the plugin's element `colorizer`.

```
gst-inspect-1.0 colorizer
```

## Running in combination with [`rgbddemux`](https://gitlab.com/aivero/public/gstreamer/gst-rgbd) and [`realsensesrc`](https://gitlab.com/aivero/public/gstreamer/gst-realsense)

Source and export `GST_PLUGIN_PATH` in a single terminal for both `realsensesrc`, `rgbddemux` and `colorizer` (if not done before).
```
source gst-realsense/build/env.sh --extend
export GST_PLUGIN_PATH=gst-realsense/target/release:${GST_PLUGIN_PATH}

source gst-rgbd/build/env.sh --extend
export GST_PLUGIN_PATH=gst-rgbd/target/release:${GST_PLUGIN_PATH}

source gst-colorizer/build/env.sh --extend
export GST_PLUGIN_PATH=gst-colorizer/target/release:${GST_PLUGIN_PATH}
```

An example of a pipeline:

```bash
# Please replace XXXXXXXX with the serial on your RealSense camera
export RS_SERIAL=XXXXXXXX
gst-launch-1.0 \
realsensesrc serial=$RS_SERIAL enable-depth=true ! \
rgbddemux name=realsense_demux \
realsense_demux.src_depth ! queue ! colorizer near-cut=300 far-cut=3000 ! glimagesink 
```

# Contributing

Please see [the contribution guidelines](CONTRIBUTING.md) for instructions on how to contribute.

# License

This project is licensed under the [GNU Lesser General Public License, version 2.1](LICENSE). Copyright 2019 Aivero.
