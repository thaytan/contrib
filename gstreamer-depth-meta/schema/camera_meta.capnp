@0xadfd4227f65e6300;

# List of all intrinsics and extrinsics for a calibrated camera setup.
struct CameraMeta {
    # List of intrinsics for each camera.
    intrinsics @0 :List(Intrinsics);
    # List of extrinsics between cameras for a calibrated camera setup.
    extrinsics @1 :List(Extrinsics);
    # Scaling factor of the depth map, in metres.
    depthScale @2 :Float32;
}

# Intrinsics of a specific camera.
struct Intrinsics {
    # Camera for which the intrinsics are valid.
    camera @0 :Text;
    # Focal length of the image plane, as a multiple of pixel width.
    fx @1 :Float32;
    # Focal length of the image plane, as a multiple of pixel height.
    fy @2 :Float32;
    # Horizontal coordinate of the principal point of the image, as a pixel offset from the left edge.
    cx @3 :Float32;
    # Vertical coordinate of the principal point of the image, as a pixel offset from the top edge.
    cy @4 :Float32;

    # Distortion specifier.
    distortion :union {
        # Unknown or unsupported distortion model. Distortion coefficients might are invalid.
        unknown @5 :Void;
        # Image is already rectilinear. No distortion compensation is required.
        none @6 :Void;
        # RealSense Brown-Conrady calibration model.
        rsBrownConrady @7 :RsCoefficients;
        # RealSense equivalent to Brown-Conrady distortion, except that tangential distortion is applied to radially distorted points.
        rsModifiedBrownConrady @8 :RsCoefficients;
        # RealSense equivalent to Brown-Conrady distortion, except that it undistorts image instead of distorting it.
        rsInverseBrownConrady @9 :RsCoefficients;
        # RealSense four parameter Kannala Brandt distortion model.
        rsKannalaBrandt4 @10 :RsCoefficients;
        # RealSense F-Theta fish-eye distortion model.
        rsFTheta @11 :RsCoefficients;
        # K4A Brown-Conrady calibration model.
        k4aBrownConrady @12 :K4aCoefficients;
    }

    # RealSense distortion coefficients. The use of these coefficients depend on the utilised distrortion model.
    struct RsCoefficients {
        # 1st distortion coefficient.
        a1 @0 :Float32;
        # 2nd distortion coefficient.
        a2 @1 :Float32;
        # 3rd distortion coefficient.
        a3 @2 :Float32;
        # 4th distortion coefficient.
        a4 @3 :Float32;
        # 5th distortion coefficient.
        a5 @4 :Float32;
    }
    # K4A distortion coefficients. 
    struct K4aCoefficients {
        # 1st radial distortion coefficient.
        k1 @0 :Float32;
        # 2nd radial distortion coefficient.
        k2 @1 :Float32;
        # 3rd radial distortion coefficient.
        k3 @2 :Float32;
        # 4th radial distortion coefficient.
        k4 @3 :Float32;
        # 5th radial distortion coefficient.
        k5 @4 :Float32;
        # 6th radial distortion coefficient.
        k6 @5 :Float32;
        # 1st tangential distortion coefficient.
        p1 @6 :Float32;
        # 2nd tangential distortion coefficient.
        p2 @7 :Float32;
    }
}

# Extrinsics from source to target coordinate frame.
struct Extrinsics {
    # Source coordinate frame.
    source @0 :Text;
    # Target coordinate frame.
    target @1 :Text;

    # Translation.
    translation @2 :Translation;
    # Rotation.
    # TODO: Replace for union of rotation matrix, quaternions, angle-axis, Euler.
    rotation @3 :RotationMatrix;

    # Translation vector, in metres.
    struct Translation {
        # Displacement along x axis.
        x @0 :Float32;
        # Displacement along y axis.
        y @1 :Float32;
        # Displacement along z axis.
        z @2 :Float32;
    }

    # Rotation matrix.
    struct RotationMatrix {
        # Entry of row 1 and column 1.
        r11 @0 :Float32;
        # Entry of row 1 and column 2.
        r12 @1 :Float32;
        # Entry of row 1 and column 3.
        r13 @2 :Float32;
        # Entry of row 2 and column 1.
        r21 @3 :Float32;
        # Entry of row 2 and column 2.
        r22 @4 :Float32;
        # Entry of row 2 and column 3.
        r23 @5 :Float32;
        # Entry of row 3 and column 1.
        r31 @6 :Float32;
        # Entry of row 3 and column 2.
        r32 @7 :Float32;
        # Entry of row 3 and column 3.
        r33 @8 :Float32;
    }
}
