/// Helper structs that contains information about what streams are enabled
pub(crate) struct EnabledStreams {
    pub(crate) depth: bool,
    pub(crate) infra1: bool,
    pub(crate) infra2: bool,
    pub(crate) color: bool,
}

impl EnabledStreams {
    /// Determines whether at least one stream is enabled.
    ///
    /// # Returns
    /// * `true` if at least one stream is enabled.
    /// * `false` if no stream is enabled.
    pub(crate) fn any(&self) -> bool {
        if self.depth || self.infra1 || self.infra2 || self.color {
            true
        } else {
            false
        }
    }

    /// Determines whether there are any conflict between `enabled_streams` and
    /// `available_streams`
    ///
    /// # Arguments
    /// * `enabled_streams` - The streams that are enabled.
    /// * `available_streams` - The streams that are available.
    ///
    /// # Returns
    /// * `Vec<&str>` of conflicting streams, which is empty if there is no conflict.
    pub(crate) fn get_conflicts(
        enabled_streams: &EnabledStreams,
        available_streams: &EnabledStreams,
    ) -> Vec<&'static str> {
        let mut conflicting_streams: Vec<&str> = Vec::new();
        if enabled_streams.depth && !available_streams.depth {
            conflicting_streams.push("depth");
        }
        if enabled_streams.infra1 && !available_streams.infra1 {
            conflicting_streams.push("infra1");
        }
        if enabled_streams.infra2 && !available_streams.infra2 {
            conflicting_streams.push("infra2");
        }
        if enabled_streams.color && !available_streams.color {
            conflicting_streams.push("color");
        }
        conflicting_streams
    }
}
