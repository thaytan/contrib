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

use glib::*;

/// Timestamp mode, which is used to determine the timestamps of outgoing buffers.
#[derive(Debug, Clone, Copy, Eq, PartialEq, Hash)]
#[repr(u32)]
pub enum TimestampMode {
    /// Don't do any timestamping.
    Ignore = 0,
    /// Timestamp only the main buffer based on running time.
    ClockMain = 1,
    /// Timestamp all buffers based on running time.
    ClockAll = 2,
    /// Timestamp all buf// Copyright (C) <2019> Aivero
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

use glib::*;

/// Timestamp mode, which is used to determine the timestamps of outgoing buffers.
#[derive(Debug, Clone, Copy, Eq, PartialEq, Hash)]
#[repr(u32)]
pub enum TimestampMode {
    /// Don't do any timestamping.
    Ignore = 0,
    /// Timestamp only the main buffer based on running time.
    ClockMain = 1,
    /// Timestamp all buffers based on running time.
    ClockAll = 2,
    /// Timestamp all buffers based on camera timestamps. All buffers in a single frameset have the same timestamp.
    CameraCommon = 3,
    /// Timestamp all buffers based on camera timestamps. Buffers in a single frameset can have different timestamps.
    CameraIndividual = 4,
}

/// Implentation of Default trait for TimestampMode, which returns `TimestampMode::CameraCommon`.
impl Default for TimestampMode {
    fn default() -> Self {
        TimestampMode::CameraCommon
    }
}

impl TimestampMode {
    /// Return glib type of TimestampMode.
    fn get_glib_type() -> glib::Type {
        use std::sync::Once;
        static ONCE: Once = Once::new();
        static mut TYPE: glib::Type = glib::Type::Invalid;

        ONCE.call_once(|| {
            use std::ffi;
            use std::ptr;

            static mut VALUES: [gobject_sys::GEnumValue; 6] = [
            gobject_sys::GEnumValue {
                    value: TimestampMode::Ignore as i32,
                    value_name: b"Ignore: Do not apply timestamp to any buffer.\0" as *const _ as *const _,
                    value_nick: b"ignore\0" as *const _ as *const _,
                },
                gobject_sys::GEnumValue {
                    value: TimestampMode::ClockMain as i32,
                    value_name: b"ClockMain: Determine timestamps based on the current running time. Apply timestamps only to buffers of the main stream. Note that functionality of this variant is identical to enabling `do-timestamp` property.\0" as *const _ as *const _,
                    value_nick: b"clock_main\0" as *const _ as *const _,
                },
                gobject_sys::GEnumValue {
                    value: TimestampMode::ClockAll as i32,
                    value_name: b"ClockAll: Determine timestamps based on the current running time. Apply timestamps to buffers of all streams.\0" as *const _ as *const _,
                    value_nick: b"clock_all\0" as *const _ as *const _,
                },
                gobject_sys::GEnumValue {
                    value: TimestampMode::CameraCommon as i32,
                    value_name: b"CameraCommon: Utilise timestamps acquired from camera or recording, if applicable. Apply timestamps to buffers of all streams. A common timestamp is applied to all buffers that belong to a single frameset, where the timestamp for each frameset is based on a frame that belongs to the main stream.\0" as *const _ as *const _,
                    value_nick: b"camera_common\0" as *const _ as *const _,
                },
                gobject_sys::GEnumValue {
                    value: TimestampMode::CameraIndividual as i32,
                    value_name: b"CameraIndividual: Utilise timestamps acquired from camera or recording, if applicable. Apply timestamps to buffers of all streams. Individual timestamps are applied to buffers that belong to a single frameset, where the timestamp of each buffer is based on corresponding frame. Note that certain cameras can have some of all of the streams synchronised.\0" as *const _ as *const _,
                    value_nick: b"camera_individual\0" as *const _ as *const _,
                },
                gobject_sys::GEnumValue {
                    value: 0,
                    value_name: ptr::null(),
                    value_nick: ptr::null(),
                },
            ];

            let name = ffi::CString::new("GstTimestampMode").unwrap();
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

    /// Return `timestamp-mode` property definition that can be utilised by elements that use `TimestampMode` struct.
    /// Element utilising this property also needs to implement the corresponding variants for `get_property()` and `set_property()`
    pub fn get_property_type() -> subclass::Property<'static> {
        subclass::Property("timestamp-mode", |name| {
            glib::ParamSpec::enum_(
                name,
                "Timestamp Mode",
                "This property determines what timestamp mode to use for the outgoing `video/rgbd` stream. If implemented, please ignore `do-timestamp` property.",
                TimestampMode::static_type(),
                TimestampMode::default() as i32,
                glib::ParamFlags::READWRITE,
            )
        })
    }
}

impl StaticType for TimestampMode {
    fn static_type() -> Type {
        TimestampMode::get_glib_type()
    }
}
impl glib::translate::ToGlib for TimestampMode {
    type GlibType = i32;

    fn to_glib(&self) -> Self::GlibType {
        *self as i32
    }
}
impl glib::translate::FromGlib<i32> for TimestampMode {
    fn from_glib(val: i32) -> Self {
        match val {
            0 => TimestampMode::Ignore,
            1 => TimestampMode::ClockMain,
            2 => TimestampMode::ClockAll,
            3 => TimestampMode::CameraCommon,
            4 => TimestampMode::CameraIndividual,
            _ => unreachable!("Invalid GstTimestampMode, supported variants are 0 (Ignore), 1 (ClockMain, 2 (ClockAll), 3 (CameraCommon) and 4 (CameraIndividual)"),
        }
    }
}
impl<'a> glib::value::FromValueOptional<'a> for TimestampMode {
    unsafe fn from_value_optional(value: &glib::Value) -> Option<Self> {
        Some(glib::value::FromValue::from_value(value))
    }
}
impl<'a> glib::value::FromValue<'a> for TimestampMode {
    unsafe fn from_value(value: &glib::Value) -> Self {
        use glib::translate::ToGlibPtr;
        glib::translate::from_glib(gobject_sys::g_value_get_enum(value.to_glib_none().0))
    }
}
impl glib::value::SetValue for TimestampMode {
    unsafe fn set_value(value: &mut glib::Value, this: &Self) {
        use glib::translate::{ToGlib, ToGlibPtrMut};
        gobject_sys::g_value_set_enum(value.to_glib_none_mut().0, this.to_glib())
    }
}
fers based on camera timestamps. All buffers in a single frameset have the same timestamp.
    CameraCommon = 3,
    /// Timestamp all buffers based on camera timestamps. Buffers in a single frameset can have different timestamps.
    CameraIndividual = 4,
}

/// Implentation of Default trait for TimestampMode, which returns `TimestampMode::CameraCommon`.
impl Default for TimestampMode {
    fn default() -> Self {
        TimestampMode::CameraCommon
    }
}

impl TimestampMode {
    /// Return glib type of TimestampMode.
    fn get_glib_type() -> glib::Type {
        use std::sync::Once;
        static ONCE: Once = Once::new();
        static mut TYPE: glib::Type = glib::Type::Invalid;

        ONCE.call_once(|| {
            use std::ffi;
            use std::ptr;

            static mut VALUES: [gobject_sys::GEnumValue; 6] = [
            gobject_sys::GEnumValue {
                    value: TimestampMode::Ignore as i32,
                    value_name: b"Ignore: Do not apply timestamp to any buffer.\0" as *const _ as *const _,
                    value_nick: b"ignore\0" as *const _ as *const _,
                },
                gobject_sys::GEnumValue {
                    value: TimestampMode::ClockMain as i32,
                    value_name: b"ClockMain: Determine timestamps based on the current running time. Apply timestamps only to buffers of the main stream. Note that functionality of this variant is identical to enabling `do-timestamp` property.\0" as *const _ as *const _,
                    value_nick: b"clock_main\0" as *const _ as *const _,
                },
                gobject_sys::GEnumValue {
                    value: TimestampMode::ClockAll as i32,
                    value_name: b"ClockAll: Determine timestamps based on the current running time. Apply timestamps to buffers of all streams.\0" as *const _ as *const _,
                    value_nick: b"clock_all\0" as *const _ as *const _,
                },
                gobject_sys::GEnumValue {
                    value: TimestampMode::CameraCommon as i32,
                    value_name: b"CameraCommon: Utilise timestamps acquired from camera or recording, if applicable. Apply timestamps to buffers of all streams. A common timestamp is applied to all buffers that belong to a single frameset, where the timestamp for each frameset is based on a frame that belongs to the main stream.\0" as *const _ as *const _,
                    value_nick: b"camera_common\0" as *const _ as *const _,
                },
                gobject_sys::GEnumValue {
                    value: TimestampMode::CameraIndividual as i32,
                    value_name: b"CameraIndividual: Utilise timestamps acquired from camera or recording, if applicable. Apply timestamps to buffers of all streams. Individual timestamps are applied to buffers that belong to a single frameset, where the timestamp of each buffer is based on corresponding frame. Note that certain cameras can have some of all of the streams synchronised.\0" as *const _ as *const _,
                    value_nick: b"camera_individual\0" as *const _ as *const _,
                },
                gobject_sys::GEnumValue {
                    value: 0,
                    value_name: ptr::null(),
                    value_nick: ptr::null(),
                },
            ];

            let name = ffi::CString::new("GstTimestampMode").unwrap();
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

    /// Return `timestamp-mode` property definition that can be utilised by elements that use `TimestampMode` struct.
    /// Element utilising this property also needs to implement the corresponding variants for `get_property()` and `set_property()`
    pub fn get_property_type() -> subclass::Property<'static> {
        subclass::Property("timestamp-mode", |name| {
            glib::ParamSpec::enum_(
                name,
                "Timestamp Mode",
                "This property determines what timestamp mode to use for the outgoing `video/rgbd` stream. If implemented, please ignore `do-timestamp` property.",
                TimestampMode::static_type(),
                TimestampMode::default() as i32,
                glib::ParamFlags::READWRITE,
            )
        })
    }
}

impl StaticType for TimestampMode {
    fn static_type() -> Type {
        TimestampMode::get_glib_type()
    }
}
impl glib::translate::ToGlib for TimestampMode {
    type GlibType = i32;

    fn to_glib(&self) -> Self::GlibType {
        *self as i32
    }
}
impl glib::translate::FromGlib<i32> for TimestampMode {
    fn from_glib(val: i32) -> Self {
        match val {
            0 => TimestampMode::Ignore,
            1 => TimestampMode::ClockMain,
            2 => TimestampMode::ClockAll,
            3 => TimestampMode::CameraCommon,
            4 => TimestampMode::CameraIndividual,
            _ => unreachable!("Invalid GstTimestampMode, supported variants are 0 (Ignore), 1 (ClockMain, 2 (ClockAll), 3 (CameraCommon) and 4 (CameraIndividual)"),
        }
    }
}
impl<'a> glib::value::FromValueOptional<'a> for TimestampMode {
    unsafe fn from_value_optional(value: &glib::Value) -> Option<Self> {
        Some(glib::value::FromValue::from_value(value))
    }
}
impl<'a> glib::value::FromValue<'a> for TimestampMode {
    unsafe fn from_value(value: &glib::Value) -> Self {
        use glib::translate::ToGlibPtr;
        glib::translate::from_glib(gobject_sys::g_value_get_enum(value.to_glib_none().0))
    }
}
impl glib::value::SetValue for TimestampMode {
    unsafe fn set_value(value: &mut glib::Value, this: &Self) {
        use glib::translate::{ToGlib, ToGlibPtrMut};
        gobject_sys::g_value_set_enum(value.to_glib_none_mut().0, this.to_glib())
    }
}