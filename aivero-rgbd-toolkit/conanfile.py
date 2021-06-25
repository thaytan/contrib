from build import *


class AiveroRgbDToolkit(GstProject):
    description = "Package containing all open source RGB-D elements"
    license = "LGPL"
    exports_sources = ["*.adoc", "scripts/*"]
    requires = (
        f"gst-rgbd/{branch()}",
        f"gst-rgbd-src/{branch()}",
        f"gst-colorizer/{branch()}",
        "gst-plugins-good/[~1.18]",
        "gst-plugins-bad/[~1.18]",
        ## `libglvnd` is currently removed because it causes problems for `glimagesink`
        # self.requires("libglvnd/[>=1.2.0]@%s/stable" % self.user)
    )

    def build(self):
        # Don't build anything
        pass

    def package(self):
        self.copy(pattern="*.adoc*", keep_path=False)
        self.copy("*", src="scripts/", dst="scripts", keep_path=False)

    def deploy(self):
        install_path = os.getcwd()
        self.copy("*.adoc", dst="readmes", keep_path=False)
        self.copy("*", src="scripts/", dst="scripts", keep_path=False)
        # Gstreamer binaries
        self.copy_deps("*gst-inspect-1.0", dst="bin", keep_path=False)
        self.copy_deps("*gst-launch-1.0", dst="bin", keep_path=False)
        self.copy_deps("*gst-plugin-scanner", dst="bin", keep_path=False)

        # Pkg-config files
        self.copy_deps("*.pc", dst="lib/pkgconfig", keep_path=False)
        for pc_file in os.listdir("lib/pkgconfig"):
            tools.replace_prefix_in_pc_file(
                os.path.join("lib", "pkgconfig", pc_file), install_path)

        # Libraries
        self.copy_deps("*.so*", excludes="*python*")
        self.copy_deps("*.h*")

        # Environment script
        with open(os.path.join(install_path, "aivero_environment.sh"),
                  "w+") as env_file:

            env_file.write("export PREFIX=" + install_path)
            env_file.write("\nexport PATH=" + os.path.join("$PREFIX", "bin") +
                           ":$PATH")
            env_file.write("\nexport LD_LIBRARY_PATH=" +
                           os.path.join("$PREFIX", "lib") +
                           ":$LD_LIBRARY_PATH")
            env_file.write("\nexport PKG_CONFIG_PATH=" +
                           os.path.join("$PREFIX", "lib", "pkgconfig"))
            env_file.write("\nexport GST_PLUGIN_PATH=" +
                           os.path.join("$PREFIX", "lib", "gstreamer-1.0"))
            env_file.write(
                "\nexport GST_PLUGIN_SCANNER=" +
                os.path.join("$PREFIX", "bin", "gst-plugin-scanner"))

            env_file.write("\nexport PYTHONPATH=$PYTHONPATH:" +
                           os.path.join("$PREFIX", "lib"))
            env_file.write("\nexport LIBVA_DRIVERS_PATH=" +
                           os.path.join("$PREFIX", "lib", "dri"))
