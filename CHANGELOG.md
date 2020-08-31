# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased
### Fixed

- Timestamps in GAP events - use proper timestamps instead of current running time.
- Fix incorrect computation of the frame duration for GAP event.

## [0.5.1] - 2020-08-21
### Changed

- Fall back to the default pad event handling - fixes EOS not being forwarded correctly in ~50% if cases. Credit to @slomo for the fix.

## [0.5.0] - 2020-07-22

### Changed

- Re-implemented the stream-id generation on rgbddemux, so that it follows the GStreamer
documentation:

> The stream_id should be a unique string that consists of the upstream stream-id, / as separator
> and a unique stream-id for this specific stream. A new stream-id should only be created for a
> stream if the upstream stream is split into (potentially) multiple new streams, e.g. in a demuxer,
> but not for every single element in the pipeline.

## [0.4.1] - 2020-07-01
### Changed
- Add gstreamer conan config, bump cargo deps to gst-depth-meta-rs

## [0.4.0] - 2020-04-07
### Changed
- Update dependencies
  - `glib` to 0.9
  - `gst` to 0.15

## 0.3.1 - 2020-04-02

### Fixed
- `rgbdmux` - Fixed EOS forwarding by implementing custom `sink_event()` handling.
- `rgbdmux` - No longer tries to renegotiate CAPS once EOS was received and the element is shutting down.

## 0.3.0 - 2020-03-10

### Added
- `rgbddemux` - Added `distribute-timestamps` property that enables distribution of the main buffer timestamps to the auxiliary buffers embedded within the `video/rbgd` stream. The property defaults to *false* and must be explicitly enabled to cause any difference from the previous version.


## 0.2.3 - 2020-03-04

### Modified
- Use of standard function for work with `video/rgbd` CAPS from `gst_depth_meta::rgbd` module, instead of custom-local implementation.


## 0.2.2 - 2020-01-28

### Added
- Support for MJPG


## 0.2.1 - 2020-01-24

### Added
- `rgbdmux` - CAPS negotiation of video formats with downstream element, conversion of these formats from `video/rgbd` to `video/x-raw` and subsequent use of the requested formats during creation of new sink pads.


## 0.2.0 - 2020-01-21

### Removed

- Partial KLV packing. `rgbddemux` now forwards the buffers simply as Cap'n Proto serialised buffers

### Changed

- `rgbddemux` and `rgbdmux` now treats per-frame metadata as top-level streams. This means that they're also included in the `streams` field of the `video/rgbd` CAPS.


## 0.1.6

### Added
- `rgbdmux` - If `drop-if-missing` is set to false, there is no deadline for the aggregation. This makes deadline based aggregation optional. If `drop-if-missing` is set to true, the behaviour is identical to `0.1.5`.
- `rgbdmux` - Added `deadline-multiplier` property that controls the duration of deadline if `drop-if-missing` is enabled.

### Changed
- `rgbdmux` - Split `internals` into `sink_pads` and `settings` to avoid the possibility of deadlock caused by Mutex, which was introduced by the new additions.


## 0.1.5

### Added
- `rgbdmux` - Dropping of all other frames if one of the sink pads does not have a buffer queued, see property `drop-if-missing`.
- `rgbdmux` - Synchronisation of buffers by dropping buffers that are late, see property `drop-to-synchronise`.


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
