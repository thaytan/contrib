from build import *


class DirenvRecipe(Recipe):
    description = "A shell extension that manages your environment"
    license = "MIT"
    build_requires = (
        "cc/[^1.0.0]",
        "go/[^1.15.3]",
        "make/[^4.3]",
    )

    def source(self):
        self.get(f"https://github.com/direnv/direnv/archive/v{self.version}.tar.gz")

    def build(self):
        os.environ["GOFLAGS"] = "-buildmode=pie -trimpath -mod=vendor -modcacherw"
        os.environ["DESTDIR"] = self.package_folder
        self.make()
