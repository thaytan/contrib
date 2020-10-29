from build import *


class Bzip2Recipe(Recipe):
    description = "A high-quality data compression program"
    license = "custom"
    build_requires = (
        "cc/[^1.0.0]",
        "make/[^4.3]",
    )

    def source(self):
        self.get(f"https://sourceware.org/pub/bzip2/bzip2-{self.version}.tar.gz")

    def build(self):
        args = [
            f"PREFIX={self.package_folder}",
            "CC=cc",
        ]
        self.make(args)

    def package(self):
        with tools.chdir(os.path.join(self.package_folder, "bin")):
            for source, link in (
                ("bzdiff", "bzcmp"),
                ("bzgrep", "bzegrep"),
                ("bzgrep", "bzfgrep"),
                ("bzmore", "bzless"),
            ):
                os.remove(link)
                os.symlink(source, link)
