#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os
import glob
import shutil


class FFMpegConan(ConanFile):
    name = "ffmpeg"
    version = "4.1"
    default_user = "bincrafters"
    default_channel = "stable"
    url = "https://github.com/bincrafters/conan-ffmpeg"
    description = "A complete, cross-platform solution to record, convert and stream audio and video"
    license = "https://github.com/FFmpeg/FFmpeg/blob/master/LICENSE.md"
    exports_sources = ["LICENSE"]
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = (
        "fPIC=True",
    )

    def source(self):
        tools.get("http://ffmpeg.org/releases/ffmpeg-%s.tar.bz2" % self.version)

    def build_requirements(self):
        self.build_requires("yasm_installer/1.3.0@%s/%s" % (self.user, self.channel))

    def build(self):
        prefix = tools.unix_path(self.package_folder) if self.settings.os == 'Windows' else self.package_folder
        args = ['--prefix=%s' % prefix,
                '--disable-doc',
                '--disable-programs']
        if self.settings.build_type == 'Debug':
            args.extend(['--disable-optimizations', '--disable-mmx', '--disable-stripping', '--enable-debug'])

        with tools.chdir(os.path.join(self.source_folder, "ffmpeg-" + self.version)):
            env_build = AutoToolsBuildEnvironment(self)
            env_build.configure(args=args, build=False, host=False, target=False)
            env_build.make()
            env_build.make(args=['install'])

    def package(self):
        if self.channel == "testing":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.srcdirs.append("src")
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
        self.env_info.SOURCE_PATH.append(os.path.join(self.package_folder, "src"))
        for file in os.listdir(os.path.join(self.package_folder, "lib", "pkgconfig")):
            setattr(self.env_info, "PKG_CONFIG_%s_PREFIX" % file[:-3].replace(".", "_").replace("-", "_").upper(), self.package_folder)
