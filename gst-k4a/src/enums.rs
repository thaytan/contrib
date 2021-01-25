// Aivero
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

use crate::error::K4aSrcError;
use glib::{StaticType, Type};
use libk4a::{DepthMode, ImageFormat};
use std::convert::TryFrom;

/// Represents the Azure Kinect's color format and is used here to implement it as a GStreamer property.
/// It is a small wrapper around the libk4a::ImageFormat enum, storing only the
/// K4A_IMAGE_FORMAT_COLOR_* part of it.
#[derive(Debug, Eq, PartialEq, Ord, PartialOrd, Hash, Clone, Copy)]
#[repr(u32)]
pub enum K4aColorFormat {
    MJPG = 0,
    NV12 = 1,
    YUV2 = 2,
    BGRA32 = 3,
}

impl K4aColorFormat {
    pub fn get_glib_type() -> glib::Type {
        use std::sync::Once;
        static ONCE: Once = Once::new();
        static mut TYPE: glib::Type = glib::Type::Invalid;

        ONCE.call_once(|| {
            use std::ffi;
            use std::ptr;

            static mut VALUES: [gobject_sys::GEnumValue; 5] = [
                gobject_sys::GEnumValue {
                    value: K4aColorFormat::MJPG as i32,
                    value_name: b"MJPG\0" as *const _ as *const _,
                    value_nick: b"mjpg\0" as *const _ as *const _,
                },
                gobject_sys::GEnumValue {
                    value: K4aColorFormat::NV12 as i32,
                    value_name: b"NV12 (720p only)\0" as *const _ as *const _,
                    value_nick: b"nv12\0" as *const _ as *const _,
                },
                gobject_sys::GEnumValue {
                    value: K4aColorFormat::YUV2 as i32,
                    value_name: b"YUV2 (720p only)\0" as *const _ as *const _,
                    value_nick: b"yuv2\0" as *const _ as *const _,
                },
                gobject_sys::GEnumValue {
                    value: K4aColorFormat::BGRA32 as i32,
                    value_name: b"BGRA32\0" as *const _ as *const _,
                    value_nick: b"bgra32\0" as *const _ as *const _,
                },
                gobject_sys::GEnumValue {
                    value: 0,
                    value_name: ptr::null(),
                    value_nick: ptr::null(),
                },
            ];

            let name = ffi::CString::new("GstK4aColorFormat").unwrap();
            unsafe {
                // Lookup the type ID or return 0 if it has not yet been registered under the specific name
                let mut type_ = gobject_sys::g_type_from_name(name.as_ptr());
                if type_ == 0 {
                    // Register the type ONLY if not done before
                    type_ = gobject_sys::g_enum_register_static(name.as_ptr(), VALUES.as_ptr());
                }
                TYPE = glib::translate::from_glib(type_);
            }
        });

        unsafe {
            assert_ne!(TYPE, glib::Type::Invalid);
            TYPE
        }
    }
}

impl glib::translate::ToGlib for K4aColorFormat {
    type GlibType = i32;

    fn to_glib(&self) -> Self::GlibType {
        *self as i32
    }
}
impl glib::translate::FromGlib<i32> for K4aColorFormat {
    fn from_glib(val: i32) -> Self {
        match val {
            0 => K4aColorFormat::MJPG,
            1 => K4aColorFormat::NV12,
            2 => K4aColorFormat::YUV2,
            3 => K4aColorFormat::BGRA32,
            _ => unreachable!("Invalid GstK4aColorFormat, options are: 0 (MJPG), 1 (NV12), 2 (YUV2) or 3 (BGRA32)"),
        }
    }
}
impl StaticType for K4aColorFormat {
    fn static_type() -> Type {
        K4aColorFormat::get_glib_type()
    }
}
impl<'a> glib::value::FromValueOptional<'a> for K4aColorFormat {
    unsafe fn from_value_optional(value: &glib::Value) -> Option<Self> {
        Some(glib::value::FromValue::from_value(value))
    }
}
impl<'a> glib::value::FromValue<'a> for K4aColorFormat {
    unsafe fn from_value(value: &glib::Value) -> Self {
        use glib::translate::ToGlibPtr;

        glib::translate::from_glib(gobject_sys::g_value_get_enum(value.to_glib_none().0))
    }
}

