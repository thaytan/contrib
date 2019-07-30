// Properties and their corresponding ranges based on D435

// Framerate
pub const MIN_FRAMERATE: u32 = 6;
pub const MAX_FRAMERATE: u32 = 90;
pub const DEFAULT_FRAMERATE: u32 = 30;
// pub const SUPPORTED_FRAMERATE: [i32; 5] = [6, 15, 30, 60, 90];

// Depth
// This stream is always enabled
pub const DEPTH_MIN_WIDTH: u32 = 424;
pub const DEPTH_MAX_WIDTH: u32 = 1280;
pub const DEFAULT_DEPTH_WIDTH: u32 = 1280;
// pub const DEPTH_SUPPORTED_WIDTH: [u32; 6] = [424, 480, 640, 640, 848, 1280];

pub const DEPTH_MIN_HEIGHT: u32 = 240;
pub const DEPTH_MAX_HEIGHT: u32 = 720;
pub const DEFAULT_DEPTH_HEIGHT: u32 = 720;
// pub const DEPTH_SUPPORTED_HEIGHT: [u32; 6] = [240, 270, 360, 480, 480, 720];

// IR
pub const DEFAULT_ENABLE_INFRA_1: bool = false;
pub const DEFAULT_ENABLE_INFRA_2: bool = false;
// Resolution is identical with depth stream

// Color
pub const DEFAULT_ENABLE_COLOR: bool = false;

pub const COLOR_MIN_WIDTH: u32 = 320;
pub const COLOR_MAX_WIDTH: u32 = 1920;
pub const DEFAULT_COLOR_WIDTH: u32 = 1280;
// pub const COLOR_SUPPORTED_WIDTH: [u32; 9] = [320, 320, 424, 640, 640, 848, 960, 1280, 1920];

pub const COLOR_MIN_HEIGHT: u32 = 180;
pub const COLOR_MAX_HEIGHT: u32 = 1080;
pub const DEFAULT_COLOR_HEIGHT: u32 = 720;
// pub const COLOR_SUPPORTED_HEIGHT: [u32; 9] = [180, 240, 240, 360, 480, 480, 540, 720, 1080];
