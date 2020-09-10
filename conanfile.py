#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools
import os

def get_version():
    try:
        git = tools.Git()
        tag, branch = git.get_tag(), git.get_branch()
        return tag if tag and branch.startswith("HEAD") else branch
    except:
        return tools.get_env("GIT_BRANCH", "master")


def make_cargo_version(version_string):
    try:
        version = tools.Version(version_string, loose=False)
        return "%d.%d.%d" % (version.major, version.minor, version.patch)
    except:
        return "0.0.0-nottagged"


class K4aSrcConan(ConanFile):
    name = "gst-k4a"
    version = get_version()
    description = "GStreamer plugin containing `video/rgbd` source for an Azure Kinect DK (K4A) device"
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

    def build_requirements(self):
        self.build_requires("generators/[>=1.0.0]@%s/stable" % self.user)
        self.build_requires("rust/[>=1.3.8]@%s/stable" % self.user)
        self.build_requires("sccache/[>=0.2.12]@%s/stable" % self.user)

    def requirements(self):
        self.requires("gstreamer-depth-meta/[>=0.2.0]@%s/stable" % self.user)
        self.requires("rgbd-timestamps/[>=2.0.0]@%s/stable" % self.user)
        self.requires("k4a/[>=1.4.0]@%s/stable" % self.user)
        self.requires("capnproto/[>=0.7.0]@%s/stable" % self.user)

    def source(self):
        # Override the package version defined in the Cargo.toml file
        tools.replace_path_in_file(file_path="Cargo.toml", search=("[package]\nname = \"%s\"\nversion = \"0.0.0-ohmyconanpleaseoverwriteme\"" % self.name), replace=("[package]\nname = \"%s\"\nversion = \"%s\"" % (self.name, make_cargo_version(self.version))))

    def build(self):
        if self.settings.build_type == 'Release':
            self.run("cargo build --release")
        elif self.settings.build_type == 'Debug':
            self.run("cargo build")
        else:
            print('Invalid build_type selected')

    def package(self):
        self.copy(pattern="*.so", excludes="*k4asrc.so", dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        self.copy(pattern="*k4asrc.so", dst=os.path.join(self.package_folder, "lib", "gstreamer-1.0"), keep_path=False)

    def package_info(self):
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
        self.cpp_info.srcdirs.append("src")