impl glib::value::SetValue for K4aColorFormat {
    unsafe fn set_value(value: &mut glib::Value, this: &Self) {
        use glib::translate::{ToGlib, ToGlibPtrMut};

        gobject_sys::g_value_set_enum(value.to_glib_none_mut().0, this.to_glib())
    }
}

/// Try to convert a `k4a::ImageFormat` into a [K4aColorFormat](enum.K4aColorFormat.html). This is a
/// TryFrom, as `k4a::ImageFormat` is wider than [K4aColorFormat](enum.K4aColorFormat.html), as it
/// also holds image formats for other streams.
impl TryFrom<libk4a::ImageFormat> for K4aColorFormat {
    type Error = K4aSrcError;

    fn try_from(value: libk4a::ImageFormat) -> Result<Self, Self::Error> {
        match value {
            ImageFormat::K4A_IMAGE_FORMAT_COLOR_NV12 => Ok(K4aColorFormat::NV12),
            ImageFormat::K4A_IMAGE_FORMAT_COLOR_YUY2 => Ok(K4aColorFormat::YUV2),
            ImageFormat::K4A_IMAGE_FORMAT_COLOR_MJPG => Ok(K4aColorFormat::MJPG),
            ImageFormat::K4A_IMAGE_FORMAT_COLOR_BGRA32 => Ok(K4aColorFormat::BGRA32),
            _ => Err(K4aSrcError::Failure("Unsupported ImageFormat conversion")),
        }
    }
}
/// Convert a [K4aColorFormat](enum.K4aColorFormat.html) into a `libk4a::ImageFormat`. This can be
/// converted directly, as all values represented by [K4aColorFormat](enum.K4aColorFormat.html) is
/// also represented by `libk4a::ImageFormat`.
impl From<K4aColorFormat> for libk4a::ImageFormat {
    fn from(cf: K4aColorFormat) -> Self {
        match cf {
            K4aColorFormat::NV12 => ImageFormat::K4A_IMAGE_FORMAT_COLOR_NV12,
            K4aColorFormat::BGRA32 => ImageFormat::K4A_IMAGE_FORMAT_COLOR_BGRA32,
            K4aColorFormat::MJPG => ImageFormat::K4A_IMAGE_FORMAT_COLOR_MJPG,
            K4aColorFormat::YUV2 => ImageFormat::K4A_IMAGE_FORMAT_COLOR_YUY2,
        }
    }
}

/// Represents the Azure Kinect's color resolution and is used here to implement it as a GStreamer property.
#[derive(Debug, Eq, PartialEq, Ord, PartialOrd, Hash, Clone, Copy)]
#[repr(u32)]
pub enum K4aColorResolution {
    C720p = 0,
    C1080p = 1,
    C1440p = 2,
    C1536p = 3,
    C2160p = 4,
    C3072p = 5,
}

