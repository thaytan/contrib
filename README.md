[![Download](https://api.bintray.com/packages/bincraters/public-conan/yasm_installer%3Abincraters/images/download.svg) ](https://bintray.com/bincraters/public-conan/yasm_installer%3Abincraters/_latestVersion)
[![Build Status](https://travis-ci.org/bincraters/conan-yasm_installer.svg?branch=testing%2F1.3.0)](https://travis-ci.org/bincraters/conan-yasm_installer)
[![Build status](https://ci.appveyor.com/api/projects/status/github/bincraters/conan-yasm_installer?branch=testing%2F1.3.0&svg=true)](https://ci.appveyor.com/project/bincraters/conan-yasm_installer)

[Conan.io](https://conan.io) package recipe for *yasm_installer*.

Yasm is a complete rewrite of the NASM assembler under the “new” BSD License

The packages generated with this **conanfile** can be found on [Bintray](https://bintray.com/bincraters/public-conan/yasm_installer%3Abincraters).

## For Users: Use this package

### Basic setup

    $ conan install yasm_installer/1.3.0@bincraters/testing

### Project setup

If you handle multiple dependencies in your project is better to add a *conanfile.txt*

    [requires]
    yasm_installer/1.3.0@bincraters/testing


Complete the installation of requirements for your project running:

    $ mkdir build && cd build && conan install ..

Note: It is recommended that you run conan install from a build directory and not the root of the project directory.  This is because conan generates *conanbuildinfo* files specific to a single build configuration which by default comes from an autodetected default profile located in ~/.conan/profiles/default .  If you pass different build configuration options to conan install, it will generate different *conanbuildinfo* files.  Thus, they should not be added to the root of the project, nor committed to git.

## For Packagers: Publish this Package

The example below shows the commands used to publish to bincraters conan repository. To publish to your own conan respository (for example, after forking this git repository), you will need to change the commands below accordingly.

## Build and package

The following command both runs all the steps of the conan file, and publishes the package to the local system cache.  This includes downloading dependencies from "build_requires" and "requires" , and then running the build() method.

    $ conan create bincraters/testing



## Add Remote

    $ conan remote add bincraters "https://api.bintray.com/conan/bincraters/public-conan"

## Upload

    $ conan upload yasm_installer/1.3.0@bincraters/testing --all -r bincraters


## Conan Recipe License

NOTE: The conan recipe license applies only to the files of this recipe, which can be used to build and package yasm_installer.
It does *not* in any way apply or is related to the actual software being packaged.

[LICENSE](https://github.com/bincrafters/conan-yasm_installer.git/blob/testing/1.3.0/LICENSE.md)
