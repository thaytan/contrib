import os
from datetime import datetime

from conans import ConanFile, tools

def get_version():
    try:
        git = tools.Git()
        tag, branch = git.get_tag(), git.get_branch()
        return tag if tag and branch.startswith("HEAD") else branch
    except:
        return None


def make_cargo_version(version_string):
    try:
        version = tools.Version(version_string, loose=False)
        return "%d.%d.%d" % (version.major, version.minor, version.patch)
    except:
        return "0.0.0-nottagged"


class GstreamerFrameAlignerConan(ConanFile):
    name = "gstreamer-frame-aligner"
    version = get_version()
    license = "Proprietary"
    author = "João Alves <joao.alves@aivero.com>"
    url = ""
    description = "Gstreamer align frames utilities"
    topics = ("rgbd", "Gstreamer")
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = [
        "Cargo.toml",
        "src/*",
        "calib/*",  # TODO: This needs to be replaced with pipeline metadata
    ]

    def source(self):
        # Override the version supplied to GStreamer, as specified in lib.rs
        tools.replace_path_in_file(file_path="src/lib.rs", search="\"2017-12-01\"", replace=("\"%s\"" % datetime.now().strftime("%Y-%m-%d")))
        # Override the package version defined in the Cargo.toml file
        tools.replace_path_in_file(file_path="Cargo.toml",
                                   search=("[package]\nname = \"%s\"\nversion = \"0.0.0-ohmyconanpleaseoverwriteme\"" % self.name),
                                   replace=("[package]\nname = \"%s\"\nversion = \"%s\"" % (self.name, make_cargo_version(self.version))))

    def build_requirements(self):
        self.build_requires("generators/[>=1.0.0]@%s/stable" % self.user)
        self.build_requires("rust/[>=1.40.0]@%s/stable" % self.user)
        self.build_requires("sccache/[>=0.2.12]@%s/stable" % self.user)
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % self.user)

    def requirements(self):
        self.requires("gstreamer-depth-meta/[>=0.2.0]@%s/stable" % self.user)

    def build(self):
        if self.settings.build_type == 'Release':
            self.run("cargo build --release")
        elif self.settings.build_type == 'Debug':
            self.run("cargo build")
        else:
            self.output.error('Invalid build_type selected')

    def package(self):
        self.copy(pattern="*.so", dst=os.path.join(self.package_folder, "lib", "gstreamer-1.0"), keep_path=False)
        self.copy(pattern="calib/*", dst=os.path.join(self.package_folder, "calib"), keep_path=False)

    def package_info(self):
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
