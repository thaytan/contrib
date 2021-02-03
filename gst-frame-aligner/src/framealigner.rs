/*
 * AIVERO CONFIDENTIAL
 * __________________
 *
 *  [2017] - [2020] Aivero AS
 *  All Rights Reserved.
 *
 * NOTICE:  All information contained herein is, and remains
 * the property of Aivero AS and its suppliers,
 * if any. The intellectual and technical concepts contained
 * herein are proprietary to Aivero AS
 * and its suppliers and may be covered by EU,
 * patents in process, and are protected by trade secret or copyright law.
 * Dissemination of this information or reproduction of this material
 * is strictly forbidden unless prior written permission is obtained
 * from Aivero AS.
 */

use crate::common::*;
use glib::subclass;
use gst::subclass::prelude::*;
use gst_base::prelude::*;
use gst_base::subclass::prelude::*;
use gstreamer_depth_meta::rgbd;
use na::*;
use std::collections::HashMap;
use std::sync::Mutex;

// Declare debug category
lazy_static! {
    static ref CAT: gst::DebugCategory = gst::DebugCategory::new(
        "framealigner",
        gst::DebugColorFlags::empty(),
        Some("Frame Aligner")
    );
}

// This element is based on this formula x2 = K2*R*inverse(K1)*x1 + K2*t/x1_z. THe first of the sum we called transform1*x1.

/// Depth factor for which we have to divide the depth values read from the camera,
/// e.g. if a camera is using mm units, this should be 1000. If it is using half-mm
/// units this should be 2000.
const DEFAULT_DEPTH_FACTOR: f32 = 1000.0;

