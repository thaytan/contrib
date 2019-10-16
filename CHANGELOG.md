# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.1.3

### Added
- Metadata support: The `rgbdmux` reads per-frame metadata on the frame buffers and pushes them to a sink-pad called *dddqmeta*. Similarly, if the rgbd CAPS contains a stream called *dddqmeta*, its content is also outputted on the *dddqmeta* sink.

### Patched
- This patch fixes a bug introduces in 0.1.2 which caused the rgbddemux to return a gst::FlowError when it attempts to push meta buffer for which it does not have a pad.

## Before
Prior to 0.1.2 this repository did not have a changelog.

