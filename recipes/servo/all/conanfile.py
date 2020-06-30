import os
import shutil

from conans import ConanFile, tools


class ServoConan(ConanFile):
    name = "servo"
    settings = "os", "compiler", "arch"
    license = "MIT", "Apache"
    description = "The Servo Browser Engine"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % self.user)
        self.build_requires("python/[>=3.7.4]@%s/stable" % self.user)
        self.build_requires("python-virtualenv/[>=3.7.4]@%s/stable" % self.user)
        self.build_requires("python-pillow/[>=7.1.2]@%s/stable" % self.user)
        self.build_requires("rustup/[>=1.21.1]@%s/stable" % self.user)

    def requirements(self):
        self.requires("openssl/[>=1.1.1b]@%s/stable" % self.user)
        self.requires("dbus/[>=1.12.16]@%s/stable" % self.user)
        self.requires("libx11/[>=1.6.8]@%s/stable" % self.user)
        self.requires("libunwind/[>=1.3.1]@%s/stable" % self.user)
        self.requires("gstreamer/[>=1.16.2]@%s/stable" % self.user)
        self.requires("gstreamer-plugins-base/[>=1.16.2]@%s/stable" % self.user)
        self.requires("gstreamer-plugins-bad/[>=1.16.2]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/noverby/servo/archive/{}.tar.gz".format(self.version))

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            self.run("echo $PATH")
            self.run("./mach build -r")