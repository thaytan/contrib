# gst-k4a

GStreamer plugin containing `video/rgbd` source for Azure Kinect DK (K4A) device.

> Note: Streaming from IMU is currently not implemented

> Note: Streaming from the microphone array is currently not implemented

## `video/rgbd`
The `video/rgbd` caps always contain the following fields
- **streams** - This field contains selected streams with priority `depth > ir > color > imu`. The first stream in this comma separated string, e.g. "depth,ir,color", is considered to be the main stream and is therefore transported in the main buffer. There must always be at least one stream enabled. All additional buffers are attached as meta to the main buffer.
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
# You should now see a list of all the releases of gst-k4a
```

## Install a tagged release

You may use conan to install a pre-built release of the gst-k4a package:

**NOTE:** This does not work yet, as the `k4asrc` has not yet been released.

```bash
conan install gst-k4a/0.3.0@aivero/stable -if installation
export GST_PLUGIN_PATH=$GST_PLUGIN_PATH:$PWD/installation
# And validate that the realsensesrc is properly installed
gst-inspect-1.0 k4asrc
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

Source and export `GST_PLUGIN_PATH` in a single terminal for both `k4asrc` and `rgbddemux` (if not done before).
```
source gst-k4a/build/env.sh --extend
export GST_PLUGIN_PATH=gst-k4a/target/release:${GST_PLUGIN_PATH}

source gst-rgbd/build/env.sh --extend
export GST_PLUGIN_PATH=gst-rgbd/target/release:${GST_PLUGIN_PATH}
```

An example of a pipeline:

```bash
gst-launch-1.0 rgbddemux name=k4a_demux \
k4asrc enable-depth=true enable-ir=true enable-color=true enable-imu=false color-format=nv12 color-resolution=720p depth-mode=nfov_unbinned framerate=15fps ! \
k4a_demux.sink \
k4a_demux.src_depth ! queue ! glimagesink \
k4a_demux.src_ir ! queue ! glimagesink \
k4a_demux.src_color ! queue ! glimagesink
```

## Timestamping

This element provides multiple options for timestamping under `timestamp-mode` property due to the way in which `video/rgbd` CAPS are implemented.
- `ignore`: Do not apply timestamp to any buffer
- `main`: Apply timestamps only to the main buffers based on current stream time (identical to enabling `do-timestamp=true`)
- `all` (default): Apply timestamps to all buffers based on current stream time, i.e. since the element was last put to PLAYING
- `common`: Apply timestamps to all buffers based on the timestamps obtained from physical K4A device or playback. A common timestamp will be applied to all buffers belonging to one capture. Such timestamp is always based on the frame that belongs to the main stream (usually `depth`)
- `individual`: Apply timestamps to all buffers based on the timestamps obtained from physical K4A device or playback. Each buffer receives an individual timestamp based on the K4A timestamps of the corresponding frame. Note that `depth` and `ir` streams of K4A are always synchronised but their timestamps can differ from `color` and `imu` streams

Here are some overall guidelines for their usage:

#### General
- Although not recommended, options `ignore` and `main` can be used with one stream enabled, both when streaming from Device and Playback.

#### Streaming from Device
- Option `all` is the only reliable alternative that works with multiple streams enabled.

#### Streaming from Playback without looping
- Options `common` and `individual` seem to be always reliable and result in real-life like playback (regardless of `real-time-playback`).
- Option `all` provides as-fast-as-possible playback if the element is set to live (`real-time-playback=true`). Option `all` can also be used if `real-time-playback=false` to result in the same behaviour, however, downstream sink element cannot be set to `async=true` as it would cause the pipeline to freeze due to lack of clock.

#### Streaming from Playback with looping
- Only option `all` can be used, which provides as-fast-as-possible playback. Similarly, do not use `real-time-playback=false` with downstream sink element set to `async=true`.

| **Streaming Source** | **Recommended `real-time-playback`** | **Recommended Option** | **Alternative** |
|:---------------------:|:------------------------------------:|:---------------------------------------------:|:-----------------------------------:|
| Device | Does no apply, Always live | `all` | - |
| Playback | Live (true) | `common` `individual` | `all`: as-fast -as-possible |
| Playback with looping | Live (true) | `all`: as-fast -as-possible | - |


# Contributing

Please see [the contribution guidelines](CONTRIBUTING.md) for instructions on how to contribute.

# License

This project is licensed under the [GNU Lesser General Public License, version 2.1](LICENSE). Copyright 2019 Aivero.
