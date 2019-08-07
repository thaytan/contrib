from conans import ConanFile, tools

def get_version():
    git = tools.Git()
    try:
        if git.get_tag() and not git.get_branch():
            return git.get_tag()
        else:
            return "32-2"
    except:
        return None

class V4l2(ConanFile):
    name = "nv-v4l2"
    version = get_version()
    license = "LGPL"
    description = "NVIDIA built Accelerated GStreamer Plugins"
    default_user = "aivero"
    default_channel = "stable"
    url = "https://developer.nvidia.com/embedded/linux-tegra"
    settings = "os", "compiler", "build_type", "arch"
    exports_sources= ["public_sources.tbz2"]
    options = {
    "jetson": ["Nano", "TX2", "Xavier"]
    }
    default_options = (
    "jetson=TX2",
    )
    generators = ["virtualenv", "virtualrunenv", "make"]
    def requirements(self):
        self.requires("nv-v4lconvert/%s@%s/%s" % (self.version, self.user, self.channel))

    def source(self):

        if (self.options.jetson in ["TX2", "Xavier"]):
            tools.download("https://developer.download.nvidia.com/embedded/L4T/r" + self.version + "_Release_v1.0/TX2-AGX/public_sources.tbz2", filename="public_sources.tbz2")
        elif (self.options.jetson in ["Nano"]):
            tools.download("https://developer.download.nvidia.com/embedded/L4T/r" + self.version + "_Release_v1.0/Nano-TX1/public_sources.tbz2", filename="public_sources.tbz2")
        else:
            raise KeyError("Unknown option: " + self.options.jetson)

        tools.untargz("public_sources.tbz2")
        tools.untargz("public_sources/v4l2_libs_src.tbz2", self.source_folder)
        tools.rmdir("public_sources")

    def build(self):
        vars = {
        }
        with tools.environment_append(vars):
            self.run("cd libv4l2 && make")

    def package(self):
        self.copy("*.so*")

    def package_info(self):
        self.cpp_info.libdirs = ["libv42"]
        self.cpp_info.libs = tools.collect_libs(self)
        for lib_path in self.cpp_info.lib_paths:
            self.env_info.LD_LIBRARY_PATH.append(lib_path)
