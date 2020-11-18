# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2020-Nov-18

### Changed

- Updated dependencies for `gst-rgbd`, `gst-k4a`, `gst-realsense` and `gstreamer-colorizer`.
- Use temporary fix of registering timestamp mode for `gst-k4a` and `gst-realsense`.
  - TODO: Make sure to update these dependencies back to tagged release once we find a solution.

### Fixed

- Removed dependency for `libglvnd`, which causes problems with `glimagesink`.

## [1.7.0] - 2020-Aug-11

### Changed

- Updated dependencies for new release

## [1.6.0] - 2020-Aug-01

### Added

- docker examples for running RGB-D toolkit

## Before [1.6.0] this project did not have a changelog.
