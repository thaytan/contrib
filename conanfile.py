#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os
import glob
import shutil

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "4.1"
    except:
        return None

class FFMpegConan(ConanFile):
    name = "ffmpeg"
    version = get_version()
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "A complete, cross-platform solution to record, convert and stream audio and video"
    license = "https://github.com/FFmpeg/FFmpeg/blob/master/LICENSE.md"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/%s" % (self.user, self.channel))

    def build_requirements(self):
        self.build_requires("yasm/1.3.0@%s/%s" % (self.user, self.channel))

    def source(self):
        tools.get("http://ffmpeg.org/releases/ffmpeg-%s.tar.bz2" % self.version)

    def build(self):
        prefix = tools.unix_path(self.package_folder) if self.settings.os == 'Windows' else self.package_folder
        args = [
            '--disable-doc',
            '--disable-programs'
        ]
        if self.settings.build_type == 'Debug':
            args.extend(['--disable-optimizations', '--disable-mmx', '--disable-stripping', '--enable-debug'])

        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args, build=False, host=False, target=False)
            autotools.make()
            autotools.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.srcdirs.append("src")
