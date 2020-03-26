# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2020-03-25
### Added
- Implemented `RgbdTimestamps` trait.
### Changed
- Organised project into submodules.

## [0.3.1] - 2020-03-10
### Fixed
- Make `rgbd::get_aux_buffers_mut()` return writable buffers by utilising `gst::Buffer::from_glib_borrow()` instead of `gst::Buffer::from_glib_none()`.

## [0.3.0] - 2020-03-04
### Added
- Implemented serialisation of CameraMeta by the use of Cap'n Proto.
- Module `rgbd` that contains commonly used function for work with `video/rgbd` CAPS.

## [0.1.0] - Prior to 2019-10-21
Before [0.1.1] this project did not have a changelog.
