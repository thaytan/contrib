from conans import ConanFile, tools
from os import symlink, path

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "4.0"
    except:
        return None

class Deepstream(ConanFile):
    name = "deepstream"
    version = get_version()
    license = "proprietary"
    description = "Complete streaming analytics toolkit for AI-based video"
    url = "https://developer.nvidia.com/embedded/linux-tegra"
    settings = "os", "compiler", "build_type", "arch"
    options = {"jetson": ["Nano", "TX2", "Xavier"]}
    default_options = ("jetson=TX2",)
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/%s" % (self.user, self.channel))

    def source(self):
        if self.options.jetson in ("TX2", "Xavier"):
            tools.get("https://developer.download.nvidia.com/assets/Deepstream/Deepstream_{0}/deepstream_sdk_v{0}_jetson.tbz2".format(self.version))
        else:
            raise KeyError("Unknown option: " + self.options.jetson)

        tools.untargz("deepstream_sdk_v%s_jetson/binaries.tbz2" % self.version, self.source_folder)
        tools.rmdir("deepstream_sdk_v%s_jetson" % self.version)

    def package(self):
        self.copy("*.so*", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
