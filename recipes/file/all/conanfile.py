from build import *


class FileRecipe(Recipe):
    description = "File type identification utility"
    license = "custom"

    def source(self):
        self.get(f"https://astron.com/pub/file/file-{self.version}.tar.gz")

    def build(self):
        args = [
            "--disable-shared",
            "--disable-dependency-tracking",
        ]
        self.autotools(args)
