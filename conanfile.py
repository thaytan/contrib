from conans import ConanFile, tools
from os import symlink, path

pc_content = """
prefix=%s
exec_prefix=${prefix}/bin
includedir=${prefix}/include
libdir=${prefix}/lib

Name: libv4l2
Description: v4l2 device access library
Version: %s
Requires.private: libv4lconvert
Libs: -L${libdir} -lv4l2
Libs.private: -lpthread
Cflags: -I${includedir}
"""

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "32.2.1"
    except:
        return None

class V4l2(ConanFile):
    name = "nv-v4l2"
    version = get_version()
    license = "LGPL"
    description = "NVIDIA built Accelerated GStreamer Plugins"
    url = "https://developer.nvidia.com/embedded/linux-tegra"
    settings = "os", "compiler", "build_type", "arch"
    options = {"jetson": ["Nano", "TX2", "Xavier"]}
    default_options = ("jetson=TX2",)
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/stable" % self.user)
        self.requires("nv-v4lconvert/%s@%s/stable" % (self.version, self.user))

    def source(self):
        if self.options.jetson in ("TX2", "Xavier"):
            tools.get("https://developer.nvidia.com/embedded/dlc/r%s_Release_v1.0/TX2-AGX/sources/public_sources.tbz2" % self.version.replace(".", "-"))
        elif self.options.jetson == "Nano":
            tools.get("https://developer.nvidia.com/embedded/dlc/r%s_Release_v1.0/Nano-TX1/sources/public_sources.tbz2" % self.version.replace(".", "-"))
        else:
            raise KeyError( "Unknown option: " + self.options.jetson)

        tools.untargz("public_sources/v4l2_libs_src.tbz2", self.source_folder)
        tools.rmdir("public_sources")

    def build(self):
        # Hack to workaround hardcoded library path
        env = {"DEST_DIR": path.join(self.deps_cpp_info["nv-v4lconvert"].rootpath, "lib")}
        with tools.chdir("libv4l2"), tools.environment_append(env):
            self.run("make")
            symlink("libnvv4l2.so", "libv4l2.so")
        with open("libv4l2.pc", "w") as pc:
            pc.write(pc_content % (self.package_folder, self.version))

    def package(self):
        self.copy("*.so*", dst="lib", keep_path=False)
        self.copy("*.h", dst="include", keep_path=False)
        self.copy("libv4l2.pc", dst="lib/pkgconfig", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
