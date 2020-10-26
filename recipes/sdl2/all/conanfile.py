
from build import *


class Sdl2Recipe(Recipe):
    description = "A library for portable low-level access to a video framebuffer, audio output, mouse, and keyboard"
    license = "MIT"
        requires = (
        "base/[^1.0.0]",
        "libxcb/[^1.13.1]",
        "libxext/[^1.3.4]",
    )

    def source(self):
        self.get(f"https://www.libsdl.org/release/SDL2-{self.version}.tar.gz")