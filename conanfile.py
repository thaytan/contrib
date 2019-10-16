from glob import glob
from os import environ, listdir, makedirs, path, pathsep, remove
from shutil import copy, copyfileobj, rmtree

from conans import ConanFile
from conans.model import Generator


def replace_prefix_in_pc_file(pc_file, prefix):
    with open(pc_file) as f:
        old_prefix = ""
        # Get old prefix
        for l in f:
            if "prefix=" in l:
                old_prefix = l.split("=")[1][:-1]
                break
        f.seek(0)
        if not old_prefix:
            for l in f:
                if "libdir=" in l:
                    old_prefix = l.split("=")[1][:-1]
                    break

        f.seek(0)
        content = f.read().replace(old_prefix, prefix)
    with open(pc_file, "w") as f:
        f.write(content)


def env_prepend(var, val, sep=pathsep):
    environ[var] = val + (sep + environ[var] if var in environ else "")


def remove_folder(folder):
    if path.isdir(folder):
        rmtree(folder)


class env(Generator):
    def __init__(self, conanfile):
        super().__init__(conanfile)
        self.env = conanfile.env

    @property
    def filename(self):
        return "env.sh"

    @property
    def content(self):
        conanfile = self.conanfile
        pc_output_path = self.output_path
        if not path.isdir(pc_output_path):
            makedirs(pc_output_path)

        # Replace package method
        if hasattr(conanfile, "package"):
            conanfile.pre_package = conanfile.package

        def package():
            # Run original package method
            if hasattr(conanfile, "pre_package"):
                conanfile.pre_package()
            # Copy sources to package
            if conanfile.settings.build_type == "Debug":
                for ext in ("c", "cpp", "cpp", "h", "hpp", "hxx"):
                    conanfile.copy("*." + ext, "src")

            # Delete libtool files
            for f in glob(
                path.join(conanfile.package_folder, "**", "*.la"), recursive=True
            ):
                remove(f)

            # Delete unneeded folders in share
            for folder in ("man", "doc", "gdb", "bash-completion", "gtk-doc"):
                remove_folder(path.join(conanfile.package_folder, "share", folder))

            # Fix shebangs
            if path.isdir(path.join(conanfile.package_folder, "bin")):
                for exe_name in listdir(path.join(conanfile.package_folder, "bin")):
                    exe_path = path.join(conanfile.package_folder, "bin", exe_name)
                    if path.isdir(exe_path):
                        continue
                    try:
                        exe = open(exe_path, "r")
                        line = exe.readline()
                        if "python" in line:
                            interpreter = "python"
                        elif "perl" in line:
                            interpreter = "perl"
                        elif "sh" in line:
                            interpreter = "sh"
                        else:
                            interpreter = None
                        line = "#!/usr/bin/env %s\n" % interpreter
                        to_exe = open(exe_path, mode="w")
                        to_exe.write(line)
                        copyfileobj(exe, to_exe)
                        exe.close()
                        to_exe.close()
                    except UnicodeDecodeError:
                        pass

        conanfile.package = package

        # Copy pc files from PKG_CONFIG_SYSTEM_PATH
        if hasattr(conanfile, "system_pcs") and "PKG_CONFIG_SYSTEM_PATH" in environ:
            if isinstance(conanfile.system_pcs, str):
                system_pcs = set([conanfile.system_pcs])
            else:
                system_pcs = set(conanfile.system_pcs)
            for pc_path in environ["PKG_CONFIG_SYSTEM_PATH"].split(pathsep):
                for pc in listdir(pc_path):
                    if path.splitext(pc)[0] in conanfile.system_pcs:
                        system_pcs.remove(path.splitext(pc)[0])
                        copy(path.join(pc_path, pc), pc_output_path)
            if len(system_pcs):
                raise Exception(
                    "'%s' not available in system pkg-config directories"
                    % ", ".join(system_pcs)
                )

        # Find bin, lib and pkgconfig paths
        bin_paths = []
        lib_paths = []
        prefix_paths = []
        for _, cpp_info in self.deps_build_info.dependencies:
            prefix_paths.append(cpp_info.rootpath)
            lib_path = path.join(cpp_info.rootpath, "lib")
            if path.isdir(lib_path):
                lib_paths.append(lib_path)
            bin_path = path.join(cpp_info.rootpath, "bin")
            if path.isdir(bin_path):
                bin_paths.append(bin_path)
            pc_lib_path = path.join(cpp_info.rootpath, "lib", "pkgconfig")
            pc_share_path = path.join(cpp_info.rootpath, "share", "pkgconfig")
            if path.isdir(pc_lib_path):
                for pc in listdir(pc_lib_path):
                    copy(path.join(pc_lib_path, pc), pc_output_path)
                    replace_prefix_in_pc_file(
                        path.join(pc_output_path, pc), cpp_info.rootpath
                    )
            if path.isdir(pc_share_path):
                for pc in listdir(pc_share_path):
                    copy(path.join(pc_share_path, pc), pc_output_path)
                    replace_prefix_in_pc_file(
                        path.join(pc_output_path, pc), cpp_info.rootpath
                    )

        # Update Conan environment
        env_prepend("PATH", pathsep.join(bin_paths))
        env_prepend("LD_LIBRARY_PATH", pathsep.join(lib_paths))
        env_prepend("PKG_CONFIG_PATH", pc_output_path)
        env_prepend("CMAKE_PREFIX_PATH", pathsep.join(prefix_paths))
        if hasattr(conanfile, "source_folder"):
            env_prepend(
                "CFLAGS", "-fdebug-prefix-map=%s=." % conanfile.source_folder, " "
            )
            env_prepend(
                "CXXFLAGS", "-fdebug-prefix-map=%s=." % conanfile.source_folder, " "
            )

        # Generate env.sh
        content = 'export PATH=%s:"$PATH"\n' % pathsep.join(
            '"%s"' % p for p in bin_paths
        )
        content += 'export LD_LIBRARY_PATH=%s:"$LD_LIBRARY_PATH"\n' % pathsep.join(
            '"%s"' % p for p in lib_paths
        )
        content += 'export PKG_CONFIG_PATH="%s":"$PKG_CONFIG_PATH"\n' % pc_output_path
        content += 'export CMAKE_PREFIX_PATH=%s:"$CMAKE_PREFIX_PATH"\n' % pathsep.join(
            '"%s"' % p for p in prefix_paths
        )
        content += 'export SOURCE_PATH=%s:"$SOURCE_PATH"\n' % pathsep.join(
            '"%s"' % p for p in path.join(prefix_paths, "src") if path.isdir(p)
        )
        for var, val in self.env.items():
            if type(val) is list:
                content += 'export {0}={1}:"${0}"\n'.format(
                    var, pathsep.join('"%s"' % p for p in val)
                )
            else:
                content += "export {0}={1}\n".format(var, '"%s"' % val)

        return content


class EnvPackage(ConanFile):
    name = "env-generator"
    version = "1.0.0"
    url = "https://gitlab.com/aivero/public/tools/conan-env-generator"
    license = "MIT"
    description = "Generator for combined build and runtime environment file"
