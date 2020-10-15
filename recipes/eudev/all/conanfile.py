from conans import AutoToolsBuildEnvironment, ConanFile, tools


class EudevConan(ConanFile):
    description = "OpenRC compatible fork of systemd-udev"
    license = "GPL2"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "clang/[^10.0.1]",
        "autotools/[^1.0.0]",
        "gperf/[^3.1]",
        "gobject-introspection/[^1.59.3]",
    )

    def source(self):
        tools.get(f"https://dev.gentoo.org/~blueness/eudev/eudev-{self.version}.tar.gz")

    def build(self):
        args = [
            "--disable-static",
        ]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"eudev-{self.version}", args)
        autotools.make()
        autotools.install()
