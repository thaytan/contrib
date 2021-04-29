# librealsense-rs

Unofficial Rust FFI bindings for `librealsense`. For more information, please visit the official API documentation [here](https://intelrealsense.github.io/librealsense/doxygen/index.html).

## Overview

These bindings are based on [`librealsense-sys`](https://gitlab.com/aivero/streaming/librealsense-sys), which automatically exposes the C API of `librealsense` by the use of [`bindgen`](https://rust-lang.github.io/rust-bindgen/). This repository (`librealsense-rs`) makes the auto-generated `librealsense-sys` bindings more idiomatic and safe for use in applications.

The general structure of these bindings closely follows the C API with all structs implemented to automatically release the memory they use on `drop()`. Therefore, it is generally a good idea to first look into the [official C/C++ API documentation](https://intelrealsense.github.io/librealsense/doxygen/dir_9d25e8b11fe18f2432ba6c8d035b608c.html) before finding a corresponding method in these bindings.

File [*high_level_utils.rs*](src/high_level_utils.rs) contains few higher-level functionalities that combine multiple methods of the API. Please feel free to add additional functionalities in this file.

These bindings contain majority of the high-level functionalities that utilise `Pipeline`, however, most of the low-level internal interactions with `Sensor`s are currently missing. 

# Getting Started

We recommend that you use conan to manage your dependencies. These guidelines assume that you do. You may also build the bindings by installing librealsense on your system, but do so at your own peril.

## Setup

First you need to install and setup conan, as we use that to handle our dependencies. Before you start, please make sure
that your default python version is 3.X and that pip installs packages for python 3. Then run:

```bash
pip install conan --user
# You may need to source ~/.profile here, please see https://docs.conan.io/en/latest/installation.html#known-installation-issues-with-pip
conan config install https://github.com/aivero/conan-config.git
# And to ensure that the remote is configured properly:
conan search -r aivero librealsense
# You should now see a list of all the releases of librealsense
```

## Building

With conan installed you're ready to proceed. This section details how to use cargo to build the bindings. We do not have a conan package for this project, as we rely on cargo to include and build the bindings for us.

```bash
cd librealsense-rs
conan install . aivero/stable -if build
source build/env.sh
cargo build
```

## Add as dependency

If you wish to use the librealsense bindings, you'll need to add them as a dependency in another project. Please add the following to your `Cargo.toml` file:

```toml
librealsense2 = { git = "https://gitlab.com/aivero/public/librealsense-rs", tag="1.0.1" }
```

You will also need a librealsense installation, which the bindings can be generated against. Again, we recommend that you use conan to do so. Please create a `conanfile.txt` in the project and put in the following content:

```
[build_requires]
clang/[>=9.0.0]@aivero/stable
env-generator/[>=1.0.0]@aivero/stable
rust/[>=1.38.0]@aivero/stable

[requires]
librealsense/[>=2.28.1]@aivero/stable

[generators]
env
```

You will then need to execute the following to build your project:

```bash
conan install . aivero/stable -if build
source build/env.sh
cargo build
```

Sadly, this also means that you cannot build from your IDE as of yet.

# Missing features

The following is the list of functionalities that are not yet mapped. Feel free to create a new issue if you need some of them.

*context*
- Explicit addition and removal of physical or software devices
- Device Hub

*device*
- Firmware updates
- Writing and resetting of calibration
- Manipulation with device's flash

*frame*
- Points and texture coordinates
- Exporting to ply
- Others ...

*sensor*
- Majority of functionalities

*internal*
- Everything

*option*
- Everything

*processing*
- Everything

*record_playback*
- Everything

# Contributing

Please see [the contribution guidelines](CONTRIBUTING.md) for instructions on how to contribute.

# License

This project is licensed under the [MIT License](LICENSE). Copyright 2019 Aivero.
