from conans import ConanFile, Meson, tools


def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "19.2.0"
    except:
        return None


class MesaConan(ConanFile):
    name = "mesa"
    version = get_version()
    settings = "os", "compiler", "build_type", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "custom"
    description = "An open-source implementation of the OpenGL specification"
    options = {"x11": [True, False]}
    default_options = ("x11=True",)
    generators = "env"

    def build_requirements(self):
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)
        self.build_requires("gettext/[>=0.20.1]@%s/stable" % self.user)
        self.build_requires("bison/[>=3.3]@%s/stable" % self.user)
        self.build_requires("flex/[>=2.6.4]@%s/stable" % self.user)
        self.build_requires("python-mako/[>=1.1.0]@%s/stable" % self.user)
        self.build_requires("zlib/[>=1.2.11]@%s/stable" % self.user)
        self.build_requires("expat/[>=2.2.7]@%s/stable" % self.user)
        self.build_requires("libdrm/[>=2.4.99]@%s/stable" % self.user)
        self.build_requires("libglvnd/[>=1.2.0]@%s/stable" % self.user)
        if self.options.x11:
            self.build_requires("libx11/[>=1.6.8]@%s/stable" % self.user)
            self.build_requires("libxext/[>=1.3.4]@%s/stable" % self.user)
            self.build_requires("libxdamage/[>=1.1.5]@%s/stable" % self.user)
            self.build_requires("libxshmfence/[>=1.3]@%s/stable" % self.user)
            self.build_requires("libxxf86vm/[>=1.1.4]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://mesa.freedesktop.org/archive/mesa-%s.tar.xz" % self.version)

    def build(self):
        args = [
            "--auto-features=disabled",
            "--wrap-mode=nofallback",
            "-Dglvnd=true",
            "-Dglx=dri",
            "-Degl=true",
            "-Dgles1=false",
            "-Dgles2=true",
            "-Dplatforms=x11",
            "-Dvulkan-drivers=",
            "-Dgallium-drivers=",
        ]
        if self.settings.arch == "x86_64":
            args.append("-Ddri-drivers=i915,i965")
        if self.settings.arch == "armv8":
            args.append("-Ddri-drivers=tegra")
        meson = Meson(self)
        meson.configure(source_folder="%s-%s" % (self.name, self.version), args=args)
        meson.install()
