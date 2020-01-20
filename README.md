# gst-rgbd 

GStreamer plugin for demuxing and muxing video/rgbd streams using `rgbddemux` and `rgbdmux` respectively.

## `rgbddemux`

GStreamer element for demuxing a single `video/rgbd` stream that creates a `src_%s` pad with `video/x-raw` caps for each detected stream.

## `rgbdmux`

GStreamer element for muxing multiple `video/x-raw` on its `sink_%s` sink pads into a single `video/rgbd`.

## `video/rgbd`
 
The `video/rgbd` caps always contain the following fields

- **streams** - This field contains selected streams with priority `depth > infra1 > infra2 > color`. The first stream 
in this comma separated string, e.g. "depth,infra2,color", is considered to be the main stream and is therefore 
transported in the main buffer. There must always be at least one stream enabled. All additional buffers are attached as
meta to the main buffer.
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
conan remote add aivero https://conan.aa.aivero.dev/artifactory/api/conan/aivero-public
# And to ensure that the remote is configured properly:
conan search -r aivero gst-rgbd
# You should now see a list of all the releases of gst-realsense 
```

## Install a tagged release

You may use conan to install a pre-built release of the gst-realsense package:

```bash
conan install gst-rgbd/0.1.6@aivero/stable -if installation
export GST_PLUGIN_PATH=$GST_PLUGIN_PATH:$PWD/installation
# And validate that the plugins are properly installed
gst-inspect-1.0 rgbd
```

## Build your own

### Using Cargo

If you have made changes to the `rgbddemux` or `rgbdmux` that you wish to try, you may want to build the project locally: 
```bash
cd gst-rgbd
conan install -if build . aivero/stable
source build/env.sh
cargo build --release
export GST_PLUGIN_PATH=$GST_PLUGIN_PATH:$PWD/target/release
```

> Note: `conan install -if build . aivero/stable` might require you to build extra packages. Just follow the instructions in the error message.

Now you should see the plugin's element `rgbddemux` and `rgbdmux`.
```bash
gst-inspect-1.0 rgbd
``` 

### Using conan

If you have a project with many dependencies, it quickly becomes tiresome to manage them manually. You will, as we say
in Danish, get gray hair. Conan may come in handy in such cases, and thus you may want to build a conan package locally:

```bash
conan create . aivero/stable
```

Conan will report the name it has given the package, e.g. `gst-rgbd/master@aivero/stable`. Please take a note of that name.

Yoy may now add the package as a dependency in another project, please add the following to the `conanfile.py` in the 
other project:

```python
def requirements(self):
    # replace the name below with the name you took note of earlier
    self.requires("gst-rgbd/master@%s/stable" % self.user)
```

## Running in combination with [`rgbddemux`](https://gitlab.com/aivero/public/gstreamer/gst-rgbd)

Source and export `GST_PLUGIN_PATH` in a single terminal for both `realsensesrc` and `rgbddemux` (if not done before).

```bash
source gst-realsense/build/env.sh --extend
export GST_PLUGIN_PATH=gst-realsense/target/release:${GST_PLUGIN_PATH}

source gst-rgbd/build/env.sh --extend
export GST_PLUGIN_PATH=gst-rgbd/target/release:${GST_PLUGIN_PATH}
```

An example of a pipeline:

```bash 
# Please replace XXXXXXXX with the serial on your RealSense camera
export RS_SERIAL=XXXXXXXX
gst-launch-1.0 realsensesrc serial=$RS_SERIAL enable-depth=true enable-infra2=true enable-color=true ! \
rgbddemux name=realsense_demux \
realsense_demux.src_depth ! queue ! glimagesink  \ 
realsense_demux.src_infra2 ! queue ! glimagesink \ 
realsense_demux.src_color ! queue ! glimagesink
```