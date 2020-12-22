from build import *


class GstPerfRecipe(Recipe):
    description = "Performance Evaluation tool for Gstreamer"
    license = "LGPL"
    build_requires = (
        "cc/[^1.0.0]",
        "autotools/[^1.0.0]",
        "automake/[^1.16.1]",
        "autoconf/[^2.69]",
    )
    requires = (
        "glib/[^2.62.0]",
        "gst/[^1.18.1]",
    )

    def source(self):
        git = tools.Git()
        git.clone("https://github.com/RidgeRun/gst-perf.git", f"v{self.version}")

    def package(self):
        self.copy(pattern="*.so", dst=os.path.join(self.package_folder, "lib", "gstreamer-1.0"), keep_path=False)

