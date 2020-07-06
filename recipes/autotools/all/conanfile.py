from conans import *


class AutotoolsConan(ConanFile):
    description = "A suite of programming tools 'designed' to assist in making source code"
    license = "GPL"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    requires = (
        "base/[^1.0.0]",
        "cc/[^1.0.0]",
        "make/[^3.4.0]",
        "autoconf/[^2.69]",
        "automake/[^1.16.1]",
        "libtool/[^2.4.6]",
        "pkgconf/[^1.6.3]",
        "gettext/[^0.20.1]",
        "texinfo/[^6.6]",
    )
