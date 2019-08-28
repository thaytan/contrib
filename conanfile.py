#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools
import os

class RealsenseConan(ConanFile):
    name = "gst-realsense"
    version = "0.1.0"
    description = "Realsense gstreamer source element"
    url = "https://aivero.com"
    license = "Proprietary"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = [
        "Cargo.toml",
        "src/*",
    ]
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/stable" % self.user)
        self.requires("gstreamer-depth-meta/0.2.0@%s/stable" % self.user)
        self.requires("librealsense/2.20.0@%s/stable" % self.user)

    def build(self):
        if self.settings.build_type == 'Release':
            self.run("cargo build --release")
        elif self.settings.build_type == 'Debug':
            self.run("cargo build")
        else:
            print('Invalid build_type selected')

    def package(self):
        self.copy(pattern="*.so", dst=os.path.join(self.package_folder, "lib", "gstreamer-1.0"), keep_path=False)

    def package_info(self):
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
        self.cpp_info.srcdirs.append("src")
