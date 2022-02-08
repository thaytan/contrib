from build import *


class File(Recipe):
    description = "File type identification utility"
    license = "custom"
    build_requires = (
        "zig-bootstrap/[^0.9.0]",
    )

    def source(self):
        self.get(f"http://astron.com/pub/file/file-{self.version}.tar.gz")

    def package_info(self):
        self.env_info.MAGIC = os.path.join(self.package_folder, "share", "misc", "magic.mgc")