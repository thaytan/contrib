from build import *


class LibtiffRecipe(Recipe):
    description = "Library for manipulation of TIFF images"
    license = "custom"
    build_requires = (
        "autotools/[^1.0.0]",
        "mesa/20.0.0",
    )
    requires = (
        "zlib/[^1.2.11]",
        "libjpeg-turbo/[^2.0.4]",
    )

    def source(self):
        self.get(f"https://download.osgeo.org/libtiff/tiff-{self.version}.tar.gz")
