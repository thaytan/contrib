from build import *


class OpusRecipe(Recipe):
    description = "Modern audio compression for the internet"
    license = "BSD"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "gstreamer"
    build_requires = ("make/[^4.3]",)

    def source(self):
        self.get(f"https://archive.mozilla.org/pub/opus/opus-{self.version}.tar.gz")

    def build(self):
        args = [
            "--disable-shared",
        ]
        self.autotools(args)
