// Copyright (C) <2019> Aivero
//
// This library is free software; you can redistribute it and/or
// modify it under the terms of the GNU Library General Public
// License as published by the Free Software Foundation; either
// version 2 of the License, or (at your option) any later version.
// This library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
// Library General Public License for more details.
// You should have received a copy of the GNU Library General Public
// License along with this library; if not, write to the
// Free Software Foundation, Inc., 51 Franklin St, Fifth Floor,
// Boston, MA 02110-1301, USA.

// Framerate
pub(crate) const MIN_FRAMERATE: i32 = 6;
pub(crate) const MAX_FRAMERATE: i32 = 90;

// Resolution of depth, infra1 and infra2 streams
pub(crate) const DEPTH_MIN_WIDTH: i32 = 424;
pub(crate) const DEPTH_MAX_WIDTH: i32 = 1280;
pub(crate) const DEPTH_MIN_HEIGHT: i32 = 240;
pub(crate) const DEPTH_MAX_HEIGHT: i32 = 720;

// Resolution of color stream
pub(crate) const COLOR_MIN_WIDTH: i32 = 320;
pub(crate) const COLOR_MAX_WIDTH: i32 = 1920;
pub(crate) const COLOR_MIN_HEIGHT: i32 = 180;
pub(crate) const COLOR_MAX_HEIGHT: i32 = 1080;

// Supported formats
// pub(crate) const SUPPORTED_FRAMERATE: [i32; 5] = [6, 15, 30, 60, 90];
// pub(crate) const DEPTH_SUPPORTED_WIDTH: [i32; 6] = [424, 480, 640, 640, 848, 1280];
// pub(crate) const DEPTH_SUPPORTED_HEIGHT: [i32; 6] = [240, 270, 360, 480, 480, 720];
// pub(crate) const COLOR_SUPPORTED_WIDTH: [i32; 9] = [320, 320, 424, 640, 640, 848, 960, 1280, 1920];
// pub(crate) const COLOR_SUPPORTED_HEIGHT: [i32; 9] = [180, 240, 240, 360, 480, 480, 540, 720, 1080];
