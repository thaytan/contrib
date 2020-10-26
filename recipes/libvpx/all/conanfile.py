from build import *


class LibVpxRecipe(Recipe):
    description = "WebM VP8/VP9 Codec SDK"
    license = "BSD"
    build_requires = (
        "make/[^4.3]",
        "yasm/[^1.3.0]",
    )

    def source(self):
        self.get(f"https://github.com/webmproject/libvpx/archive/v{self.version}.tar.gz")

    def build(self):
        args = [
            "--enable-shared",
            "--disable-static",
            "--disable-examples",
            "--disable-install-docs",
            "--disable-install-srcs",
        ]
        os.environ["STRIP"] = "no"
        self.autotools(args)
