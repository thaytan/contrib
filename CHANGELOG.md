# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.4] - 2020-Sep-07
### Changed
- Set dependency of `rgbd-timestamps` to a separate shared library (separate from `gstreamer-depth-meta-rs`), such that `GstTimestampMode` gets registered only once.

## [2.2.3] - 2020-Sep-02
### Changed
- Update to GStreamer bindings to version 0.16.

## [2.2.2] - 2020-Aug-24
### Changed
- Bump version of librealsense-rs to 2.2.3

## [2.2.1] - 2020-Jul-14
### Changed
- Bump version of librealsense-rs to 2.2.2

## [2.2.0] - 2020-Jul-10

## Added
- Printing of CameraMeta (intrinsics, extrinsics and depth scale) to GST_INFO.
- Printing of more detailed error messages when either serial or resolution+framerate is invalid. Implemented with ConfigError enum.

## [2.1.4] - 2020-Jul-01
## Fixed
- Implement latency query handling.

## [2.1.3] - 2020-Jul-01
### Changed
- Add gstreamer conan settings, add plugins-base with deps on it.

## [2.1.2] - 2020-May-26
### Changed
- Use new version of gstreamer-depth-meta - 1.2.0
- Use new version of librealsense-rs - 2.1.0
- Update readme

## [2.1.1] - 2020-Apr-28
### Changed
- Use new version of gstreamer-depth-meta - 1.0.1

## [2.1.0] - 2020-Apr-02
### Added
- Accept "~/path/to/file", i.e. tilde as $HOME, while setting `rosbag-location` and `json-location`.
### Changed
- Update dependencies
  - `glib` to 0.9
  - `gst` to 0.15

## [2.0.0] - 2020-Apr-02

### Changed

- Use implementation of standard `RgbdTimestamps` trait instead of custom timestamping. This introduces different variants for `timestamp-mode` property.
- Default value for `loop-rosbag` is now *false*.


## [1.2.1] - 2020-Mar-27

### Fixed

- Updated librealsense-rs to newest version (2.0.0) in cargo.toml.


## [1.2.0] - 2020-Mar-04

### Added
- Implemented attaching of camera meta containing intrinsics, extrinsics and depth scale. This functionality can be enabled by `attach-camera-meta` property.

### Modified
- Use of standard function for work with `video/rgbd` CAPS from `gst_depth_meta::rgbd` module, instead of custom-local implementation.


## [1.1.0] - 2020-Feb-18

### Added
- Explicitly call `rs2::Config::resolve()` before starting the pipeline in order to speed up returning of errors if `Config` cannot be resolved.

### Changed
- Behaviour for setting both `serial` and `rosbag-location`.
  - Print an informative error stating that only one of these can be specified.
  - Terminate when both `serial` and `rosbag-location` are specified.


## [1.0.1] - 2020-Jan-29

### Fixed

- Properly set live-mode based on `real-time-rosbag-playback` property when playing from ROSBAG.

## [1.0.0] - 2020-Jan-21

### Added

- `timestamp-mode` property, which can have values *default*, *all-buffers* or *rs2*. This replaces `do-rs2-timestamp` and `do-custom-timestamp`.

### Removed

- `do-rs2-timestamp` property
- `do-custom-timestamp` property

### Changed

- `realsensesrc` now includes per-frame metadata buffers as top-level buffers. This means that the per-frame metadata buffers of all streams are attached as `BufferMeta` onto the main buffer.

## [0.1.9] - 2020-Jan-03

### Changed

- Updated rust compiler from 1.38.0 to 1.40.0

### Patched

- `realsensesrc` now correctly sets the LIVE-mode to false when playing from ROSBAG.

## [0.1.8] - 2019-Dec-20

### Changed

- `do-rs2-timestamp` now defaults to `false`, as it proved troublesome. It is thus treated as an advanced options from now on.

## [0.1.7] - 2019-Dec-12

### Added
- `do-rs2-timestamp` property that stamps all buffers with timestamps from `librealsense`, starting from 0 and monotomically increasing. If enabled, this property has higher priority than `do-custom-timestamp`. If used in combination with playing back from rosbag, make sure that property `loop-rosbag=false`. If set to false, behaviour is identical to previous versions.
- `real-time-rosbag-playback` property that makes playback from rosbag behave as a real-time live source. If set to false, playback from rosbag is independent from real-time and allows arbitrary rate of playback, if downstream element(s) have `sync=false`. If set to true, behaviour is identical to previous versions.


## [0.1.6] - 2019-Nov-13

### Added
- Fixed issues related to playback from rosbag recording.
  - Streams no longer loop if not all streams contained within rosbag are enabled.
  - The resolution and framerate gets updated from rosbag recording if there is a conflict with settings.
  - Helpful error is thrown while enabling a stream that is not available.
### Modified
- Use version 0.6.0 of `librealsense-rs`
  - Change `String` to `&str` for some of the `Config` and `Device` method calls.
  - Rename certain deprecated method so that these are identical to C/C++ API.
- Moved 4 booleans, i.e. `enable_x`, under `EnabledStreams` as the new code benefits from it.
- Use `StreamResolution` struct definition from `librealsense-rs` instead of a local copy of it.
- Split structs into multiple files, i.e. create `enabled_streams.rs`, `settings.rs`, `errors.rs` and `properties.rs`.
### Patched
- Also set timestamp and buffer duration on per-frame metadata buffers.


## [0.1.5] - 2019-Oct-30
### Patched
- Set duration on buffers to remove the `missing offset_end` warnings
- Also set timestamp and buffer duration on per-frame metadata buffers.
- Fix git dependencies in cargo.toml to the relevant tags

## [0.1.4] - 2019-Oct-17
### Added
- `do-custom-timestamp` property to `realsensesrc`
### Modified
- The way in which timestamps are computed

## [0.1.3] - 2019-Sep-25
### Added
- Custom timestamps

## [0.1.0] - 2019-Sep-19
### Added
- `include-per-frame-metadata` property to `realsensesrc`
- CapnProto serialized metadata

## [0.1.0]
### Added
- Prior to 0.1.1 this repository did not have a changelog.
