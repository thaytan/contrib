#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools
import os
from datetime import datetime

def get_version():
    git = tools.Git()
    try:
        tag, branch = git.get_tag(), git.get_branch()
        return tag if tag and branch.startswith("HEAD") else branch
    except:
        return None

def make_cargo_version(version_string):
    try:
        version = tools.Version(version_string, loose=False)
        return "%d.%d.%d" % (version.major, version.minor, version.patch)
    except:
        return "0.0.0-nottagged"

class RealsenseConan(ConanFile):
    name = "gst-realsense"
    version = get_version()
    description = "GStreamer plugin containing `video/rgbd` source for a RealSense device"
    url = "https://aivero.com"
    license = "LGPL"
    settings = "os", "arch", "compiler", "build_type", "gstreamer"
    exports_sources = [
        "Cargo.toml",
        "schema/*",
        "src/*",
        "build.rs"
    ]
    generators = "env"

    def source(self):
        # Override the version supplied to GStreamer, as specified in lib.rs
        tools.replace_path_in_file(file_path="src/lib.rs", search="\"2017-12-01\"", replace=("\"%s\"" % datetime.now().strftime("%Y-%m-%d")))
        # Override the package version defined in the Cargo.toml file
        tools.replace_path_in_file(file_path="Cargo.toml", search=("[package]\nname = \"%s\"\nversion = \"0.0.0-ohmyconanpleaseoverwriteme\"" % self.name), replace=("[package]\nname = \"%s\"\nversion = \"%s\"" % (self.name, make_cargo_version(self.version))))

    def build_requirements(self):
        self.build_requires("generators/[>=1.0.0]@%s/stable" % self.user)
        self.build_requires("rust/[>=1.40.0]@%s/stable" % self.user)
        self.build_requires("sccache/[>=0.2.12]@%s/stable" % self.user)

    def requirements(self):
        self.requires("gstreamer-depth-meta/[>=0.2.0]@%s/stable" % self.user)
        self.requires("rgbd-timestamps/[>=2.0.0]@%s/stable" % self.user)
        self.requires("gstreamer-plugins-base/[~%s]@%s/stable" % (self.settings.gstreamer, self.user))
        self.requires("librealsense/[>=2.20.0]@%s/stable" % self.user)
        self.requires("capnproto/[>=0.7.0]@%s/stable" % self.user)

    def build(self):
        if self.settings.build_type == 'Release':
            self.run("cargo build --release")
        elif self.settings.build_type == 'Debug':
            self.run("cargo build")
        else:
            print('Invalid build_type selected')

    def package(self):
        self.copy(pattern="*.so", excludes="*realsensesrc.so", dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        self.copy(pattern="*realsensesrc.so", dst=os.path.join(self.package_folder, "lib", "gstreamer-1.0"), keep_path=False)

    def package_info(self):
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
        self.cpp_info.srcdirs.append("src")
