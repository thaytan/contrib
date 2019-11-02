from conans import ConanFile, tools


class Deepstream(ConanFile):
    name = "deepstream"
    version = tools.get_env("GIT_TAG", "4.0.1")
    license = "proprietary"
    description = "Complete streaming analytics toolkit for AI-based video"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    settings = "os", "compiler", "build_type", "arch"
    options = {"jetson": ["Nano", "TX2", "Xavier"]}
    default_options = ("jetson=TX2",)
    generators = "env"

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/%s" % (self.user, self.channel))

    def source(self):
        if self.options.jetson in ("TX2", "Xavier"):
            tools.get(
                "https://developer.download.nvidia.com/assets/Deepstream/Deepstream_{0}/deepstream_sdk_v{0}_jetson.tbz2".format(
                    self.version
                )
            )
        else:
            raise KeyError("Unknown option: " + self.options.jetson)

        tools.untargz(
            "deepstream_sdk_v%s_jetson/binaries.tbz2" % self.version, self.source_folder
        )

    def package(self):
        self.copy("*.so*", dst="lib", keep_path=False)
        self.copy(
            "*",
            dst="include",
            src="deepstream_sdk_v%s_jetson/sources/includes" % self.version,
            keep_path=False,
        )
