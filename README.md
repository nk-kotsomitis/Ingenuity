
<div align="center">
  <img src="./assets/logo_ingenuity.png" alt="ingenuity." width="200"/>
</div>
<br>
<br>
<br>

![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)  

## Introduction
<b>Ingenuity</b> is designed to benchmark the inference performance of ML models on embedded
devices using its own inference engine.
Benchmarking a quantized TFLite model typically involves multiple steps, including building
and deploying the model on the device, as well as designing and implementing benchmarking
test suites. Ingenuity automates this entire process with a single click, seamlessly bridging the
gap between model quantization and benchmarking.
<br>
<br>
<br>
<div align="center">
  <img src="./assets/screenshot_1.png" alt="software_screenshot" width="800"/>
</div>
<br>
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
<br>
<br>
<br>
## Getting-started
<p align="left">
  <img src="./assets/button_home.png" alt="home_button" width="50" style="vertical-align: middle; margin-right: 10px;"/>
  The <b>Home</b> button allows you to create a new project or load an existing one. To create a new project, follow these steps: <br>
1. Click the Home button and select "New Project..." <br>
2. In the New Project window, choose the folder where the project will be created. <br>
3. Enter a name for the new project and click OK—this will open a file explorer window.<br>
4. Locate and open the .yaml file, then edit it with the appropriate parameters.<br>
</p>
<br>
<br>
<div align="center">
  <img src="./assets/screenshot_2.png" alt="yaml_file" width="600"/>
</div>
<br>
<br>
<p align="left">
  <img src="./assets/button_execution.png" alt="execution_button" width="50" style="vertical-align: middle; margin-right: 10px;"/>
  The <b>Execution</b> button starts the one-click benchmarking process. It becomes enabled after a project is loaded and consists of the following steps: <br>
1.	Generates the <b>ESP-IDF project</b>, including the Ingenuity inference engine library. <br>
2.	Creates the main C file and the validator files required for benchmarking. <br>
3.	Builds the project and flashes it to the device. <br>
4.	Monitors the device output and displays the benchmark results. <br>
</p>
<br>
<br>
<p align="left">
  <img src="./assets/button_settings.png" alt="settings_button" width="50" style="vertical-align: middle; margin-right: 10px;"/>
  The <b>Settings</b> button opens the settings window, allowing you to configure benchmark parameters. <br>
<b>Note</b>: These parameters can also be modified directly in the project file before loading the project.
</p>
<br>
<br>
The <b>main panel</b> displays benchmark results for the following metrics: <br>
1.	<b>Latency</b> – Inference latency measured in MCU cycles. <br>
2.	<b>Accuracy</b> – Accuracy of the inference engine, calculated by comparing the actual output with the representative output dataset. <br>
3.	<b>Memory</b> – <br>
&nbsp;&nbsp; o	The first table shows the device's overall memory usage. <br>
&nbsp;&nbsp; o	The second table shows the inference engine’s memory usage as a separate component. <br>
4.	<b>Energy</b> – This feature is currently under development. <br>

## License  
This project is licensed under the **GNU General Public License v3.0**.  
See the [LICENSE](LICENSE) file for details.  

