# k4a-rs

Unofficial rust FFI bindings for Azure Kinect SDK. For more information, please visit the official API documentation [here](https://microsoft.github.io/Azure-Kinect-Sensor-SDK).

All structs are implemented to automatically release the memory they use on `drop()`.

> Note: Does not implement API for work with microphone array.

> Note: Several functionalities are not yet implemented. Let me know if you need some of them.

## Environment Variables

#### K4A_ENABLE_LOG_TO_STDOUT
* **0** - Disable logging to stdout.
* **else** - Log all messages to stdout.

#### K4A_ENABLE_LOG_TO_A_FILE
* **0** - Disable logging to a file.
* **~\log\custom.log** - Log all messages to the path and file specified, which must end in ".log" to be considered a valid entry. When enabled, this takes precedence over the value of K4A_ENABLE_LOG_TO_STDOUT.

#### K4A_LOG_LEVEL
* **c** - Log all messages of level *critical* criticality.
* **e** (DEFAULT) - Log all messages of level *error* or higher criticality.
* **w** - Log all messages of level *warning* or higher criticality.
* **i** - Log all messages of level *info* or higher criticality.
* **t** - Log all messages of level *trace* or higher criticality.