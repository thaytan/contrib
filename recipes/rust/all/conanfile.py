from build import *


class RustRecipe(Recipe):
    description = "Virtual rust package"
    license = "MIT"
    settings = Recipe.settings + ("rust",)

    def requirements(self):
        # Rust is not compatible between releases
        self.requires(f"rustc/[~{self.settings.rust}]")
