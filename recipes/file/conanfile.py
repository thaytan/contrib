from build import *


class FileRecipe(Recipe):
    description = "File type identification utility"
    license = "custom"

    def source(self):
        self.get(f"http://astron.com/pub/file/file-{self.version}.tar.gz")

    def package_info(self):
        self.env_info.MAGIC = os.path.join(self.package_folder, "share", "misc", "magic.mgc")