impl K4aColorResolution {
    pub fn get_glib_type() -> glib::Type {
        use std::sync::Once;
        static ONCE: Once = Once::new();
        static mut TYPE: glib::Type = glib::Type::Invalid;

        ONCE.call_once(|| {
            use std::ffi;
            use std::ptr;

            static mut VALUES: [gobject_sys::GEnumValue; 7] = [
                gobject_sys::GEnumValue {
                    value: K4aColorResolution::C720p as i32,
                    value_name: b"720p: 720p resolution\0" as *const _ as *const _,
                    value_nick: b"720p\0" as *const _ as *const _,
                },
                gobject_sys::GEnumValue {
                    value: K4aColorResolution::C1080p as i32,
                    value_name: b"1080p: 1080p resolution\0" as *const _ as *const _,
                    value_nick: b"1080p\0" as *const _ as *const _,
                },
                gobject_sys::GEnumValue {
                    value: K4aColorResolution::C1440p as i32,
                    value_name: b"1440p: 1440p resolution\0" as *const _ as *const _,
                    value_nick: b"1440p\0" as *const _ as *const _,
                },
                gobject_sys::GEnumValue {
                    value: K4aColorResolution::C1536p as i32,
                    value_name: b"1536p: 1536p resolution\0" as *const _ as *const _,
                    value_nick: b"1536p\0" as *const _ as *const _,
                },
                gobject_sys::GEnumValue {
                    value: K4aColorResolution::C2160p as i32,
                    value_name: b"2160p: 2160p resolution\0" as *const _ as *const _,
                    value_nick: b"2160p\0" as *const _ as *const _,
                },
                gobject_sys::GEnumValue {
                    value: K4aColorResolution::C3072p as i32,
                    value_name: b"3072p: 3072p resolution\0" as *const _ as *const _,
                    value_nick: b"3072p\0" as *const _ as *const _,
                },
                gobject_sys::GEnumValue {
                    value: 0,
                    value_name: ptr::null(),
                    value_nick: ptr::null(),
                },
            ];

            let name = ffi::CString::new("GstK4aColorResolution").unwrap();
            unsafe {
                // Lookup the type ID or return 0 if it has not yet been registered under the specific name
                let mut type_ = gobject_sys::g_type_from_name(name.as_ptr());
                if type_ == 0 {
                    // Register the type ONLY if not done before
                    type_ = gobject_sys::g_enum_register_static(name.as_ptr(), VALUES.as_ptr());
                }
                TYPE = glib::translate::from_glib(type_);
            }
        });

        unsafe {
            assert_ne!(TYPE, glib::Type::Invalid);
            TYPE
        }
    }
}

impl glib::translate::ToGlib for K4aColorResolution {
    type GlibType = i32;

    fn to_glib(&self) -> Self::GlibType {
        *self as i32
    }
}
impl glib::translate::FromGlib<i32> for K4aColorResolution {
    fn from_glib(val: i32) -> Self {
        match val {
            0 => K4aColorResolution::C720p,
            1 => K4aColorResolution::C1080p,
            2 => K4aColorResolution::C1440p,
            3 => K4aColorResolution::C1536p,
            4 => K4aColorResolution::C2160p,
            5 => K4aColorResolution::C3072p,
            _ => unreachable!("Invalid GstK4aColorResolution, options are: 0 (720p), 1 (1080p), 2 (1440p), 3 (1536p), 4 (2160p) or 5 (3072p)"),
        }
    }
}
impl StaticType for K4aColorResolution {
    fn static_type() -> Type {
        K4aColorResolution::get_glib_type()
    }
}
impl<'a> glib::value::FromValueOptional<'a> for K4aColorResolution {
    unsafe fn from_value_optional(value: &glib::Value) -> Option<Self> {
        Some(glib::value::FromValue::from_value(value))
    }
}
impl<'a> glib::value::FromValue<'a> for K4aColorResolution {
    unsafe fn from_value(value: &glib::Value) -> Self {
        use glib::translate::ToGlibPtr;

        glib::translate::from_glib(gobject_sys::g_value_get_enum(value.to_glib_none().0))
    }
}

impl glib::value::SetValue for K4aColorResolution {
    unsafe fn set_value(value: &mut glib::Value, this: &Self) {
        use glib::translate::{ToGlib, ToGlibPtrMut};

        gobject_sys::g_value_set_enum(value.to_glib_none_mut().0, this.to_glib())
    }
}

/// Try to convert a `k4a::ColorResolution` into a [K4aColorResolution](enum.K4aColorResolution.html). This is a
/// TryFrom, as `k4a::ColorResolution` is wider than [K4aColorResolution](enum.K4aColorResolution.html).
impl TryFrom<libk4a::ColorResolution> for K4aColorResolution {
    type Error = K4aSrcError;

