#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os

class AiveroRgbDToolkit(ConanFile):
    name = "aivero_rgbd_toolkit"
    description = "Package containing all open source RGB-D elements"
    url = "https://aivero.com"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type", "gstreamer"
    exports_sources = [
        "*.adoc",
        "scripts/*"
    ]
    
    def set_version(self):
        self.version =  tools.get_env("CI_COMMIT_REF_SLUG", "master")

    def requirements(self):
        self.requires("gst-rgbd/[>=0.4.0]@%s/stable" % self.user)
        self.requires("gst-k4a/[>=1.1.1]@%s/stable" % self.user)
        self.requires("gst-realsense/[>=2.1.1]@%s/stable" % self.user)
        self.requires("gstreamer-colorizer/[>=0.1.2]@%s/stable" % self.user)
        self.requires("gstreamer-plugins-base/[~%s]@%s/stable" % (self.settings.gstreamer, self.user))
        self.requires("gstreamer-plugins-good/[~%s]@%s/stable" % (self.settings.gstreamer, self.user))
        self.requires("gstreamer-plugins-bad/[~%s]@%s/stable" % (self.settings.gstreamer, self.user))

    def package(self):
        self.copy(pattern="*.adoc*", keep_path=False)
        self.copy("*", src="scripts/", dst="scripts", keep_path=False)

    def deploy(self):
        install_path = os.getcwd()
        self.copy("*.adoc",  dst="readmes", keep_path=False)
        self.copy("*", src="scripts/", dst="scripts", keep_path=False)
        # Gstreamer binaries
        self.copy_deps("*gst-inspect-1.0", dst="bin", keep_path=False)
        self.copy_deps("*gst-launch-1.0", dst="bin", keep_path=False)
        self.copy_deps("*gst-plugin-scanner", dst="bin", keep_path=False)

        # Pkg-config files
        self.copy_deps("*.pc", dst="lib/pkgconfig", keep_path=False)
        for pc_file in os.listdir("lib/pkgconfig"):
            tools.replace_prefix_in_pc_file(os.path.join("lib", "pkgconfig", pc_file), install_path)

        # Libraries
        self.copy_deps("*.so*", excludes="*python*")
        self.copy_deps("*.h*")

        # Environment script
        with open(os.path.join(install_path, "aivero_environment.sh"), "w+") as env_file:
            license_folder = os.path.join(install_path, "licenses")
            os.mkdir(license_folder)

            env_file.write("export PREFIX=" + install_path)
            env_file.write("\nexport PATH=" + os.path.join("$PREFIX", "bin") + ":$PATH")
            env_file.write("\nexport LD_LIBRARY_PATH=" + os.path.join("$PREFIX", "lib") + ":$LD_LIBRARY_PATH")
            env_file.write("\nexport PKG_CONFIG_PATH=" + os.path.join("$PREFIX", "lib", "pkgconfig"))
            env_file.write("\nexport GST_PLUGIN_PATH=" + os.path.join("$PREFIX", "lib", "gstreamer-1.0"))
            env_file.write("\nexport GST_PLUGIN_SCANNER=" + os.path.join("$PREFIX", "bin", "gst-plugin-scanner"))

            env_file.write("\nexport PYTHONPATH=$PYTHONPATH:" + os.path.join("$PREFIX", "lib"))
            env_file.write("\nexport LIBVA_DRIVERS_PATH=" + os.path.join("$PREFIX", "lib", "dri"))
