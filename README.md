# gst-k4a

GStreamer plugin containing `video/rgbd` source for an Azure Kinect DK (K4A) device.

> Note: Streaming from IMU is currently not implemented

## `video/rgbd`
The `video/rgbd` caps always contain the following fields
- **streams** - This field contains selected streams with priority `depth > ir > color > imu`. The first stream in this comma separated string, e.g. "depth,infra2,color", is considered to be the main stream and is therefore transported in the main buffer. There must always be at least one stream enabled. All additional buffers are attached as meta to the main buffer.
- **%s_format** - Format for each selected stream, e.g. depth_format="Gray16Le".
- **%s_width** - Width for each selected stream, e.g. depth_width=1280.
- **%s_height** - Height for each selected stream, e.g. depth_height=720.
- **framerate** - Common framerate for all selected streams.
