# gst-realsense

GStreamer plugin containing `video/rgbd` source for RealSense devices and recordings.

The setup instructions can be found below. To find more information about the element and its use, please see the documentation [here](docs/modules/ROOT/pages/realsense.adoc).


# Getting started

> Note: This repo builds and installs **only** the `realsensesrc`. Additionally you require the `rgbddemux` element to display a `video/rgbd` stream. Please head to the [Aivero RGB-D Toolkit](https://gitlab.com/aivero/public/aivero-rgbd-toolkit) to install a complete set of elements for handling RGB-D cameras.

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

# Changelog

Versions and corresponding changes can be tracked in [changelog](CHANGELOG.md) of this repository.

# Contributing

Please see [the contribution guidelines](CONTRIBUTING.md) for instructions on how to contribute.

# License

This project is licensed under the [GNU Lesser General Public License, version 2.1](LICENSE). Copyright 2019 Aivero.
