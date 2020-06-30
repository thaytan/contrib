import os

from conans import *

id = {"3.1.103": "4acde034-669e-4d98-86ac-6214ebb36ff9/7e3cf7e4c323840c49ad7c3e4e2c7755"}
id = {"3.1.201": "f65a8eb0-4537-4e69-8ff3-1a80a80d9341/cc0ca9ff8b9634f3d9780ec5915c1c66"}


class DotnetSdkConan(ConanFile):
    description = "The .NET Core SDK"
    license = "custom"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    )
    requires = (
        "generators/1.0.0",
    )

    def source(self):
        tools.get("https://download.visualstudio.microsoft.com/download/pr/%s/dotnet-sdk-%s-linux-x64.tar.gz" % (id[self.version], self.version))

    def package(self):
        self.copy("packs/*", dst="share")
        self.copy("sdk/*", dst="share")
        self.copy("shared/*", dst="share")
        self.copy("host/*", dst="share")
        self.copy("templates/*", dst="share")
        self.copy("dotnet", dst="share")
        os.mkdir(os.path.join(self.package_folder, "bin"))
        os.symlink(os.path.join(self.package_folder, "share", "dotnet"), os.path.join(self.package_folder, "bin", "dotnet"))

    def package_info(self):
        self.env_info.DOTNET_ROOT = os.path.join(self.package_folder, "share")
