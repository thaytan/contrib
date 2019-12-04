#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools
import os

def get_version():
    git = tools.Git()
    try:
        tag, branch = git.get_tag(), git.get_branch()
        return tag if tag and branch.startswith("HEAD") else branch
    except:
        return None


class K4aSrcConan(ConanFile):
    name = "gst-k4a"
    version = get_version()
    description = "GStreamer plugin containing `video/rgbd` source for an Azure Kinect DK (K4A) device"
    url = "https://aivero.com"
    license = "LGPL"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = [
        "Cargo.toml",
        "schema/*",
        "src/*",
        "build.rs"
    ]
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.build_requires("rust/[>=1.3.8]@%s/stable" % self.user)
        self.build_requires("sccache/[>=0.2.12]@%s/stable" % self.user)

    def requirements(self):
        self.requires("gstreamer-depth-meta/[>=0.2.0]@%s/stable" % self.user)
        self.requires("k4a/[>=1.3.0]@aivero/testing")

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
