from conans import *


class P11KitConan(ConanFile):
    description = "Loads and enumerates PKCS#11 modules"
    license = "BSD"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cc/[^1.0.0]",
        "make/[^4.3]",
        "pkgconf/[^1.7.3]",
        "libtasn1/[^4.16.0]",
        "libffi/[^3.3]",
    )

    def source(self):
        tools.get(f"https://github.com/p11-glue/p11-kit/releases/download/{self.version}/p11-kit-{self.version}.tar.xz")

    def build(self):
        args = [
            "--without-trust-paths",
        ]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"p11-kit-{self.version}", args)
        autotools.make()
        autotools.install()