    fn try_from(res: libk4a::ColorResolution) -> Result<Self, Self::Error> {
        match res {
            libk4a::ColorResolution::K4A_COLOR_RESOLUTION_720P => Ok(K4aColorResolution::C720p),
            libk4a::ColorResolution::K4A_COLOR_RESOLUTION_1080P => Ok(K4aColorResolution::C1080p),
            libk4a::ColorResolution::K4A_COLOR_RESOLUTION_1440P => Ok(K4aColorResolution::C1440p),
            libk4a::ColorResolution::K4A_COLOR_RESOLUTION_1536P => Ok(K4aColorResolution::C1536p),
            libk4a::ColorResolution::K4A_COLOR_RESOLUTION_2160P => Ok(K4aColorResolution::C2160p),
            libk4a::ColorResolution::K4A_COLOR_RESOLUTION_3072P => Ok(K4aColorResolution::C3072p),
            _ => Err(K4aSrcError::Failure(
                "Unsupported k4a color resolution conversion",
            )),
        }
    }
}
/// Convert a [K4aColorResolution](enum.K4aColorResolution.html) into a `libk4a::ColorResolution`. This can be
/// converted directly, as all values represented by [K4aColorResolution](enum.K4aColorResolution.html) is
/// also represented by `libk4a::ColorResolution`.
impl From<K4aColorResolution> for libk4a::ColorResolution {
    fn from(cr: K4aColorResolution) -> Self {
        match cr {
            K4aColorResolution::C720p => libk4a::ColorResolution::K4A_COLOR_RESOLUTION_720P,
            K4aColorResolution::C1080p => libk4a::ColorResolution::K4A_COLOR_RESOLUTION_1080P,
            K4aColorResolution::C1440p => libk4a::ColorResolution::K4A_COLOR_RESOLUTION_1440P,
            K4aColorResolution::C1536p => libk4a::ColorResolution::K4A_COLOR_RESOLUTION_1536P,
            K4aColorResolution::C2160p => libk4a::ColorResolution::K4A_COLOR_RESOLUTION_2160P,
            K4aColorResolution::C3072p => libk4a::ColorResolution::K4A_COLOR_RESOLUTION_3072P,
        }
    }
}

/// Represents the Azure Kinect's depth mode and is used here to implement it as a GStreamer property.
#[derive(Debug, Eq, PartialEq, Ord, PartialOrd, Hash, Clone, Copy)]
#[repr(u32)]
pub enum K4aDepthMode {
    Nfov2x2Binned,
    NfovUnbinned,
    Wfov2x2Binned,
    WfovUnbinned,
}

impl glib::translate::ToGlib for K4aDepthMode {
    type GlibType = i32;

    fn to_glib(&self) -> Self::GlibType {
        *self as i32
    }
}
impl glib::translate::FromGlib<i32> for K4aDepthMode {
    fn from_glib(val: i32) -> Self {
        match val {
            0 => K4aDepthMode::Nfov2x2Binned,
            1 => K4aDepthMode::NfovUnbinned,
            2 => K4aDepthMode::Wfov2x2Binned,
            3 => K4aDepthMode::WfovUnbinned,
            _ => unreachable!("Invalid GstK4aColorResolution, options are: 0 (Nfov2x2Binned), 1 (NfovUnbinned), 2 (Wfov2x2Binned), or 3 (WfovUnbinned)"),
        }
    }
}
impl StaticType for K4aDepthMode {
    fn static_type() -> Type {
        K4aDepthMode::get_glib_type()
    }
}
impl<'a> glib::value::FromValueOptional<'a> for K4aDepthMode {
    unsafe fn from_value_optional(value: &glib::Value) -> Option<Self> {
        Some(glib::value::FromValue::from_value(value))
    }
}
impl<'a> glib::value::FromValue<'a> for K4aDepthMode {
    unsafe fn from_value(value: &glib::Value) -> Self {
        use glib::translate::ToGlibPtr;

        glib::translate::from_glib(gobject_sys::g_value_get_enum(value.to_glib_none().0))
    }
}

impl glib::value::SetValue for K4aDepthMode {
    unsafe fn set_value(value: &mut glib::Value, this: &Self) {
        use glib::translate::{ToGlib, ToGlibPtrMut};

        gobject_sys::g_value_set_enum(value.to_glib_none_mut().0, this.to_glib())
    }
}

