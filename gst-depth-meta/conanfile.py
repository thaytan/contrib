from build import *

class GstDepthMeta(GstProject):
    license = "Apache"
    description = "Library to stream depth video"
    exports_sources = (
        "CMakeLists.txt", 
        "src/*"
    )
    build_requires = (
        "cc/[^1.0.0]",
        "cmake/[^3.18.4]"
    )
    requires = (
        "gst-plugins-base/[^1.18]"
    )

    def build(self):
        os.environ["CONAN_BRANCH"] = branch()
        self.cmake()