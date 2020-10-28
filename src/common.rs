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

#[cfg(test)]
pub(crate) mod tests {
    /// Return true if `a` and `b` are nearly equal.
    /// Adapted from https://floating-point-gui.de/errors/comparison
    pub(crate) fn nearly_equal_f32(a: f32, b: f32) -> bool {
        let diff = (a - b).abs();

        #[allow(clippy::float_cmp)]
        let are_equal = a == b;

        if are_equal {
            true
        } else if a == 0.0 || b == 0.0 || diff < std::f32::MIN_POSITIVE {
            diff < (std::f32::EPSILON * std::f32::MIN_POSITIVE)
        } else {
            (diff / (a.abs() + b.abs()).min(std::f32::MAX)) < std::f32::EPSILON
        }
    }
}
