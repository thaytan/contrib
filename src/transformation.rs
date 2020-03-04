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

/// Transformation in 3D.
#[derive(Debug, Default, PartialEq, Clone)]
pub struct Transformation {
    /// Translation.
    pub translation: Translation,
    /// Rotation.
    pub rotation: RotationMatrix,
}

impl Transformation {
    /// Create a new Transformation from `translation` and `rotation`.
    ///
    /// # Arguments
    /// * `translation` - Translation component of the Transformation.
    /// * `rotation` - RotationMatrix defining the rotation of the Transformation.
    ///
    /// # Returns
    /// * Newly created Transformaion.
    pub fn new(translation: Translation, rotation: RotationMatrix) -> Self {
        Self {
            translation,
            rotation,
        }
    }

    /// Inverts Transformation such as it descibes pose of `source` in `target` coordinate frame.
    pub fn inverse(&self) -> Self {
        let t = &self.translation;
        let r_inv = self.rotation.inverse();
        Self {
            translation: Translation {
                x: -(r_inv.r11 * t.x + r_inv.r12 * t.y + r_inv.r13 * t.z),
                y: -(r_inv.r21 * t.x + r_inv.r22 * t.y + r_inv.r23 * t.z),
                z: -(r_inv.r31 * t.x + r_inv.r32 * t.y + r_inv.r33 * t.z),
            },
            rotation: r_inv,
        }
    }
}

/// Translation vector, in metres.
#[derive(Debug, Default, PartialEq, Clone)]
pub struct Translation {
    /// Displacement along x axis.
    pub x: f32,
    /// Displacement along y axis.
    pub y: f32,
    /// Displacement along z axis.
    pub z: f32,
}

impl Translation {
    /// Create a new Translation vector.
    ///
    /// # Arguments
    /// * `x` - Displacement along x axis.
    /// * `y` - Displacement along y axis.
    /// * `z` - Displacement along z axis.
    ///
    /// # Returns
    /// * Newly created Translation.
    pub fn new(x: f32, y: f32, z: f32) -> Self {
        Self { x, y, z }
    }
}

impl From<[f32; 3]> for Translation {
    /// Implements conversion from slice into Translation.
    fn from(slice: [f32; 3]) -> Self {
        Self {
            x: slice[0],
            y: slice[1],
            z: slice[2],
        }
    }
}

/// Rotation matrix.
#[derive(Debug, PartialEq, Clone)]
pub struct RotationMatrix {
    ///  Entry of row 1 and column 1.
    pub r11: f32,
    ///  Entry of row 1 and column 2.
    pub r12: f32,
    ///  Entry of row 1 and column 3.
    pub r13: f32,
    ///  Entry of row 2 and column 1.
    pub r21: f32,
    ///  Entry of row 2 and column 2.
    pub r22: f32,
    ///  Entry of row 2 and column 3.
    pub r23: f32,
    ///  Entry of row 3 and column 1.
    pub r31: f32,
    ///  Entry of row 3 and column 2.
    pub r32: f32,
    ///  Entry of row 3 and column 3.
    pub r33: f32,
}

impl RotationMatrix {
    /// Create a new RotationMatrix.
    ///
    /// # Arguments
    /// * `r11` - Entry of row 1 and column 1.
    /// * `r12` - Entry of row 1 and column 2.
    /// * `r13` - Entry of row 1 and column 3.
    /// * `r21` - Entry of row 2 and column 1.
    /// * `r22` - Entry of row 2 and column 2.
    /// * `r23` - Entry of row 2 and column 3.
    /// * `r31` - Entry of row 3 and column 1.
    /// * `r32` - Entry of row 3 and column 2.
    /// * `r33` - Entry of row 3 and column 3.
    ///
    /// # Returns
    /// * Newly created RotationMatrix.
    pub fn new(
        r11: f32,
        r12: f32,
        r13: f32,
        r21: f32,
        r22: f32,
        r23: f32,
        r31: f32,
        r32: f32,
        r33: f32,
    ) -> Self {
        Self {
            r11,
            r12,
            r13,
            r21,
            r22,
            r23,
            r31,
            r32,
            r33,
        }
    }

