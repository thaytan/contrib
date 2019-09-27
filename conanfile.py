from conans import ConanFile, AutoToolsBuildEnvironment, tools

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "4.1"
    except:
        return None

class FFMpegConan(ConanFile):
    name = "ffmpeg"
    version = get_version()
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "A complete, cross-platform solution to record, convert and stream audio and video"
    license = "GPL3"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def build_requirements(self):
        self.build_requires("yasm/[>=1.3.0]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)

    def source(self):
        tools.get("http://ffmpeg.org/releases/ffmpeg-%s.tar.bz2" % self.version)

    def build(self):
        args = [
            "--disable-doc",
            "--disable-programs"
        ]
        if self.settings.build_type == "Debug":
            args.extend(["--disable-optimizations", "--disable-mmx", "--disable-stripping", "--enable-debug"])
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")
