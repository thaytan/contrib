from build import *


class ZlibRecipe(Recipe):
    description = "A Massively Spiffy Yet Delicately Unobtrusive Compression Library (Also Free, Not to Mention Unencumbered by Patents)"
    license = "Zlib"
    build_requires = ("make/[^4.3]",)

    def source(self):
        self.get(f"https://github.com/madler/zlib/archive/v{self.version}.tar.gz")

    def build(self):
        args = [
            "--static",
        ]
        self.autotools(args)

    def package_info(self):
        self.env_info.CPATH.append(os.path.join(self.package_folder, "include"))