/// Properties for the `framealigner` element
static PROPERTIES: [subclass::Property; 2] = [
    subclass::Property("depth_factor", |name| {
        glib::ParamSpec::float(
            name,
            "depth_factor",
            "The `depth_factor` to apply to the depth maps",
            1.0,
            30000.0,
            DEFAULT_DEPTH_FACTOR,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("calib_file", |name| {
        glib::ParamSpec::string(
            name,
            "calib_file",
            "Calibration file from where to read the camera parameters",
            Some("calib.txt"),
            glib::ParamFlags::READWRITE,
        )
    }),
];

/// This structure holds the `framealigner` state
#[derive(Debug)]
struct FrameAlignerState {
    /// * `depth_factor` - The depth factor to use to convert the read depth data into meters.
    depth_factor: f32,
    /// * `video_info_in` - CapsVideoInfo that carries info about the streams.
    video_info: Option<CapsVideoInfo>,
    /// * `calib_file` - Path to camera calibration file.
    calib_file: String,
    /// * `transform1` - Struct that holds the except for the translation.
    rotation: Matrix3<f32>,
    /// * `k_color` - Struct that holds the color camera intrinsics parameters.
    k_color: Matrix3<f32>,
    /// * `k_depth` - Struct that holds the color camera intrinsics parameters.
    k_depth: Matrix3<f32>,
    /// * `translation` - Struct that holds the translation matrix.
    translation: Matrix3x1<f32>,
    /// * `dump` - Bool that tells the element whether or not to write the curent pointcloud frame to file.
    dump: bool,
}
/// A struct representation of the `framealigner` element. The algorithm used in this element is
/// loosely based on https://www.codefull.org/2016/03/align-depth-and-color-frames-depth-and-rgb-registration/.
/// # What is this?
/// The `framealigner` aligns depth frames in a RGBD stream to the color space as indicated by the camera parameters.
struct FrameAligner {
    /// * `state` - Holds element's state.
    state: Mutex<FrameAlignerState>,
}

impl FrameAligner {
    /// Map a point in depth image to a point in color image.
    /// Code based in http://docs.ros.org/kinetic/api/librealsense2/html/align_8cpp_source.html#l00019
    /// # Arguments
    /// * `state` - The internal state of the framealigner.
    /// * `data` - Mutable reference to the in-place buffer
    /// * `width` - The width of the image.
    /// * `height` - The height of the image.
    #[inline]
    fn get_new_depth_image(
        &self,
        state: &FrameAlignerState,
        data: &mut [u16],
        width: usize,
        height: usize,
    ) {
        // Get camera parameters
        let cx_d = state.k_depth[(0, 2)] as f32;
        let cy_d = state.k_depth[(1, 2)] as f32;
        let fx_d = state.k_depth[(0, 0)] as f32;
        let fy_d = state.k_depth[(1, 1)] as f32;

        let cx_c = state.k_color[(0, 2)] as f32;
        let cy_c = state.k_color[(1, 2)] as f32;
        let fx_c = state.k_color[(0, 0)] as f32;
        let fy_c = state.k_color[(1, 1)] as f32;

        let mut depth_point = Matrix3x1::new(0.0, 0.0, 0.0);
        let mut other_pixel = Matrix2x1::new(0.0, 0.0);

        // Iterate over the image
        for x_d in 0..height {
            for y_d in 0..width {
                if data[x_d * width + y_d] != 0 {
                    // Get depth data
                    let z = (data[x_d * width + y_d] as f32) / state.depth_factor;
                    // Zero the vector
                    data[x_d * width + y_d] = 0;

                    // Map the top-left corner of the depth pixel onto the other image
                    let tl_depth_pixel = Matrix2x1::new(x_d as f32 - 0.5, y_d as f32 - 0.5);
                    // Get the 3D point in the depth world coordinate frame
                    depth_point.x = (tl_depth_pixel.x as f32 - cx_d) * z / fx_d;
                    depth_point.y = (tl_depth_pixel.y as f32 - cy_d) * z / fy_d;
                    depth_point.z = z;

                    // Rotate the 3D point to the color world coordinate frame
                    let mut other_point = state.rotation * depth_point + state.translation;

                    // Project the point into the image using camera intrinsics
                    other_pixel.x = (other_point.x / other_point.z * fx_c) + cx_c;
                    other_pixel.y = (other_point.y / other_point.z * fy_c) + cy_c;

                    // Do naive intrpolation
                    let other_x0 = (other_pixel.x + 0.5) as usize;
                    let other_y0 = (other_pixel.y + 0.5) as usize;

                    // Map the bottom-right corner of the depth pixel onto the other image
                    let br_depth_pixel = Matrix2x1::new(x_d as f32 + 0.5, y_d as f32 + 0.5);
                    // Get the 3D point in the depth world coordinate frame
                    depth_point.x = (br_depth_pixel.x as f32 - cx_d) * z / fx_d;
                    depth_point.y = (br_depth_pixel.y as f32 - cy_d) * z / fy_d;
                    depth_point.z = z;

                    // Rotate the 3D point to the color world coordinate frame
                    other_point = state.rotation * depth_point + state.translation;

                    // Project the point into the image using camera intrinsics
                    other_pixel.x = (other_point.x / other_point.z * fx_c) + cx_c;
                    other_pixel.y = (other_point.y / other_point.z * fy_c) + cy_c;

                    // DO naive interpolation
                    let other_x1 = (other_pixel.x + 0.5).round() as usize;
                    let other_y1 = (other_pixel.y + 0.5).round() as usize;

                    // Check if points are within the frame
                    if other_x1 >= height || other_y1 >= width {
                        continue;
                    }

                    // Write depth data into rectangle made by top-left and bottom-right corners
                    for i in other_x0..other_x1 {
                        for j in other_y0..other_y1 {
                            data[i * width + j] = (z * state.depth_factor) as u16;
                        }
                    }
                }
            }
        }
    }

    /// Function that gets calibration matrices from a calib file
    /// # Arguments
    /// * `path_to_calib_file` - a path to the calib file.
    /// * `state` - The state of the framealigner.
    /// # Panics
    /// If the specified file did not exist, or contained invalid data.
    fn get_parameters(
        &self,
        path_to_calib_file: String,
        state: &mut FrameAlignerState,
    ) -> Result<(), GstFrameAlignerError> {
        // Open file
        let f = std::fs::File::open(path_to_calib_file)?;
        // Read map from file
        let map: HashMap<String, f32> = serde_yaml::from_reader(f)?;

        // Parse the rotation/translation matrix
        let error = GstFrameAlignerError::new("Missing field from config file".to_string());
        // Read parameters from map
        let r11 = *map.get("r11").ok_or_else(|| error.clone())?;
        let r12 = *map.get("r12").ok_or_else(|| error.clone())?;
        let r13 = *map.get("r13").ok_or_else(|| error.clone())?;
        let t1 = *map.get("t1").ok_or_else(|| error.clone())?;
        let r21 = *map.get("r21").ok_or_else(|| error.clone())?;
        let r22 = *map.get("r22").ok_or_else(|| error.clone())?;
        let r23 = *map.get("r23").ok_or_else(|| error.clone())?;
        let t2 = *map.get("t2").ok_or_else(|| error.clone())?;
        let r31 = *map.get("r31").ok_or_else(|| error.clone())?;
        let r32 = *map.get("r32").ok_or_else(|| error.clone())?;
        let r33 = *map.get("r33").ok_or_else(|| error.clone())?;
        let t3 = *map.get("t3").ok_or_else(|| error.clone())?;
        let fx_c = *map.get("fx_c").ok_or_else(|| error.clone())?;
        let fy_c = *map.get("fy_c").ok_or_else(|| error.clone())?;
        let cx_c = *map.get("cx_c").ok_or_else(|| error.clone())?;
        let cy_c = *map.get("cy_c").ok_or_else(|| error.clone())?;
        let fx_d = *map.get("fx_d").ok_or_else(|| error.clone())?;
        let fy_d = *map.get("fy_d").ok_or_else(|| error.clone())?;
        let cx_d = *map.get("cx_d").ok_or_else(|| error.clone())?;
        let cy_d = *map.get("cy_d").ok_or_else(|| error.clone())?;

        // Build extrinsic and intrinsics matrices
        state.rotation = Matrix3::new(r11, r12, r13, r21, r22, r23, r31, r32, r33);
        state.translation = Matrix3x1::new(t1, t2, t3);
        state.k_color = Matrix3::new(fx_c, 0.0, cx_c, 0.0, fy_c, cy_c, 0.0, 0.0, 1.0);
        state.k_depth = Matrix3::new(fx_d, 0.0, cx_d, 0.0, fy_d, cy_d, 0.0, 0.0, 1.0);
        Ok(())
    }
}

impl ElementImpl for FrameAligner {
    /// Act on state transition.
    /// # Arguments
    /// * `element` - Object that holds the representation of the element.
    /// * `transition` - Object that holds a state transition.
    fn change_state(
        &self,
        element: &gst::Element,
        transition: gst::StateChange,
    ) -> Result<gst::StateChangeSuccess, gst::StateChangeError> {
        use gst::StateChange;
        #[allow(clippy::single_match)]
        match transition {
            // Act on NULL to Ready transition
            StateChange::NullToReady => {
                let mut state = self
                    .state
                    .lock()
                    .expect("Failed to lock state in framealigner");
                // TODO: In the future extrinsics should come from the stream instead of file
                gst_fixme!(
                    CAT,
                    "Extrinsics and Intrinsics are read from file. Should be changed."
                );
                // Read parameters from file.
                let path = &state.calib_file;
                if let Err(e) = self.get_parameters(path.to_string(), &mut *state) {
                    gst_error!(CAT, "Properties could not be read from file. {:?}", e);
                }
                gst_debug!(CAT, "State after get_parameters: {:?}", state);
            }
            _ => (),
        }
        self.parent_change_state(element, transition)
    }
}

impl ObjectSubclass for FrameAligner {
    const NAME: &'static str = "framealigner";
    type ParentType = gst_base::BaseTransform;
    type Instance = gst::subclass::ElementInstanceStruct<Self>;
    type Class = subclass::simple::ClassStruct<Self>;
    glib_object_subclass!();
    // Class init for FrameAligner
    fn class_init(klass: &mut subclass::simple::ClassStruct<Self>) {
        gst_debug!(CAT, "class_init");
        klass.set_metadata(
            "Frame Aligner",
            "(In-place transform/RGB-D",
            "Align depth and color streas from video/rgbd stream",
            "Joao Alves <joao.alves@aivero.com>",
        );
        klass.install_properties(&PROPERTIES);

        // Create src pad template with `video/rgbd` caps
        let src_caps = gst::Caps::new_simple("video/rgbd", &[]);
        // Create sink pad template with `video/rgbd` caps
        let sink_caps = gst::Caps::new_simple("video/rgbd", &[]);

        // Add sink pad template
        klass.add_pad_template(
            gst::PadTemplate::new(
                "sink",
                gst::PadDirection::Sink,
                gst::PadPresence::Always,
                &sink_caps,
            )
            .expect("Could not add sink pad template in framealigner"),
        );
        // Add src pad template
        klass.add_pad_template(
            gst::PadTemplate::new(
                "src",
                gst::PadDirection::Src,
                gst::PadPresence::Always,
                &src_caps,
            )
            .expect("Could not add src pad template in framealigner"),
        );

        klass.configure(
            gst_base::subclass::BaseTransformMode::AlwaysInPlace,
            false,
            false,
        );
    }
    //Initialize state
    fn new() -> Self {
        Self {
            state: Mutex::new(FrameAlignerState {
                depth_factor: DEFAULT_DEPTH_FACTOR,
                video_info: None,
                calib_file: "calib/rs728312070140.yaml".to_string(),
                rotation: Matrix3::new(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
                k_color: Matrix3::new(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
                k_depth: Matrix3::new(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
                translation: Matrix3x1::new(0.0, 0.0, 0.0),
                dump: false,
            }),
        }
    }
}

impl ObjectImpl for FrameAligner {
    glib_object_impl!();
    /// Set properties of given object
    /// # Arguments
    /// * `obj` - Object on which to set the properties.
    /// * `id` - Object properties index in PROPERTIES struct
    /// * `value` - Properties for the given object.
    fn set_property(&self, obj: &glib::Object, id: usize, value: &glib::Value) {
        let mut state = self
            .state
            .lock()
            .expect("Failed to lock state in FrameAligner");

        let element = obj
            .downcast_ref::<gst_base::BaseTransform>()
            .expect("Failed to cast framealigner `obj` to `gst_base::BaseTransform`.");

        let property = &PROPERTIES[id];
        match *property {
            subclass::Property("depth_factor", ..) => {
                let depth_factor = value
                    .get_some()
                    .expect("Failed to set property `depth_factor` on framealigner.");
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `depth_factor` to {}",
                    depth_factor
                );
                state.depth_factor = depth_factor;
            }
            subclass::Property("calib_file", ..) => {
                let calib_file = value
                .get()
                .unwrap_or_else(|err| {
                    panic!("framealigner: Failed to set property `calib_file` due to incorrect type: {:?}", err)
                })
                .unwrap_or_else(|| "calib.txt".to_string());
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `calib_file` to {}",
                    calib_file
                );
                state.calib_file = calib_file;
            }
            _ => unimplemented!("Property is not implemented"),
        };
    }
    /// Get properties of given object. Called whenever a value of a property is read. It can
    /// be called at any time from any thread
    /// # Arguments
    /// * `obj` - Object on which to get the properties.
    /// * `id` - Object properties index in PROPERTIES struct
    /// # Returns
    /// *`Value` - Properties of given object.
    fn get_property(&self, _obj: &glib::Object, id: usize) -> Result<glib::Value, ()> {
        let state = &self.state.lock().unwrap();

        let prop = &PROPERTIES[id];
        match *prop {
            subclass::Property("depth_factor", ..) => Ok(state.depth_factor.to_value()),
            subclass::Property("calib_file", ..) => Ok(state.calib_file.to_value()),
            _ => Err(()),
        }
    }
}

impl BaseTransformImpl for FrameAligner {
    fn set_caps(
        &self,
        _element: &gst_base::BaseTransform,
        sink_caps: &gst::Caps,
        _src_caps: &gst::Caps,
    ) -> Result<(), gst::LoggableError> {
        gst_debug!(CAT, "set_caps - sink_caps: {:?}", sink_caps);
        // Get sink and src caps
        let sink_caps = sink_caps
            .get_structure(0)
            .expect("No CAPS yet on framealigner");

        // Create video info from sink caps
        let depth_video_info = rgbd::get_video_info(sink_caps, "depth")?;
        let color_video_info = rgbd::get_video_info(sink_caps, "depth")?;
        // Lock the state
        let state = &mut *self
            .state
            .lock()
            .expect("Failed to lock state in framealigner");
        // Allocate correct size for each sink and src block
        // For the sink we need buffer that are big enough to contain the depth frame
        let sink_blocksize = depth_video_info.size();
        let src_blocksize = depth_video_info.size();

        // Put these into the element's state
        state.video_info = Some(CapsVideoInfo::new(
            depth_video_info,
            color_video_info,
            sink_blocksize as usize,
            src_blocksize as usize,
        ));
        Ok(())
    }

    fn transform_size(
        &self,
        element: &gst_base::BaseTransform,
        direction: gst::PadDirection,
        _caps: &gst::Caps,
        _size: usize,
        _other_caps: &gst::Caps,
    ) -> Option<usize> {
        // Get video info about the incoming streams
        let video_info = &self
            .state
            .lock()
            .expect("Failed to lock state in framealigner")
            .video_info;

        // Set blocksize based on the pad direction
        match video_info.as_ref() {
            Some(vi) => match direction {
                gst::PadDirection::Src => Some(vi.sink_blocksize),
                _ => Some(vi.src_blocksize),
            },
            None => {
                gst_element_error!(
                    element,
                    gst::CoreError::Negotiation,
                    ["Have no video_info yet"]
                );
                None
            }
        }
    }

    fn transform_ip(
        &self,
        _element: &gst_base::BaseTransform,
        buffer_ref: &mut gst::BufferRef,
    ) -> Result<gst::FlowSuccess, gst::FlowError> {
        // Lock the state
        let state = self
            .state
            .lock()
            .expect("Failed to lock state in framealigner");

        {
            let video_info = &state.video_info.as_ref().unwrap().depth_video_info;
            // Read depth information from the input buffer into the frame
            let frame_height = video_info.height() as usize;
            let frame_width = video_info.width() as usize;
            // Create depth image frame from the input buffer together with corresponding data byte array
            let mut input_frame =
                gst_video::VideoFrameRef::from_buffer_ref_writable(buffer_ref, video_info)
                    .map_err(|_| {
                        GstFrameAlignerError::new("Failed to map input buffer readable")
                    })?;
            // Plane data
            let plane_data = input_frame
                .plane_data_mut(0)
                .expect("Could not plane input data");
            // Create depth frame from data
            let depth_frame = rgbd::to_depth_buffer_mut(plane_data)?;
            // Write new depth data into buffer
            self.get_new_depth_image(&state, depth_frame, frame_width, frame_height)
        }

        Ok(gst::FlowSuccess::Ok)
    }
}

// Register the plugin
pub fn register(plugin: &gst::Plugin) -> Result<(), glib::BoolError> {
    gst::Element::register(
        Some(plugin),
        "framealigner",
        gst::Rank::None,
        FrameAligner::get_type(),
    )
}
