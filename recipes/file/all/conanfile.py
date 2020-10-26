from build import *


class FileRecipe(Recipe):
    description = "File type identification utility"
    license = "custom"

    def source(self):
        self.get(f"http://astron.com/pub/file/file-{self.version}.tar.gz")