    /// Inverts RotationMatrix such as it descibes orientation of `source` from the `target` coordinate frame.
    pub fn inverse(&self) -> Self {
        Self {
            r11: self.r11,
            r12: self.r21,
            r13: self.r31,
            r21: self.r12,
            r22: self.r22,
            r23: self.r32,
            r31: self.r13,
            r32: self.r23,
            r33: self.r33,
        }
    }
}

impl From<[f32; 9]> for RotationMatrix {
    /// Implements conversion from slice into RotationMatrix.
    fn from(slice: [f32; 9]) -> Self {
        Self {
            r11: slice[0],
            r12: slice[1],
            r13: slice[2],
            r21: slice[3],
            r22: slice[4],
            r23: slice[5],
            r31: slice[6],
            r32: slice[7],
            r33: slice[8],
        }
    }
}

impl Default for RotationMatrix {
    /// Default implementation for RotationMatrix that returns identity, i.e. no rotation.
    fn default() -> Self {
        Self {
            r11: 1.0,
            r12: 0.0,
            r13: 0.0,
            r21: 0.0,
            r22: 1.0,
            r23: 0.0,
            r31: 0.0,
            r32: 0.0,
            r33: 1.0,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use rand::random;
    const TEST_ITERATIONS: usize = 100;
    const ROUNDING_ERROR_LIMIT: f32 = 0.000001; // 1 um

    fn initialise_random_transformation() -> Transformation {
        Transformation {
            translation: Translation {
                x: random(),
                y: random(),
                z: random(),
            },
            // TODO [not too important]: Generate random rotation matrix that is valid so that it can be properly tested.
            rotation: RotationMatrix::default(),
        }
    }

    #[test]
    fn inverse_rotation_matrix() {
        for _ in 0..TEST_ITERATIONS {
            let original = RotationMatrix {
                r11: random(),
                r12: random(),
                r13: random(),
                r21: random(),
                r22: random(),
                r23: random(),
                r31: random(),
                r32: random(),
                r33: random(),
            };

            let inverted = original.inverse();
            assert_eq!(inverted.r11, original.r11);
            assert_eq!(inverted.r12, original.r21);
            assert_eq!(inverted.r13, original.r31);
            assert_eq!(inverted.r21, original.r12);
            assert_eq!(inverted.r22, original.r22);
            assert_eq!(inverted.r23, original.r32);
            assert_eq!(inverted.r31, original.r13);
            assert_eq!(inverted.r32, original.r23);
            assert_eq!(inverted.r33, original.r33);
        }
    }

    #[test]
    fn inverse_loop() {
        for _ in 0..TEST_ITERATIONS {
            let transformation = initialise_random_transformation();
            let transformation_assert_clone = transformation.clone();

            let inverted = transformation.inverse();
            let original = inverted.inverse();

            assert_eq!(original.rotation, transformation_assert_clone.rotation);
            // Due to f32 rounding error
            assert!(
                (original.translation.x - transformation_assert_clone.translation.x).abs()
                    < ROUNDING_ERROR_LIMIT
            );
            assert!(
                (original.translation.y - transformation_assert_clone.translation.y).abs()
                    < ROUNDING_ERROR_LIMIT
            );
            assert!(
                (original.translation.z - transformation_assert_clone.translation.z).abs()
                    < ROUNDING_ERROR_LIMIT
            );
        }
    }

    #[test]
    fn translation_from_slice() {
        let translation_slice = [1.1, 2.2, 3.3];

        let translation = Translation::from(translation_slice);

        assert_eq!(translation.x, 1.1);
        assert_eq!(translation.y, 2.2);
        assert_eq!(translation.z, 3.3);
    }

    #[test]
    fn rotation_from_slice() {
        let rotation_matrix_slice = [1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9];

        let rotation_matrix = RotationMatrix::from(rotation_matrix_slice);

        assert_eq!(rotation_matrix.r11, 1.1);
        assert_eq!(rotation_matrix.r12, 2.2);
        assert_eq!(rotation_matrix.r13, 3.3);
        assert_eq!(rotation_matrix.r21, 4.4);
        assert_eq!(rotation_matrix.r22, 5.5);
        assert_eq!(rotation_matrix.r23, 6.6);
        assert_eq!(rotation_matrix.r31, 7.7);
        assert_eq!(rotation_matrix.r32, 8.8);
        assert_eq!(rotation_matrix.r33, 9.9);
    }
}
