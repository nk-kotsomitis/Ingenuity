from configuration import *
from converter import model_converter
from buffers import generate_buffers
from generator import generate_public_files
from files import VALIDATION_C, VALIDATION_H
import pandas as pd
import utils
import os


def generate_engine_model(tf_lite_model, output_path):
    settings_inf_rate = 50
    settings_inferences_n = 10

    # Start
    print("Generating engine...")

    # Step 1
    print("De-serializing the TFlite model...")
    model_deserialized = model_converter(tf_lite_model)

    # Step 2
    print("Processing buffers...")
    buffers, definitions_dict, typedefs_dict = generate_buffers(model_deserialized)

    # Step 3
    print("Generating files...")
    generate_public_files(buffers, definitions_dict, typedefs_dict, output_path)

    # Completed
    print("Engine generated successfully!")


def generate_validator(dataset_input, dataset_output):
    # Start
    print("Generating validator...")

    # Step 1
    print("Processing buffers...")
    data_input = pd.read_csv(dataset_input, header=None)
    dataset_output = pd.read_csv(dataset_output, header=None)

    # TODO: For testing
    TEST_PART = True
    TEST_CNT = 1
    cnt = TEST_CNT

    # Step 2
    print("Converting to code...")
    c_arrays_inputs = []
    for index, row in data_input.iterrows():
        c_arrays_inputs.append(row.tolist())
        if TEST_PART:
            if cnt == 0:
                cnt = TEST_CNT
                break
            cnt -= 1

    rows_i = len(c_arrays_inputs)
    columns_i = len(c_arrays_inputs[0])

    c_arrays_outputs = []
    for index, row in dataset_output.iterrows():
        c_arrays_outputs.append(row.tolist())
        if TEST_PART:
            if cnt == 0:
                break
            cnt -= 1
    rows_o = len(c_arrays_outputs)
    columns_o = len(c_arrays_outputs[0])

    # TODO: Check that rows and columns of inputs and outputs are equal
    rows = rows_i = rows_o
    columns = columns_i = columns_o

    # Convert to code
    dataset_input_code = utils.convert_c_arrays_to_code(c_arrays_inputs, 'input')
    dataset_output_code = utils.convert_c_arrays_to_code(c_arrays_outputs, 'output')

    # Replace variables
    validation_c_file = (VALIDATION_C
                         .replace("{dataset_input_code}", str(dataset_input_code))
                         .replace("{dataset_output_code}", str(dataset_output_code)))
    validation_h_file = VALIDATION_H.replace("{dataset_rows}", str(rows)).replace("{dataset_columns}",
                                                                                  str(columns))

    # Step 3
    print("Generating files...")
    utils.generate_file(os.path.abspath(os.path.join(output_path, PATH_MAIN, FILENAME_VALIDATION_C)),
                        validation_c_file)
    utils.generate_file(os.path.abspath(os.path.join(output_path, PATH_MAIN, FILENAME_VALIDATION_H)),
                        validation_h_file)

    # Completed
    print("Validator generated successfully!")


tf_lite_model = "../users_folder/model/model_ToyCar_quant_fullint_micro_intio.tflite"
output_path = "../users_folder/esp32s3_micro_intio"
dat_input = "../users_folder/datasets/rep_dataset_input.csv"
dat_output = "../users_folder/datasets/rep_dataset_output.csv"

generate_engine_model(tf_lite_model, output_path)
# generate_validator(dat_input, dat_output)
