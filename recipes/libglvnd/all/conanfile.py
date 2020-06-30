from conans import AutoToolsBuildEnvironment, ConanFile, tools


class LibglvndConan(ConanFile):
    description = "The GL Vendor-Neutral Dispatch library"
    license = "custom"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    options = {
        "x11": [True, False],
    }
    default_options = ("x11=True",)
    exports = "ignore-warnings.patch"

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("autotools/[^1.0.0]")
        if self.options.x11:
            self.build_requires("xorgproto/[^2019.1]")

    def requirements(self):
        if self.options.x11:
            self.requires("libx11/[^1.6.8]")
            self.requires("libxext/[^1.3.4]")

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

    def package_info(self):
        self.env_info.__EGL_VENDOR_LIBRARY_DIRS.append("/usr/share/glvnd/egl_vendor.d")
