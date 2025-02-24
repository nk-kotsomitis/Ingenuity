
<div align="center">
  <img src="./assets/logo_ingenuity.png" alt="ingenuity." width="200"/>
</div>
 


AIngenuity is designed to benchmark the inference performance of ML models on embedded
devices using its own inference engine.
Benchmarking a quantized TFLite model typically involves multiple steps, including building
and deploying the model on the device, as well as designing and implementing benchmarking
test suites. Ingenuity automates this entire process with a single click, seamlessly bridging the
gap between model quantization and benchmarking.


<div align="center">
  <img src="./assets/screenshot_1.png" alt="software_screenshot" width="800"/>
</div>

Through the Graphical User Interface (GUI), benchmark metrics such as inference latency,
memory usage, and quantization accuracy can be easily monitored within seconds. This allows
users to benchmark their models quickly and efficiently.


Before execution, the project file must be properly configured with the validator's input
and output representative datasets, as well as inference settings such as the
inference rate and the number of inferences for benchmarking. Once
configured, a single click automates the entire process—handling file
generation, project building, flashing, and real-time monitoring of benchmarking
results. After the benchmark is completed, the generated ESP-IDF project folder can be used to integrate
the benchmarking setup with the user’s application code.