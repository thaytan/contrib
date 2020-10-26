from build import *


class CapNProtoRecipe(Recipe):
    description = "Cap'n Proto serialization/RPC system"
    license = "MIT"
    build_requires = (
        "cmake/[^3.18.3]",
        "zlib/[^1.2.11]",
    )

    def source(self):
        self.get(f"https://github.com/capnproto/capnproto/archive/v{self.version}.tar.gz")

    def build(self):
        defs = {
            "BUILD_SHARED_LIBS": True,
        }
        self.cmake(defs)
