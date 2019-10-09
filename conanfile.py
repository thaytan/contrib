import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class BinutilsConan(ConanFile):
    name = "binutils"
    version = tools.get_env("VERSION", "2.30")
    settings = "os", "compiler", "build_type", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "MIT"
    description = (
        "A portable, high level programming interface to various calling conventions"
    )
    generators = "env"

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)

    def source(self):
        arch_conv = {"x86_64": ("x86-64", "amd64"), "armv8": ("aarch64", "arm64")}
        tools.get(
            "https://mex.mirror.pkgbuild.com/core/os/x86_64/binutils-2.32-3-x86_64.pkg.tar.xz"
        )
        tools.download(
            "http://security.ubuntu.com/ubuntu/pool/main/b/binutils/binutils-%s-linux-gnu_%s-%s_%s.deb"
            % (
                arch_conv[str(self.settings.arch)][0],
                self.version,
                os.environ.get("DEB_VERSION", "21ubuntu1~18.04.2"),
                arch_conv[str(self.settings.arch)][1],
            ),
            filename="binutils.deb",
        )

    def build(self):
        env = {"LD_LIBRARY_PATH": "usr/lib", "PATH": "usr/bin"}
        with tools.environment_append(env):
            self.run("ar x binutils.deb")
            tools.unzip("data.tar.xz", destination="data")
        with tools.chdir("data/usr/bin"):
            for lib in os.listdir():
                os.symlink(lib, lib.split("-")[-1])
        tools.rmdir("usr")

    def package(self):
        self.copy("*", dst="bin", src="data/usr/bin", symlinks=True)
