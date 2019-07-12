// Framerate
pub const MIN_FRAMERATE: f32 = 6.0;
pub const MAX_FRAMERATE: f32 = 90.0;
pub const DEFAULT_FRAMERATE: f32 = 30.0;

// Depth
// This stream is always enabled
pub const DEPTH_MIN_WIDTH: u32 = 1;
pub const DEPTH_MAX_WIDTH: u32 = 1280;
pub const DEFAULT_DEPTH_WIDTH: u32 = 1280;

pub const DEPTH_MIN_HEIGHT: u32 = 1;
pub const DEPTH_MAX_HEIGHT: u32 = 720;
pub const DEFAULT_DEPTH_HEIGHT: u32 = 720;

// Color
pub const DEFAULT_ENABLE_COLOR: bool = true;

pub const COLOR_MIN_WIDTH: u32 = 1;
pub const COLOR_MAX_WIDTH: u32 = 1920;
pub const DEFAULT_COLOR_WIDTH: u32 = 1280;

pub const COLOR_MIN_HEIGHT: u32 = 1;
pub const COLOR_MAX_HEIGHT: u32 = 1080;
pub const DEFAULT_COLOR_HEIGHT: u32 = 720;

// IR
pub const DEFAULT_ENABLE_INFRA_1: bool = false;
pub const DEFAULT_ENABLE_INFRA_2: bool = false;

pub const INFRA_MIN_WIDTH: u32 = 1;
pub const INFRA_MAX_WIDTH: u32 = 1280;
pub const DEFAULT_INFRA_WIDTH: u32 = 1280;

pub const INFRA_MIN_HEIGHT: u32 = 1;
pub const INFRA_MAX_HEIGHT: u32 = 720;
pub const DEFAULT_INFRA_HEIGHT: u32 = 720;
