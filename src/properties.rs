// Framerate
pub const MIN_FRAMERATE: u32 = 6;
pub const MAX_FRAMERATE: u32 = 90;
pub const DEFAULT_FRAMERATE: u32 = 30;

// Depth
// This stream is always enabled
pub const DEPTH_MIN_WIDTH: u32 = 424;
pub const DEPTH_MAX_WIDTH: u32 = 1280;
pub const DEFAULT_DEPTH_WIDTH: u32 = 1280;

pub const DEPTH_MIN_HEIGHT: u32 = 240;
pub const DEPTH_MAX_HEIGHT: u32 = 720;
pub const DEFAULT_DEPTH_HEIGHT: u32 = 720;

// IR
pub const DEFAULT_ENABLE_INFRA_1: bool = false;
pub const DEFAULT_ENABLE_INFRA_2: bool = false;
// Resolution is identical with depth stream

// Color
pub const DEFAULT_ENABLE_COLOR: bool = true;

pub const COLOR_MIN_WIDTH: u32 = 320;
pub const COLOR_MAX_WIDTH: u32 = 1920;
pub const DEFAULT_COLOR_WIDTH: u32 = 1920;

pub const COLOR_MIN_HEIGHT: u32 = 180;
pub const COLOR_MAX_HEIGHT: u32 = 1080;
pub const DEFAULT_COLOR_HEIGHT: u32 = 1080;
