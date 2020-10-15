from conans import *


class GperfConan(ConanFile):
    description = "A portable, high level programming interface to various calling conventions"
    license = "GPL3"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "meson/[^0.55.3]",
        "clang/[^10.0.1]",
    )

    def source(self):
        tools.get(f"https://gitlab.com/aivero/public/gperf/-/archive/meson/gperf-meson.tar.gz")

    def build(self):
        meson = Meson(self)
        meson.configure(source_folder="gperf-meson")
        meson.install()
