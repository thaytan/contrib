from conans import AutoToolsBuildEnvironment, ConanFile, tools


class LibglvndConan(ConanFile):
    name = "libglvnd"
    version = tools.get_env("GIT_TAG", "1.2.0")
    description = "The GL Vendor-Neutral Dispatch library"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "custom"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "x11": [True, False],
    }
    default_options = ("x11=True", )
    exports = "ignore-warnings.patch"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("autotools/[>=1.0.0]@%s/stable" % self.user)
        if self.options.x11:
            self.build_requires("xorgproto/[>=2019.1]@%s/stable" % self.user)

    def requirements(self):
        if self.options.x11:
            self.requires("libx11/[>=1.6.8]@%s/stable" % self.user)
            self.requires("libxext/[>=1.3.4]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/NVIDIA/libglvnd/archive/v%s.tar.gz" % self.version)
        tools.patch(patch_file="ignore-warnings.patch", base_path="%s-%s" % (self.name, self.version))

    def build(self):
        args = ["--disable-static"]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.install()