impl K4aDepthMode {
    pub fn get_glib_type() -> glib::Type {
        use std::sync::Once;
        static ONCE: Once = Once::new();
        static mut TYPE: glib::Type = glib::Type::Invalid;

        ONCE.call_once(|| {
            use std::ffi;
            use std::ptr;

            static mut VALUES: [gobject_sys::GEnumValue; 5] = [
                gobject_sys::GEnumValue {
                    value: K4aDepthMode::Nfov2x2Binned as i32,
                    value_name: b"NFOV 2x2 Binned\0" as *const _ as *const _,
                    value_nick: b"nfov_2x2_binned\0" as *const _ as *const _,
                },
                gobject_sys::GEnumValue {
                    value: K4aDepthMode::NfovUnbinned as i32,
                    value_name: b"NFOV Unbinned\0" as *const _ as *const _,
                    value_nick: b"nfov_unbinned\0" as *const _ as *const _,
                },
                gobject_sys::GEnumValue {
                    value: K4aDepthMode::Wfov2x2Binned as i32,
                    value_name: b"WFOV 2x2 Binned\0" as *const _ as *const _,
                    value_nick: b"wfov_2x2_binned\0" as *const _ as *const _,
                },
                gobject_sys::GEnumValue {
                    value: K4aDepthMode::WfovUnbinned as i32,
                    value_name: b"WFOV unbinned\0" as *const _ as *const _,
                    value_nick: b"wfov_unbinned\0" as *const _ as *const _,
                },
                gobject_sys::GEnumValue {
                    value: 0,
                    value_name: ptr::null(),
                    value_nick: ptr::null(),
                },
            ];

            let name = ffi::CString::new("GstK4aDepthMode").unwrap();
            unsafe {
                // Lookup the type ID or return 0 if it has not yet been registered under the specific name
                let mut type_ = gobject_sys::g_type_from_name(name.as_ptr());
                if type_ == 0 {
                    // Register the type ONLY if not done before
                    type_ = gobject_sys::g_enum_register_static(name.as_ptr(), VALUES.as_ptr());
                }
                TYPE = glib::translate::from_glib(type_);
            }
        });

        unsafe {
            assert_ne!(TYPE, glib::Type::Invalid);
            TYPE
        }
    }
}

/// Try to convert a `k4a::DepthMode` into a [K4aDepthMode](enum.K4aDepthMode.html). This is a
/// TryFrom, as `k4a::DepthMode` is wider than [K4aDepthMode](enum.K4aDepthMode.html).
impl TryFrom<libk4a::DepthMode> for K4aDepthMode {
    type Error = K4aSrcError;

    fn try_from(dm: libk4a::DepthMode) -> Result<Self, Self::Error> {
        match dm {
            DepthMode::K4A_DEPTH_MODE_NFOV_2X2BINNED => Ok(K4aDepthMode::Nfov2x2Binned),
            DepthMode::K4A_DEPTH_MODE_NFOV_UNBINNED => Ok(K4aDepthMode::NfovUnbinned),
            DepthMode::K4A_DEPTH_MODE_WFOV_2X2BINNED => Ok(K4aDepthMode::Wfov2x2Binned),
            DepthMode::K4A_DEPTH_MODE_WFOV_UNBINNED => Ok(K4aDepthMode::WfovUnbinned),
            _ => Err(K4aSrcError::Failure(
                "Unsupported k4a::DepthMode conversion",
            )),
        }
    }
}
/// Convert a [K4aDepthMode](enum.K4aDepthMode.html) into a `k4a::DepthMode`. This can be
/// converted directly, as all values represented by [K4aDepthMode](enum.K4aDepthMode.html) is
/// also represented by `k4a::DepthMode`.
impl From<K4aDepthMode> for libk4a::DepthMode {
    fn from(value: K4aDepthMode) -> Self {
        match value {
            K4aDepthMode::Nfov2x2Binned => DepthMode::K4A_DEPTH_MODE_NFOV_2X2BINNED,
            K4aDepthMode::NfovUnbinned => DepthMode::K4A_DEPTH_MODE_NFOV_UNBINNED,
            K4aDepthMode::Wfov2x2Binned => DepthMode::K4A_DEPTH_MODE_WFOV_2X2BINNED,
            K4aDepthMode::WfovUnbinned => DepthMode::K4A_DEPTH_MODE_WFOV_UNBINNED,
        }
    }
}

/// The Azure Kinect does not have a floating framerate, as with other cameras. We therefore
/// represent it as an enum here. This enum is used to implement it as a GStreamer property.
#[derive(Debug, Eq, PartialEq, Ord, PartialOrd, Hash, Clone, Copy)]
#[repr(u32)]
pub enum K4aFramerate {
    FPS5,
    FPS15,
    FPS30,
}

