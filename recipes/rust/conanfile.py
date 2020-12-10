from build import *


class RustRecipe(RustRecipe):
    description = "Virtual rust package"
    license = "MIT"
    requires = (
        "sccache/[^0.2.13]",
        "pkgconf/[^1.7.3]",
    )

    def requirements(self):
        # Rust is not compatible between major or minor releases
        self.requires(f"rustc/[~{self.settings.rust}]")
