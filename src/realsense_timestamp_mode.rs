use glib::{gobject_sys, StaticType, Type};

#[derive(Debug, Eq, PartialEq, Ord, PartialOrd, Hash, Clone, Copy)]
#[repr(u32)]
pub enum RealsenseTimestampMode {
    Default = 0,
    AllBuffers = 1,
    RS2 = 2,
}
impl glib::translate::ToGlib for RealsenseTimestampMode {
    type GlibType = i32;

    fn to_glib(&self) -> Self::GlibType {
        *self as i32
    }
}
impl glib::translate::FromGlib<i32> for RealsenseTimestampMode {
    fn from_glib(val: i32) -> Self {
        match val {
            0 => RealsenseTimestampMode::Default,
            1 => RealsenseTimestampMode::AllBuffers,
            2 => RealsenseTimestampMode::RS2,
            _ => unreachable!("Invalid RealsenseTimestampMode, options are: 0 (default), 1 (all-buffers) or 2 (RS2)"),
        }
    }
}
impl StaticType for RealsenseTimestampMode {
    fn static_type() -> Type {
        realsense_timestamp_mode_get_type()
    }
}
impl<'a> glib::value::FromValueOptional<'a> for RealsenseTimestampMode {
    unsafe fn from_value_optional(value: &glib::Value) -> Option<Self> {
        Some(glib::value::FromValue::from_value(value))
    }
}
impl<'a> glib::value::FromValue<'a> for RealsenseTimestampMode {
    unsafe fn from_value(value: &glib::Value) -> Self {
        use glib::translate::ToGlibPtr;

        glib::translate::from_glib(gobject_sys::g_value_get_enum(value.to_glib_none().0))
    }
}

impl glib::value::SetValue for RealsenseTimestampMode {
    unsafe fn set_value(value: &mut glib::Value, this: &Self) {
        use glib::translate::{ToGlib, ToGlibPtrMut};

        gobject_sys::g_value_set_enum(value.to_glib_none_mut().0, this.to_glib())
    }
}

pub(crate) fn realsense_timestamp_mode_get_type() -> glib::Type {
    use std::sync::Once;
    static ONCE: Once = Once::new();
    static mut TYPE: glib::Type = glib::Type::Invalid;

    ONCE.call_once(|| {
        use std::ffi;
        use std::ptr;

        static mut VALUES: [gobject_sys::GEnumValue; 4] = [
            gobject_sys::GEnumValue {
                value: RealsenseTimestampMode::Default as i32,
                value_name: b"Default: Adds the realsensesrc's Clock Timestamp to only the main (depth) buffer.\0" as *const _ as *const _,
                value_nick: b"default\0" as *const _ as *const _,
            },
            gobject_sys::GEnumValue {
                value: RealsenseTimestampMode::AllBuffers as i32,
                value_name: b"All Buffers: Adds the realsensesrc's Clock Timestamp to all buffers based on the duration since the element was created.\0" as *const _ as *const _,
                value_nick: b"all-buffers\0" as *const _ as *const _,
            },
            gobject_sys::GEnumValue {
                value: RealsenseTimestampMode::RS2 as i32,
                value_name: b"RS2: Stamps librealsense2's timestamps on all buffers.\0" as *const _ as *const _,
                value_nick: b"rs2\0" as *const _ as *const _,
            },
            gobject_sys::GEnumValue {
                value: 0,
                value_name: ptr::null(),
                value_nick: ptr::null(),
            },
        ];

        let name = ffi::CString::new("GstRealsenseTimestampMode").unwrap();
        unsafe {
            let type_ = gobject_sys::g_enum_register_static(name.as_ptr(), VALUES.as_ptr());
            TYPE = glib::translate::from_glib(type_);
        }
    });

    unsafe {
        assert_ne!(TYPE, glib::Type::Invalid);
        TYPE
    }
}
