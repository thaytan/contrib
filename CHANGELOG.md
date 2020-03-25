# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.0] - 2020-03-25

### Changed

- Use implementation of standard `RgbdTimestamps` trait instead of custom timestamping.

## [0.5.0] - 2020-03-04

### Added

- Implemented attaching of camera meta containing intrinsics, extrinsics and depth scale. This functionality can be enabled by `attach-camera-meta` property.

### Modified
- Use of standard function for work with `video/rgbd` CAPS from `gst_depth_meta::rgbd` module, instead of custom-local implementation.

### Fixed
- Setting of `framerate` and `timestamp-mode` properties.

## [0.4.0] - 2020-02-18

### Added

- Implemented rectification of depth, which can be enabled by `rectify-depth` property.

## [0.3.0] - 2020-02-18

### Changed

- Implemented `GEnum` properties for all enum-like int properties on the `k4asrc`.

## [0.2.0] - 2020-02-17

### Added

- Expand timestamping capabilities, i.e. `timestamp-mode` property that can take the following forms: `ignore`, `main`, `all`, `k4a_common` and `k4a_individual`
- Support for MJPG

### Modified

- Fix streaming from Playback.

## [0.1.0] - 2020-01-24

### Added

- First version of `k4asrc`
