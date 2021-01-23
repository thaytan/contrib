# gst-rgbd 

GStreamer plugin for demuxing and muxing video/rgbd streams using `rgbddemux` and `rgbdmux` respectively.

`rgbddemux` - GStreamer element for demuxing a single `video/rgbd` stream that creates a `src_%s` pad with `video/x-raw` caps for each detected stream.

`rgbdmux` - GStreamer element for muxing multiple `video/x-raw` on its `sink_%s` sink pads into a single `video/rgbd`.

The setup instructions can be found below. To find more information about the element and its use, please see the documentation [here](docs/modules/ROOT/pages/rgbd.adoc).


# Getting started

> Note: This repo builds and installs **only** `rgbddemux` and `rgbdmux`. Please head to the [Aivero RGB-D Toolkit](https://gitlab.com/aivero/public/aivero-rgbd-toolkit) to install a complete set of elements for handling RGB-D cameras.

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

# Changelog

Versions and corresponding changes can be tracked in [changelog](CHANGELOG.md) of this repository.

# Contributing

Please see [the contribution guidelines](CONTRIBUTING.md) for instructions on how to contribute.

# License

This project is licensed under the [GNU Lesser General Public License, version 2.1](LICENSE). Copyright 2019 Aivero.
