# Copyright (C) 2025 Ingenuity
# Licensed under the GNU General Public License v3.0

import numpy as np

VERSION_INGENUITY = "1.0.2"
BUILD_INGENUITY = "14 August 2025"

# Logger output path
PATH_LOGS = './logs'
# Logger filename
LOG_FILENAME = 'ingenuity.log'
# Configuration file
CONFIGURATION_FILE = "configuration.yaml"
# Project file template
TEMPLATE_PROJECT_FILE = "project_file.yaml"

# ESP Toolchain Configuration
ESP_IDF_JSON_FILE = 'esp_idf.json'
ESP_IDF_JSON_FILE_KEY = 'idfSelectedId'

# Project template paths
PATH_ESP32S3_PROJECT_TEMPLATE = "esp32s3"
PATH_SRC = "components/nn"
PATH_INCLUDE = "components/nn/include"
PATH_MAIN = "main"

# Project template filenames
FILENAME_MAIN_C = "main.c"
FILENAME_MODEL_C = "model.c"
FILENAME_NN_C = "nn.c"
FILENAME_NN_H = "nn.h"
FILENAME_API_H = "NN_lite_API.h"
FILENAME_NN_ASM = "nn_asm.s"
FILENAME_VALIDATION_C = "validation.c"
FILENAME_VALIDATION_H = "validation.h"

# Flags - TO BE DELETED
LUT_VERSION = True

NP_TYPE_TO_C_TYPE_MAP = {np.float32: 'float',
                         np.int8: 'int8_t', np.int16: 'int16_t', np.int32: 'int32_t', np.int64: 'int64_t',
                         np.uint8: 'uint8_t', np.uint16: 'uint16_t', np.uint32: 'uint32_t', np.uint64: 'uint64_t'}

DATA_TYPE_DICT_TO_TYPEDEFS_MAP = {'c_array_w': 'Weights_t',
                                  'c_array_b': 'Bias_t',
                                  'c_array_a': 'In_out_t',
                                  'c_array_sm': 'Shapes_m_t',
                                  'c_array_zf': 'Zero_actf_t',
                                  'c_array_f': 'Scales_t',
                                  'conversion': 'In_out_float_t'}
