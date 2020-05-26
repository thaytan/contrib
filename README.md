# gst-realsense

GStreamer plugin containing `video/rgbd` source for a RealSense device.

> Note: This repo builds and installs **only** the `realsensesrc`. Additionally you require the `rgbddemux` element to display a `video/rgbd` stream. Please head to the [Aivero RGB-D Toolkit](https://gitlab.com/aivero/public/aivero-rgbd-toolkit) to install a complete set of elements for handling RGB-D cameras.


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
that your default python version is 3.X and that pip installs packages for python 3. 
We build on conan with a non-standard profile, which you can keep updated using our [conan config](https://gitlab.com/aivero/public/conan/conan-config).
Then run:


```bash
pip install conan --user
# You may need to source ~/.profile here, please see https://docs.conan.io/en/latest/installation.html#known-installation-issues-with-pip

# Install the conan repositories, as well as conan profiles
conan config install git@gitlab.com:aivero/public/conan/conan-config.git

# Select one of the provided conan profiles as default:
conan config set general.default_profile=linux_x86_64
# conan config set general.default_profile=linux_armv8

# And to ensure that the remote is configured properly:
conan search -r aivero gst-realsense
# You should now see a list of all the releases of gst-realsense
```

## Install a tagged release

You may use conan to install a pre-built release of the gst-k4a package into your hidden `~/.conan/data` directory. This will **NOT** install the required `rgbddemux`. 
	
> Unless you know your ways around conan and GStreamer we **highly recommend** installing the [Aivero RGB-D Toolkit](https://gitlab.com/aivero/public/aivero-rgbd-toolkit) instead! This contains the k4asrc, realsensesrc and all elements to support them.

### Installing to hidden conan directory:
```bash
# List all releases:
conan search -r aivero gst-realsense

# Choose one of the releases and:
conan install gst-realsense/*CHOSEN_RELEASE*@aivero/stable
# Find the .so in ~/.conan/data/k4a/1.4.0/aivero/stable/package/SOME_HASH/lib
```

## Build your own

If you have made changes to the `realsensesrc` that you wish to try, you may want to build the project locally:

```bash
cd gst-realsense
conan install -if build . aivero/stable
source build/env.sh
cargo build --release
export GST_PLUGIN_PATH=$GST_PLUGIN_PATH:$PWD/target/release
```

> Note: `conan install -if build . aivero/stable` might require you to build extra packages. Just follow the instructions in the error message. 

Now you should see the plugin's element `realsensesrc`.

```bash
gst-inspect-1.0 realsensesrc
```

## Use
 
This section details various aspects of using the `realsensesrc`.

### In combination with [`rgbddemux`](https://gitlab.com/aivero/public/gstreamer/gst-rgbd)

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
export RS_SERIAL=XXXXXXXX
gst-launch-1.0 \
realsensesrc serial=$RS_SERIAL enable-depth=true enable-infra2=true enable-color=true ! \
rgbddemux name=realsense_demux \
realsense_demux.src_depth ! queue ! glimagesink  \
realsense_demux.src_infra2 ! queue ! glimagesink \
realsense_demux.src_color ! queue ! glimagesink 
```

### Timestamping

The `realsensesrc` supports a couple of different timestamping modes, those are:

- `default`: The `realsensesrc` uses GStreamer's BaseSink timestamping implementation. This may in some cases mean that the primary `video/rgbd` buffer is timestamped, and in other cases not. None of the meta buffers are timestamped.
- `all-buffers`: This mode timestamps all `video/rgbd` buffers using the pipeline clock.
- `rs2`: Librealsense timestamps are converted into GStreamer timestamps and timestamped on every `video/rgbd` buffer.

There is an interplay between the four properties `serial`, `rosbag-location`, `real-time-rosbag-playback` and `timestamp-mode`
and the pipeline's sink. In some cases this means that there is a right and a wrong timestamping mode for the `realsensesrc`.
Timestamping problems will surface as a frozen pipeline, where only one or a few frames make it through. The table below
lists some combinations that can be used as guidelines:

| source | is-live | timestamp-mode | sink | supported |
|--------|---------|----------------|------|-----------|
| serial | always  | default        | glimagesink | no |
| serial | always  | all-buffers    | glimagesink | yes |
| serial | always  | rs2            | glimagesink | no |
| serial | always  | default        | filesink | yes |
| serial | always  | all-buffers    | filesink | yes |
| serial | always  | rs2            | filesink | yes |
| rosbag | false   | default        | glimagesink | yes (at non-real-time playback speed) |
| rosbag | false   | all-buffers    | glimagesink | yes (at non-real-time playback speed) |
| rosbag | false   | rs2            | glimagesink | yes (looping not supported) |
| rosbag | true    | default        | glimagesink | yes |
| rosbag | true    | all-buffers    | glimagesink | yes |
| rosbag | true    | rs2            | glimagesink | yes (looping not supported) |
| rosbag | false   | default        | filesink | yes |
| rosbag | false   | all-buffers    | filesink | yes |
| rosbag | false   | rs2            | filesink | yes (looping not supported) |
| rosbag | true    | default        | filesink | yes |
| rosbag | true    | all-buffers    | filesink | yes |
| rosbag | true    | rs2            | filesink | yes (looping not supported) |

We encourage you to play around with the settings and notify Aivero via email or issues if there's anything which does
make sense.

# Contributing

Please see [the contribution guidelines](CONTRIBUTING.md) for instructions on how to contribute.

# License

This project is licensed under the [GNU Lesser General Public License, version 2.1](LICENSE). Copyright 2019 Aivero.
