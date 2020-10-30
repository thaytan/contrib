from build import *


class OpusRecipe(Recipe):
    description = "Modern audio compression for the internet"
    license = "BSD"
    build_requires = (
        "cc/[^1.0.0]",
        "cmake/[^3.18.4]",
    )

    def source(self):
        # CMake broken until next release (https://github.com/xiph/opus/issues/129)
        self.get("https://github.com/xiph/opus/archive/86e5f5ea56529d688568929d036574a93311e82a.tar.gz")
