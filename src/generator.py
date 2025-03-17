# Copyright (C) 2025 Ingenuity
# Licensed under the GNU General Public License v3.0

from configuration import *
from files import EXAMPLE_MAIN_C, NN_MODEL_C, NN_C, NN_H, NN_API_H, NN_ASM
import utils
import os


def _convert_c_array_to_code(name, data_type, c_array_list):
    """

    :param name:
    :param data_type:
    :param c_array_list:
    :return:
    """
    # TODO: Check data type and set accordingly...
    # float --> {x:.8f}
    # int --> {x}
    c_array = ", ".join(f"{x}" for x in c_array_list)

    # C Code
    code = f"""\
{data_type} {name}[] __attribute__((aligned(CARRAY_ALIGN))) = {{{c_array}}};
"""
    return code


def _convert_definitions_to_code(definitions):
    defines_list = []

    for key, val in definitions.items():
        defines_list.append(f"#define {key} {val}")

    # Join the defines_list with new line characters
    defines_code = "\n".join(defines_list)

    code = f"""\
{defines_code}
"""

    return code


def _convert_typedefs_to_code(typedefs):
    typedefs_list = []

    for key, val in typedefs.items():
        typedefs_list.append(f"typedef {val} {key};")

    # Join the defines_list with new line characters
    typedefs_code = "\n".join(typedefs_list)

    code = f"""\
{typedefs_code}
"""
    return code


def generate_public_files(buffers, definitions_dict, typedefs_dict, output_path):
    c_array_w = buffers[0]
    c_array_b = buffers[1]
    c_array_sm = buffers[2]
    c_array_zf = buffers[3]
    c_array_a = buffers[4]

    # Definitions
    definitions_code = _convert_definitions_to_code(definitions=definitions_dict)

    # Typedefs
    typedefs_code = _convert_typedefs_to_code(typedefs=typedefs_dict)

    buffers_code = ''
    buffers_code += _convert_c_array_to_code(name='c_array_w',
                                             data_type=DATA_TYPE_DICT_TO_TYPEDEFS_MAP['c_array_w'],
                                             c_array_list=c_array_w)

    buffers_code += _convert_c_array_to_code(name='c_array_b',
                                             data_type=DATA_TYPE_DICT_TO_TYPEDEFS_MAP['c_array_b'],
                                             c_array_list=c_array_b)

    buffers_code += _convert_c_array_to_code(name='c_array_sm',
                                             data_type=DATA_TYPE_DICT_TO_TYPEDEFS_MAP['c_array_sm'],
                                             c_array_list=c_array_sm)

    buffers_code += _convert_c_array_to_code(name='c_array_zf',
                                             data_type=DATA_TYPE_DICT_TO_TYPEDEFS_MAP['c_array_zf'],
                                             c_array_list=c_array_zf)

    buffers_code += _convert_c_array_to_code(name='c_array_a',
                                             data_type=DATA_TYPE_DICT_TO_TYPEDEFS_MAP['c_array_a'],
                                             c_array_list=c_array_a)

    # App main
    example_main_c_file = EXAMPLE_MAIN_C
    # Model file
    model_c_file = NN_MODEL_C.replace("{c_arrays}", str(buffers_code))
    # NN c files
    nn_c_file = NN_C
    # NN header file
    nn_header_file = NN_H.replace("{definitions}", str(definitions_code)).replace("{typedefs}", str(typedefs_code))
    # NN API header file
    api_header_file = (NN_API_H
                       .replace("{input_length}", str(definitions_dict["INPUT_LENGTH"]))
                       .replace("{output_length}", str(definitions_dict["OUTPUT_LENGTH"])))

    # Generate files
    utils.generate_file(os.path.abspath(os.path.join(output_path, PATH_MAIN, FILENAME_MAIN_C)), example_main_c_file)
    utils.generate_file(os.path.abspath(os.path.join(output_path, PATH_SRC, FILENAME_MODEL_C)), model_c_file)
    utils.generate_file(os.path.abspath(os.path.join(output_path, PATH_SRC, FILENAME_NN_C)), nn_c_file)
    utils.generate_file(os.path.abspath(os.path.join(output_path, PATH_SRC, FILENAME_NN_ASM)), NN_ASM)
    utils.generate_file(os.path.abspath(os.path.join(output_path, PATH_INCLUDE, FILENAME_NN_H)), nn_header_file)
    utils.generate_file(os.path.abspath(os.path.join(output_path, PATH_INCLUDE, FILENAME_API_H)), api_header_file)