impl glib::translate::ToGlib for K4aFramerate {
    type GlibType = i32;

    fn to_glib(&self) -> Self::GlibType {
        *self as i32
    }
}
impl glib::translate::FromGlib<i32> for K4aFramerate {
    fn from_glib(val: i32) -> Self {
        match val {
            0 => K4aFramerate::FPS5,
            1 => K4aFramerate::FPS15,
            2 => K4aFramerate::FPS30,
            _ => unreachable!(
                "Invalid GstK4aFramerate, options are: 0 (5 FPS), 1 (15 FPS) or 2 (30 FPS)"
            ),
        }
    }
}
impl StaticType for K4aFramerate {
    fn static_type() -> Type {
        K4aFramerate::get_glib_type()
    }
}
impl<'a> glib::value::FromValueOptional<'a> for K4aFramerate {
    unsafe fn from_value_optional(value: &glib::Value) -> Option<Self> {
        Some(glib::value::FromValue::from_value(value))
    }
}
impl<'a> glib::value::FromValue<'a> for K4aFramerate {
    unsafe fn from_value(value: &glib::Value) -> Self {
        use glib::translate::ToGlibPtr;

        glib::translate::from_glib(gobject_sys::g_value_get_enum(value.to_glib_none().0))
    }
}

impl glib::value::SetValue for K4aFramerate {
    unsafe fn set_value(value: &mut glib::Value, this: &Self) {
        use glib::translate::{ToGlib, ToGlibPtrMut};

        gobject_sys::g_value_set_enum(value.to_glib_none_mut().0, this.to_glib())
    }
}

impl K4aFramerate {
    pub fn get_glib_type() -> glib::Type {
        use std::sync::Once;
        static ONCE: Once = Once::new();
        static mut TYPE: glib::Type = glib::Type::Invalid;

        ONCE.call_once(|| {
            use std::ffi;
            use std::ptr;

            static mut VALUES: [gobject_sys::GEnumValue; 4] = [
                gobject_sys::GEnumValue {
                    value: K4aFramerate::FPS5 as i32,
                    value_name: b"5 FPS\0" as *const _ as *const _,
                    value_nick: b"5fps\0" as *const _ as *const _,
                },
                gobject_sys::GEnumValue {
                    value: K4aFramerate::FPS15 as i32,
                    value_name: b"15 FPS\0" as *const _ as *const _,
                    value_nick: b"15fps\0" as *const _ as *const _,
                },
                gobject_sys::GEnumValue {
                    value: K4aFramerate::FPS30 as i32,
                    value_name: b"30 FPS (not available for `depth-mode=WFOV_unbinned` or `color-resolution=3072p`)\0" as *const _ as *const _,
                    value_nick: b"30fps\0" as *const _ as *const _,
                },
                gobject_sys::GEnumValue {
                    value: 0,
                    value_name: ptr::null(),
                    value_nick: ptr::null(),
                },
            ];

            let name = ffi::CString::new("GstK4aFramerate").unwrap();
            unsafe {
                // Lookup the type ID or return 0 if it has not yet been registered under the specific name
                let mut type_ = gobject_sys::g_type_from_name(name.as_ptr());
                if type_ == 0 {
                    // Register the type ONLY if not done before
                    type_ = gobject_sys::g_enum_register_static(name.as_ptr(), VALUES.as_ptr());
                }
                TYPE = glib::translate::from_glib(type_);
            }
        });

        unsafe {
            assert_ne!(TYPE, glib::Type::Invalid);
            TYPE
        }
    }

    pub fn allowed_framerates() -> Vec<i32> {
        vec![5, 15, 30]
    }
}

/// Convert a [K4aFramerate](enum.K4aFramerate.html) into `libk4a::Fps`.
impl From<K4aFramerate> for libk4a::Fps {
    fn from(fr: K4aFramerate) -> Self {
        match fr {
            K4aFramerate::FPS5 => libk4a::Fps::K4A_FRAMES_PER_SECOND_5,
            K4aFramerate::FPS15 => libk4a::Fps::K4A_FRAMES_PER_SECOND_15,
            K4aFramerate::FPS30 => libk4a::Fps::K4A_FRAMES_PER_SECOND_30,
        }
    }
}