/// Enabling of streams
pub const DEFAULT_ENABLE_DEPTH: bool = true;
pub const DEFAULT_ENABLE_INFRA1: bool = false;
pub const DEFAULT_ENABLE_INFRA2: bool = false;
pub const DEFAULT_ENABLE_COLOR: bool = false;

/// Framerate
pub const MIN_FRAMERATE: i32 = 6;
pub const MAX_FRAMERATE: i32 = 90;
pub const DEFAULT_FRAMERATE: i32 = 30;
// pub const SUPPORTED_FRAMERATE: [i32; 5] = [6, 15, 30, 60, 90];

/// Resolution of depth, infra1 and infra2 streams
pub const DEPTH_MIN_WIDTH: i32 = 424;
pub const DEPTH_MAX_WIDTH: i32 = 1280;
pub const DEFAULT_DEPTH_WIDTH: i32 = 1280;
// pub const DEPTH_SUPPORTED_WIDTH: [i32; 6] = [424, 480, 640, 640, 848, 1280];
pub const DEPTH_MIN_HEIGHT: i32 = 240;
pub const DEPTH_MAX_HEIGHT: i32 = 720;
pub const DEFAULT_DEPTH_HEIGHT: i32 = 720;
// pub const DEPTH_SUPPORTED_HEIGHT: [i32; 6] = [240, 270, 360, 480, 480, 720];

/// Resolution of color stream
pub const COLOR_MIN_WIDTH: i32 = 320;
pub const COLOR_MAX_WIDTH: i32 = 1920;
pub const DEFAULT_COLOR_WIDTH: i32 = 1280;
// pub const COLOR_SUPPORTED_WIDTH: [i32; 9] = [320, 320, 424, 640, 640, 848, 960, 1280, 1920];
pub const COLOR_MIN_HEIGHT: i32 = 180;
pub const COLOR_MAX_HEIGHT: i32 = 1080;
pub const DEFAULT_COLOR_HEIGHT: i32 = 720;
// pub const COLOR_SUPPORTED_HEIGHT: [i32; 9] = [180, 240, 240, 360, 480, 480, 540, 720, 1080];
