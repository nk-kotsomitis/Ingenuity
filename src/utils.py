# Copyright (C) 2025 Ingenuity
# Licensed under the GNU General Public License v3.0

import os
import shutil
import yaml
import ctypes
from logger import sim_logger
import json


def parse_configuration_file(configuration_file):
    conf = {}

    with open(configuration_file, "r") as file:
        config = yaml.safe_load(file)

    # -------------------------- recent_projects ---------------------------
    recent_projects = config.get("recent_projects", None)

    if recent_projects:
        conf['recent_projects'] = []
        for prg in recent_projects:
            conf['recent_projects'].append(os.path.abspath(prg))
        sim_logger.info(f"recent_projects: {conf['recent_projects']}")

    return conf


def parse_project_file(project_filename):
    conf = {}

    with open(project_filename, "r") as file:
        config = yaml.safe_load(file)

    # Base file name
    conf['name'] = os.path.basename(project_filename)
    # Base absolute path
    conf['path'] = os.path.normpath(os.path.dirname(project_filename))

    # -------------------------- main ---------------------------
    conf['output_directory'] = config.get('main', {}).get('output_directory', '')
    if not conf['output_directory']:
        return {}
    if not os.path.isabs(conf['output_directory']):
        conf['output_directory'] = os.path.join(conf['path'], conf['output_directory'])
    sim_logger.info(f"Project's settings applied successfully: output_directory={conf['output_directory']}")

    conf['model_file'] = config.get('main', {}).get('model_file', '')
    if not conf['model_file']:
        return {}
    if not os.path.isabs(conf['model_file']):
        conf['model_file'] = os.path.join(conf['path'], conf['model_file'])
    sim_logger.info(f"Project's settings applied successfully: model_file={conf['model_file']}")

    # -------------------------- device ---------------------------
    conf['manufacturer'] = config.get('device', {}).get('manufacturer', '')
    if not conf['manufacturer']:
        return {}
    sim_logger.info(f"Project's settings applied successfully: manufacturer={conf['manufacturer']}")

    conf['dev_model'] = config.get('device', {}).get('dev_model', '')
    if not conf['dev_model']:
        return {}
    sim_logger.info(f"Settings applied successfully: dev_model={conf['dev_model']}")

    conf['toolchain_path'] = config.get('device', {}).get('toolchain_path', '')
    if not conf['toolchain_path']:
        return {}
    conf['toolchain_path'] = os.path.abspath(conf['toolchain_path'])
    sim_logger.info(f"Settings applied successfully: toolchain_path={conf['toolchain_path']}")

    # -------------------------- validator ---------------------------
    conf['input_dataset'] = config.get('validator', {}).get('input_dataset', '')
    if not conf['input_dataset']:
        return {}
    if not os.path.isabs(conf['input_dataset']):
        conf['input_dataset'] = os.path.join(conf['path'], conf['input_dataset'])
    sim_logger.info(f"Project's settings applied successfully: input_dataset={conf['input_dataset']}")

    conf['output_dataset'] = config.get('validator', {}).get('output_dataset', '')
    if not conf['output_dataset']:
        return {}
    if not os.path.isabs(conf['output_dataset']):
        conf['output_dataset'] = os.path.join(conf['path'], conf['output_dataset'])
    sim_logger.info(f"Project's settings applied successfully: output_dataset={conf['output_dataset']}")

    # -------------------------- settings ---------------------------

    conf['inference_rate'] = config.get('settings', {}).get('inference_rate', '')
    if not conf['inference_rate']:
        return {}
    sim_logger.info(f"Project's settings applied successfully: inference_rate={conf['inference_rate']}")

    conf['inferences_n'] = config.get('settings', {}).get('inferences_n', '')
    if not conf['inferences_n']:
        return {}
    sim_logger.info(f"Project's settings applied successfully: inferences_n={conf['inferences_n']}")

    conf['show_graphs'] = config.get('settings', {}).get('show_graphs', None)
    if conf['show_graphs'] is None:
        return {}
    sim_logger.info(f"Project's settings applied successfully: show_graphs={conf['show_graphs']}")

    return conf


def show_conf_info_windows(text):
    MB_ICONINFORMATION = 0x40
    ctypes.windll.user32.MessageBoxW(0, text, "Info", MB_ICONINFORMATION)


def show_conf_error_windows(text):
    MB_ICONERROR = 0x10
    ctypes.windll.user32.MessageBoxW(0, text, "Error", MB_ICONERROR)


def show_conf_warn_windows(text):
    MB_ICONWARNING = 0x30
    ctypes.windll.user32.MessageBoxW(0, text, "Warning", MB_ICONWARNING)


def generate_file(file_path, content):
    folder_path = os.path.dirname(file_path)
    if folder_path and not os.path.exists(folder_path):
        os.makedirs(folder_path)

    with open(file_path, "w") as file:
        file.write(content)
        sim_logger.info(f"Generated: {file_path}")


def get_value_from_json(file_path, key):

    # Open and load the JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Retrieve the key value
    idf_selected_id = data.get(key)

    return idf_selected_id


def open_file_or_folder(file_path):
    file_path = os.path.abspath(file_path)
    folder_path = os.path.dirname(file_path)
    try:
        os.startfile(file_path)
    except (OSError, AttributeError):
        try:
            os.startfile(folder_path)
        except Exception as e:
            sim_logger.error(f"Failed to open folder: {e}")


def open_folder(file_path):
    file_path = os.path.abspath(file_path)
    folder_path = os.path.dirname(file_path)

    try:
        os.startfile(folder_path)
    except Exception as e:
        sim_logger.error(f"Failed to open folder: {e}")


def copy_folder_skip_existing(source_folder, destination_path):
    # Ensure the destination folder exists
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

    # Walk through the source folder
    for root, dirs, files in os.walk(source_folder):
        # Construct the destination folder path
        relative_path = os.path.relpath(root, source_folder)
        dest_dir = os.path.join(destination_path, relative_path)

        # Ensure all subdirectories exist in the destination
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        # Copy each file, skipping if it exists
        for file in files:
            src_file = os.path.join(root, file)
            dest_file = os.path.join(dest_dir, file)
            if not os.path.exists(dest_file):  # Skip if the file exists
                shutil.copy2(src_file, dest_file)  # copy2 preserves metadata
                sim_logger.info(f"Copied file: {dest_file}")


def convert_c_arrays_to_code(c_arrays_list, name):
    code = ""
    code_ptr = ""
    for i, c_array in enumerate(c_arrays_list):
        array_code = ", ".join(f"{x}" for x in c_array)
        code += f"""\
const int8_t {name}_{i}[] = {'{'}{array_code}{'}'};
"""
        code_ptr += f"{name}_{i}, "
    else:
        code += f"""

const int8_t *dataset_{name}s[] = {'{'}{code_ptr}{'}'};

        """
    return code



