# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## 0.1.5

### Added
- `rgbdmux` - Optional deadline based aggregation, which results in dropping all other buffers if one of the sink pads does not have a buffer queued, see properties `drop-if-missing` and `deadline-multiplier`.
- `rgbdmux` - Synchronisation of buffers by dropping buffers that are late, see property `drop-to-synchronise`.

### Changed
- `rgbdmux` - Split `internals` into `sink_pads` and `settings` to avoid the possibility of deadlock caused by Mutex, which was introduced by the new additions.


## 0.1.4

### Added
- Metadata support: The `rgbddemux` reads per-frame metadata on the frame buffers and pushes them to a sink-pad called *dddqmeta*. Similarly, if the rgbd CAPS contains a stream called *dddqmeta*, its content is also outputted on the *dddqmeta* sink.

### Changed
- Peer elements may now request pads on the `rgbddemux`, which may be linked when CAPS are available
- `rgbdmux` does downstream CAPS negotiation when sink pads are requested on the element

### Known issues
- Requesting a pad on the `rgbddemux` which is not in the `video/rgbd` stream will cause the pipeline to freeze  


## 0.1.3

### Patched
- This patch fixes a bug introduces in 0.1.2 which caused the rgbddemux to return a gst::FlowError when it attempts to push meta buffer for which it does not have a pad.

## Before
Prior to 0.1.2 this repository did not have a changelog.

