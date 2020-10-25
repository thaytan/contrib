import os
from conans import *


class CairoConan(ConanFile):
    description = "2D graphics library with support for multiple output devices"
    license = "LGPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "autotools/[^1.0.0]",
        "gobject-introspection/[^1.66.1]",
        "mesa/[^20.2.1]",
        "zlib/[^1.2.11]",
    )
    requires = (
        "glib/[^2.62.0]",
        "pixman/[^0.40.0]",
        "fontconfig/[^2.13.92]",
        "libpng/[^1.6.37]",
        "libxrender/[^0.9.10]",
        "libxext/[^1.3.4]",
    )

    def source(self):
        tools.get(f"https://gitlab.freedesktop.org/cairo/cairo/-/archive/{self.version}/cairo-{self.version}.tar.gz")

    def build(self):
        args = [
            "--disable-static",
            "--disable-gl",
            "--enable-gobject",
        ]
        os.environ["CFLAGS"] += " -lpthread"
        os.environ["CPPFLAGS"] = f"-I{os.path.join(self.deps_cpp_info['zlib'].rootpath, 'include')}"
        os.environ["NOCONFIGURE"] = "1"
        autotools = AutoToolsBuildEnvironment(self)
        self.run(f"sh autogen.sh", cwd=f"cairo-{self.version}")
        autotools.configure(f"cairo-{self.version}", args)
        autotools.install()
