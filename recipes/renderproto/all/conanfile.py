from build import *


class RenderprotoRecipe(Recipe):
    description = "X11 Render extension wire protocol"
    license = "MIT"
    build_requires = ("autotools/[^1.0.0]",)

    def source(self):
        self.get(f"https://xorg.freedesktop.org/releases/individual/proto/renderproto-{self.version}.tar.gz")
        with tools.chdir(f"{self.name}-{self.version}"):
            os.remove("config.guess")
            os.remove("config.sub")
            tools.download("http://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.guess;hb=HEAD", "config.guess")
            tools.download("http://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.sub;hb=HEAD", "config.sub")
