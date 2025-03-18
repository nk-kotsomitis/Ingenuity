# ToyCar Example

## Model
This example demonstrates a pre-trained model from MLPerf Tiny, specifically the Deep Autoencoder for Anomaly Detection in machine operating sounds. The model was trained using the ToyADMOS dataset and is designed for detecting anomalies in machine sounds. The model used in this example is a quantized INT8 version with integer input and output:

📌 model_ToyCar_quant_fullint_micro_intio.tflite

## Model Disclaimer
This repository contains a C buffer representation of the model for demonstration purposes with the Ingenuity Inference Engine. The original model is not included in this repository but was sourced from MLPerf Tiny. The model remains the property of its respective creators and is subject to its original licensing terms. For more details about the model, please refer to the official MLPerf documentation:
🔗[MLPerf Trained Models](https://github.com/mlcommons/tiny/tree/master/benchmark/training/anomaly_detection/trained_models)

## How to use
1. Run the Ingenuity software and load the project ToyCar.yaml.
2. Adjust the benchmark settings as needed.
3. Execute the project.

### Important Note
Since the TFLite model is not included in this repository, there is no need to regenerate the inference engine and model. Ensure that the "Generate Inference Engine" option remains **unchecked** in the settings.
