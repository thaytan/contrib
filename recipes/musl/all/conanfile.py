import os

from conans import *

MUSL_CLANG = """#!/usr/bin/env sh
# prevent clang from running the linker (and erroring) on no input.
sflags=
eflags=
for x ; do
    case "$x" in
        -l*) input=1 ;;
        *) input= ;;
    esac
    if test "$input" ; then
        sflags="-l-user-start"
        eflags="-l-user-end"
        break
    fi
done

exec clang \
    -fuse-ld=musl-clang \
    -static-libgcc \
    -nostdinc \
    --sysroot "$MUSL_SYSROOT" \
    -isystem "$MUSL_INCLUDE_PATH" \
    -L-user-start \
    $sflags \
    "$@" \
    $eflags \
    -L"$MUSL_LIBRARY_PATH" \
    -L-user-end
"""

MUSL_CLANGPP = """#!/usr/bin/env sh
# prevent clang from running the linker (and erroring) on no input.
sflags=
eflags=
for x ; do
    case "$x" in
        -l*) input=1 ;;
        *) input= ;;
    esac
    if test "$input" ; then
        sflags="-l-user-start"
        eflags="-l-user-end"
        break
    fi
done

exec clang++ \
    -fuse-ld=musl-clang \
    -nostdinc \
    -nostdlib++ \
    --sysroot "$MUSL_SYSROOT" \
    -isystem "$MUSL_INCLUDE_PATH" \
    -L-user-start \
    $sflags \
    "$@" \
    $eflags \
    -L"$MUSL_LIBRARY_PATH" \
    -L-user-end
"""


class MuslConan(ConanFile):
    description = "Lightweight implementation of C standard library"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("linux-headers/[^5.4.50]",)

    def source(self):
        tools.get(f"https://www.musl-libc.org/releases/musl-{self.version}.tar.gz")

    def build(self):
        arch = {"x86_64": "x86_64", "armv8": "aarch64"}[str(self.settings.arch_build)]
        vars = {
            "TARGET": f"{arch}-linux-musl",
            "LIBCC": "-lcompiler_rt",
            "CFLAGS": os.environ["CFLAGS"],
        }
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"musl-{self.version}", vars=vars)
        autotools.make()
        autotools.install()
        with tools.chdir(os.path.join(self.package_folder, "bin")):
            os.symlink(os.path.join("..", "lib", "libc.so"), "ldd")
        with tools.chdir(os.path.join(self.package_folder, "lib")):
            os.symlink(os.path.join("..", "lib", "libc.so"), f"ld-musl-{arch}.so.1")

        with open("musl-clang", "w") as pc:
            pc.write(MUSL_CLANG)
        os.chmod("musl-clang", 0o775)
        with open("musl-clang++", "w") as pc:
            pc.write(MUSL_CLANGPP)
        os.chmod("musl-clang++", 0o775)

    def package(self):
        self.copy("musl-clang*", dst="bin", keep_path=False)

    def package_info(self):
        self.env_info.MUSL_SYSROOT = self.package_folder
        self.env_info.MUSL_LIBRARY_PATH = os.path.join(self.package_folder, "lib")
        self.env_info.MUSL_INCLUDE_PATH = os.path.join(self.package_folder, "include")
