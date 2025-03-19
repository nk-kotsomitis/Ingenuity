# Copyright (C) 2025 Ingenuity
# Licensed under the GNU General Public License v3.0

from configuration import *
from converter import model_converter
from buffers import generate_buffers
from generator import generate_public_files
from PySide6.QtCore import QObject, QThread, Signal, QTimer, Qt
from PySide6.QtWidgets import (QDialog, QLineEdit, QSpinBox, QMessageBox, QVBoxLayout, QHBoxLayout, QWidget,
                               QPushButton, QFileDialog, QTabWidget, QLabel, QTabBar, QTextEdit, QScrollArea,
                               QLayout, QMenuBar, QProgressBar, QStatusBar, QMainWindow, QMenu, QCheckBox,
                               QWidgetAction, QDialogButtonBox, QToolTip, QFrame, QApplication, QInputDialog)
from PySide6.QtGui import QImage, QIcon, QAction, QFont, QFontDatabase, QIntValidator, QPixmap, QMovie
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from logger import sim_logger
from files import VALIDATION_C, VALIDATION_H, VALIDATION_MAIN_C
import pandas as pd
import numpy as np
import utils
import os
import yaml
import subprocess
import re
import serial
import serial.tools.list_ports
from logger import console_logger
from stylesheet import STYLESHEET
from console import ProjectWindow, SettingsWindow, AboutWindow, PDFViewer
import sys
from pathlib import Path
import shutil

results_raw = {'cycles': [0], 'histogram': []}
results = {}

BUTTON_WIDTH = 50
BUTTON_HEIGHT = 50


class EngineMain(QMainWindow):

    def __init__(self):
        super().__init__()

        # Get assets path
        if getattr(sys, 'frozen', False):
            self.tmp_base_path = sys._MEIPASS
        else:
            self.tmp_base_path = os.path.abspath(".")

        self.tmp_assets_path = os.path.join(self.tmp_base_path, "assets")
        self.tmp_esp32s3_path = os.path.join(self.tmp_base_path, PATH_ESP32S3_PROJECT_TEMPLATE)

        # --------------------------- Configuration file ----------------

        # TODO: Load configuration file
        # self._load_configuration_file()

        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------

        self.setWindowTitle("ingenuity.")
        self.logo_icon = QIcon(os.path.join(self.tmp_assets_path, "dots_logo.png"))
        self.setWindowIcon(self.logo_icon)
        self.setGeometry(0, 0, 1200, 700)
        self.setMinimumWidth(960)
        self.showMaximized()
        self.setStyleSheet(STYLESHEET)
        self.setObjectName('mainPanel')

        # Configuration file
        self._configuration_file = {'recent_projects': []}
        self._project_file = {}

        # Thread
        self.benchmark_perf = None
        self.thread_engine = None
        self._is_thread_in_progress = False
        self.pdf_window = []

        # Graphs
        self.inferences_n = 0
        self.inference_cnt_hist = 1
        self.inference_cnt_plot = 1
        self.inferences_max = 50
        self.latency_min = float('inf')
        self.latency_max = 0
        self.latency_avg = 0
        self.latency_avg_sum = 0
        self.histograms_last_four = []
        self.histograms_z_max = 0
        self.x_data = []
        self.y_data = []

        # --------------------------- Figures ---------------------------

        # Figure 1 - Latency
        self.figure_1, (self.ax_1a, self.ax_1b) = plt.subplots(1, 2, gridspec_kw={'width_ratios': [4, 1]})
        self.figure_1.subplots_adjust(wspace=0.05, left=0.05, right=0.99)

        # Figure 2 - Accuracy
        self.figure_2 = plt.figure()
        self.ax_2 = self.figure_2.add_subplot(111, projection='3d')
        self.figure_2.subplots_adjust(top=1, bottom=0)

        # Figure 3 - Memory
        self.figure_3, (self.ax_3a, self.ax_3b) = plt.subplots(1, 2, gridspec_kw={'width_ratios': [3, 1]})
        self.figure_3.subplots_adjust(wspace=0.1, left=0.01)

        # Figure 4 - Energy
        self.figure_4, self.ax_4 = plt.subplots()

        self.canvas_1 = FigureCanvas(self.figure_1)
        self.canvas_2 = FigureCanvas(self.figure_2)
        self.canvas_3 = FigureCanvas(self.figure_3)
        self.canvas_4 = FigureCanvas(self.figure_4)

        # --------------------------- Menu Bar ---------------------------

        self.menubar = QMenuBar()
        self.menubar.setFixedWidth(50)

        # self.project_widget = QWidget()
        # self.menubar_layout = QHBoxLayout()
        # self.menubar_layout.setContentsMargins(0, 0, 0, 0)  # Remove padding

        # self.label_test = QLabel("Test")

        # Create the Project menu without text, using an icon
        # icon_action = QAction(QIcon("assets/dots.png"), "", self)
        icon_action = QAction(QIcon(os.path.join(self.tmp_assets_path, "dots.png")), "", self)
        self.menu_project = QMenu(self)
        self.menu_project.setTitle("Home")
        icon_action.setMenu(self.menu_project)
        self.menubar.addAction(icon_action)

        # New...
        action = QAction('New Project...', self)
        action.triggered.connect(self._new_project_file)
        self.menu_project.addAction(action)

        # Open...
        action = QAction('Open Project...', self)
        action.triggered.connect(self._open_project_file)
        self.menu_project.addAction(action)

        # TODO: Recent projects
        # self.menu_recent = QMenu("Open Recent Project", self.menu_project)
        # self.menu_project.addMenu(self.menu_recent)

        # if self._configuration_file.get('recent_projects'):
        #     for project in self._configuration_file['recent_projects']:
        #         action = QAction(project, self)
        #         action.triggered.connect(lambda checked, p=project: self._load_project_file(p))
        #         self.menu_recent.addAction(action)
        # else:
        #     # Add disabled "No Recent Projects" if the list is empty
        #     no_recent_action = QAction("No Recent Projects", self)
        #     no_recent_action.setEnabled(False)
        #     self.menu_recent.addAction(no_recent_action)

        # Project Details
        # self.menu_project.addSeparator()
        # action = QAction('Project Details...', self)
        # # action.triggered.connect()
        # self.menu_project.addAction(action)

        self.menu_project.addSeparator()
        action = QAction('About...', self)
        action.triggered.connect(self.open_about_window)
        self.menu_project.addAction(action)

        # layout = QHBoxLayout()
        # layout.addWidget(self.menubar, stretch=1)
        # self.project_label = QLabel("Test.......................", self)
        # self.project_label.setFixedWidth(50)
        # self.project_label.setStyleSheet("padding-left: 5px;")
        # layout.addWidget(self.project_label, stretch=1)

        # self.menubar_layout.addWidget(self.menubar)
        # self.menubar_layout.addWidget(self.label_test)
        # self.project_widget.setLayout(self.menubar_layout)

        # self.menubar.setCornerWidget(self.project_widget, Qt.Corner.TopLeftCorner)

        # --------------------------- Logo ------------------------------
        font_id = QFontDatabase.addApplicationFont(os.path.join(self.tmp_assets_path, "GeliatExtralight.otf"))
        if font_id != -1:
            self.font_family = QFontDatabase.applicationFontFamilies(font_id)[0]  # Get font name
            custom_font = QFont(self.font_family, 24)
        else:
            custom_font = QFont("Verdana", 24)

        self.logo = QLabel("ingenuity.")
        self.logo.setFont(custom_font)
        self.logo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.logo.setFixedHeight(55)
        # self.logo.setStyleSheet("color: blue;")

        # --------------------------- Buttons ---------------------------
        # Button Run
        self.button_run = QPushButton()
        self.button_run.setObjectName("mainButtons")
        # self.button_run.setObjectName("runButton")
        self.button_run.clicked.connect(self.execution_start)
        self.button_run.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
        self.button_run.setEnabled(False)
        self.button_run_icon_1 = QIcon(os.path.join(self.tmp_assets_path, "play_white.png"))
        self.button_run_icon_2 = QIcon(os.path.join(self.tmp_assets_path, "stop_white.png"))
        self.button_run.setIcon(self.button_run_icon_1)

        # Button Settings
        self.button_settings = QPushButton()
        self.button_settings.setObjectName("mainButtons")
        self.button_settings.clicked.connect(self.open_settings_window)
        self.button_settings.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
        self.button_settings.setIcon(QIcon(os.path.join(self.tmp_assets_path, "settings_white.png")))
        self.button_settings.setEnabled(False)

        # Button Help
        self.button_help = QPushButton()
        self.button_help.setObjectName("mainButtons")
        self.button_help.clicked.connect(self.open_help_window)
        self.button_help.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
        self.button_help.setIcon(QIcon(os.path.join(self.tmp_assets_path, "help_white.png")))

        # --------------------------- Tabs ---------------------------
        tab_bar = QTabBar()
        tab_bar.setDrawBase(False)
        self.tabs = QTabWidget()
        self.tabs.setTabBar(tab_bar)
        self.tabs.setObjectName('myTabs')

        self.tabs.addTab(self.canvas_1, "Latency")
        self.tabs.addTab(self.canvas_2, "Accuracy")
        self.tabs.addTab(self.canvas_3, "Memory")

        text = QLabel("Under development")
        self.tabs.addTab(text, "Energy")
        self.tabs.setTabToolTip(3, "This feature is under development and will be available soon.")
        self.tabs.setTabEnabled(3, False)
        self.tabs.setToolTipDuration(0)

        # --------------------------- Logs ---------------------------

        self.logs_text_area = QTextEdit(self)
        self.logs_text_area.setObjectName('logsText')
        self.logs_text_area.setReadOnly(True)
        self.logs_text_area.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        self.logs_area = QScrollArea(self)
        self.logs_area.setObjectName('logsArea')
        self.logs_area.setWidget(self.logs_text_area)
        self.logs_area.setWidgetResizable(True)
        self.logs_area.setMaximumHeight(140)

        # --------------------------- Progress Bar --------------------

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setObjectName("myBar")
        self.progress_bar.setMinimum(0)
        self.progress_bar.setTextVisible(False)

        # --------------------------- Main ---------------------------
        self.frame_main = QFrame()
        self.frame_main.setObjectName('mainFrame')
        self.frame_main.setFrameShape(QFrame.Shape.Panel)
        self.frame_main.setFrameShadow(QFrame.Shadow.Raised)

        self.frame_second = QFrame()
        self.frame_second.setObjectName('secondFrame')
        self.frame_second.setFrameShape(QFrame.Shape.Panel)
        self.frame_second.setFrameShadow(QFrame.Shadow.Raised)

        # Layout Left
        self.layout_butons = QVBoxLayout()
        self.layout_butons.addWidget(self.button_run)
        self.layout_butons.addWidget(self.button_settings)
        self.layout_butons.addWidget(self.button_help)
        self.layout_butons.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.layout_butons.setContentsMargins(20, 0, 20, 0)

        # Create a layout for the main frame
        self.layout_tabs = QVBoxLayout()
        self.frame_main.setLayout(self.layout_tabs)
        self.layout_tabs.addWidget(self.tabs)

        # Create a layout for the second frame
        self.layout_logs = QVBoxLayout()
        self.frame_second.setLayout(self.layout_logs)
        self.layout_logs.addWidget(self.logs_area)

        # Layout Right
        self.layout_main = QVBoxLayout()
        self.layout_main.addWidget(self.logo)
        self.layout_main.addWidget(self.frame_main, stretch=3)
        self.layout_main.addSpacing(20)
        self.layout_main.addWidget(self.frame_second, stretch=1)
        self.layout_main.addSpacing(15)
        self.layout_main.addWidget(self.progress_bar)
        self.layout_main.setContentsMargins(0, 0, 20, 15)

        # Layout main
        self.main_layout = QHBoxLayout()
        self.main_layout.addLayout(self.layout_butons, stretch=1)
        self.main_layout.addLayout(self.layout_main, stretch=1)

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)
        self.setMenuWidget(self.menubar)
        # self.setStatusBar(self.status_bar)

        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------

        console_logger.consoleLog.connect(self._update_logs)

        self._clear_figures()

    def _clear_figures(self):

        # Graphs
        self.inference_cnt_hist = 1
        self.inference_cnt_plot = 1
        self.inferences_max = 50
        self.latency_min = float('inf')
        self.latency_max = 0
        self.latency_avg = 0
        self.latency_avg_sum = 0
        self.histograms_last_four = []
        self.histograms_z_max = 0
        self.x_data = []
        self.y_data = []

        # ------------------------- Figure 1 -------------------------
        line_width = 0.1
        line_color = 'black'

        self.ax_1a.clear()
        self.ax_1a.spines['bottom'].set_color(line_color)
        self.ax_1a.spines['top'].set_color(line_color)
        self.ax_1a.spines['left'].set_color(line_color)
        self.ax_1a.spines['right'].set_color(line_color)
        self.ax_1a.spines['bottom'].set_linewidth(line_width)
        self.ax_1a.spines['top'].set_linewidth(line_width)
        self.ax_1a.spines['left'].set_linewidth(line_width)
        self.ax_1a.spines['right'].set_linewidth(line_width)
        self.ax_1a.set_xlabel("Inferences", fontsize=8)
        self.ax_1a.set_ylabel("Latency [cycles]", fontsize=8)
        self.ax_1a.set_xlim(0, 50)
        self.ax_1a.tick_params(axis='both', labelsize=7)

        self.ax_1b.clear()
        self.ax_1b.spines['bottom'].set_color(line_color)
        self.ax_1b.spines['top'].set_color(line_color)
        self.ax_1b.spines['left'].set_color(line_color)
        self.ax_1b.spines['right'].set_color(line_color)
        self.ax_1b.spines['bottom'].set_linewidth(line_width)
        self.ax_1b.spines['top'].set_linewidth(line_width)
        self.ax_1b.spines['left'].set_linewidth(line_width)
        self.ax_1b.spines['right'].set_linewidth(line_width)
        stats_text = f"Inferences: 0\nMinimum: 0.0\nMaximum: 0.0\nAverage: 0.0"
        self.ax_1b.text(0.05, 0.95, stats_text, transform=self.ax_1b.transAxes, fontsize=9,
                        verticalalignment='top', horizontalalignment='left', wrap=True, linespacing=1.5)
        self.ax_1b.set_xlabel("Statistics", fontsize=8)
        self.ax_1b.set_xticks([])
        self.ax_1b.set_yticks([])
        self.ax_1b.set_frame_on(True)

        # ------------------------- Figure 2 -------------------------
        self.ax_2.clear()
        # self.ax_2.xaxis.label.set_color('red')   # X-axis label color
        # self.ax_2.yaxis.label.set_color('green') # Y-axis label color
        # self.ax_2.zaxis.label.set_color('blue')  # Z-axis label color
        self.ax_2.tick_params(axis='x', colors='black', labelsize=7)
        self.ax_2.tick_params(axis='y', colors='black', labelsize=7)
        self.ax_2.tick_params(axis='z', colors='black', labelsize=7)
        self.ax_2.set_xticks([-4, -3, -2, -1, 0, 1, 2, 3, 4])
        self.ax_2.set_yticks([0, 0, 0, 0])
        self.ax_2.set_yticks([-3, -2, -1, 0])
        self.ax_2.set_ylim(0, -3)
        self.ax_2.xaxis._axinfo['grid'].update(color='white', linestyle='solid')
        self.ax_2.yaxis._axinfo['grid'].update(color='white', linestyle='solid')
        self.ax_2.zaxis._axinfo['grid'].update(color='white', linestyle='solid')
        self.ax_2.xaxis.set_pane_color('white')
        self.ax_2.yaxis.set_pane_color('white')
        self.ax_2.zaxis.set_pane_color('white')
        self.ax_2.xaxis.line.set_linewidth(line_width)  # X-axis thickness
        self.ax_2.yaxis.line.set_linewidth(line_width)  # Y-axis thickness
        self.ax_2.zaxis.line.set_linewidth(line_width)  # Z-axis thickness
        self.ax_2.set_xlabel("Error Category", fontsize=8)
        self.ax_2.set_ylabel("Inferences", fontsize=8)
        self.ax_2.set_zlabel("Error Count", fontsize=8)
        self.ax_2.view_init(azim=-45, elev=15, roll=0.1)

        # ------------------------- Figure 3 -------------------------
        self.ax_3a.clear()
        self.ax_3b.clear()

        # Size
        self.ax_3a.axis("off")
        num_rows = 15
        empty_data = [["   " for _ in range(5)] for _ in range(num_rows)]
        self.table_a = self.ax_3a.table(cellText=empty_data,
                                        colLabels=["Memory Section", "Used [Bytes]", "Used [%]",
                                                   "Remain [Bytes]", "Total [Bytes]"],
                                        loc="center", cellLoc="left", edges='vertical')

        title = "Device Memory Usage"
        self.ax_3a.text(0.5, 1.05, title, ha='center', va='bottom', fontsize=9,
                        weight='bold', transform=self.ax_3a.transAxes)

        self.table_a.auto_set_font_size(False)
        self.table_a.set_fontsize(8)
        self.table_a.auto_set_column_width([0, 1, 2, 3, 4])
        self.table_a.scale(1, 1.1)

        for (i, j), cell in self.table_a.get_celld().items():
            if i == 0:
                cell.set_text_props(weight='bold', )  # backgroundcolor='#0d0d0d'
            cell.set_facecolor("#000000")
            cell.set_linewidth(line_width)

        # Size component
        self.ax_3b.axis("off")
        num_rows = 15
        empty_data = [["   " for _ in range(2)] for _ in range(num_rows)]
        self.table_b = self.ax_3b.table(cellText=empty_data, colLabels=["Memory Section", "Size [Bytes]"],
                                loc="center", cellLoc="left", edges='vertical')
        title = "Inference Engine Memory Usage"
        self.ax_3b.text(0.5, 1.05, title, ha='center', va='bottom', fontsize=9, weight='bold', transform=self.ax_3b.transAxes)

        self.table_b.auto_set_font_size(False)
        self.table_b.set_fontsize(8)
        self.table_b.auto_set_column_width([0, 1])
        self.table_b.scale(1, 1.1)

        for (i, j), cell in self.table_b.get_celld().items():
            if i == 0:
                cell.set_text_props(weight='bold', )  # backgroundcolor='#0d0d0d'
            cell.set_facecolor("#000000")
            cell.set_linewidth(line_width)

        self.canvas_1.draw()
        self.canvas_2.draw()
        self.canvas_3.draw()

    def _update_logs(self, new_log):
        self.logs_text_area.append(new_log)

    def _load_configuration_file(self):
        sim_logger.info("Loading configuration file...")

        # Check if configuration.yaml exists, if not, create one
        if not os.path.exists(CONFIGURATION_FILE):
            default_config = {"recent_projects": []}
            try:
                with open(CONFIGURATION_FILE, "w") as file:
                    yaml.dump(default_config, file, default_flow_style=False)
                sim_logger.info("Default configuration file created successfully.")
            except Exception as e:
                sim_logger.error(f"Failed to create configuration file: {e}")
                utils.show_conf_warn_windows(f"Failed to create configuration file.")
                return

        try:
            # Load configuration file
            self._configuration_file = utils.parse_configuration_file(CONFIGURATION_FILE)

        except Exception as e:
            sim_logger.error(f"Configuration file loading error: {e}")
            utils.show_conf_warn_windows("Configuration file loading error.")

    def _new_project_file(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Project Folder")

        if not folder_path:
            return  # User canceled the dialog

        project_title, ok = QInputDialog.getText(self, "Project Title", "Enter project name:")

        if not ok or not project_title.strip():  # User canceled or entered empty name
            return

        try:
            project_folder = Path(folder_path) / project_title
            project_folder.mkdir(parents=True, exist_ok=True)
            project_file = project_folder / f"{project_title}.yaml"

            # Copy project file
            shutil.copy(os.path.join(self.tmp_base_path, TEMPLATE_PROJECT_FILE), project_file)

            # Load new project file
            self._load_project_file(str(project_file))

            # Open project's folder
            utils.open_folder(project_file)

        except Exception as e:
            sim_logger.error(f"New project error: {e}")
            utils.show_conf_error_windows(f"New project error!")

    def _open_project_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Project", "", "Project Files (*.yaml);;All Files (*)")
        if file_path:
            self._load_project_file(file_path)

    def _load_project_file(self, full_path_name):
        try:
            sim_logger.info(f"Loading project file: {os.path.normpath(full_path_name)}")
            # Parse program file
            prog_file = utils.parse_project_file(full_path_name)

            if not prog_file:
                sim_logger.error(f"Project file loading error.")
                utils.show_conf_error_windows(f"Project file loading error.")
                return

        except Exception as e:
            sim_logger.error(f"Project file loading error: {e}")
            utils.show_conf_error_windows(f"Project file loading error.")
            return

        self._project_file['name'] = prog_file['name']
        self._project_file['path'] = prog_file['path']

        self._project_file['output_directory'] = prog_file['output_directory']
        self._project_file['model_file'] = prog_file['model_file']
        self._project_file['manufacturer'] = prog_file['manufacturer']
        self._project_file['dev_model'] = prog_file['dev_model']
        self._project_file['toolchain_path'] = prog_file['toolchain_path']
        self._project_file['input_dataset'] = prog_file['input_dataset']
        self._project_file['output_dataset'] = prog_file['output_dataset']
        self._project_file['generate_inference_engine'] = prog_file['generate_inference_engine']
        self._project_file['enable_benchmark'] = prog_file['enable_benchmark']
        self._project_file['inference_rate'] = prog_file['inference_rate']
        self._project_file['inferences_n'] = prog_file['inferences_n']
        self._project_file['show_graphs'] = prog_file['show_graphs']

        try:
            # Copy project template to output directory
            utils.copy_folder_skip_existing(self.tmp_esp32s3_path, self._project_file['output_directory'])

            # Get the idf selected id from the esp_idf.json file
            file = os.path.join(self._project_file['toolchain_path'], ESP_IDF_JSON_FILE)
            self._project_file['idf_id'] = utils.get_value_from_json(file_path=file, key=ESP_IDF_JSON_FILE_KEY)

        except Exception as e:
            sim_logger.error(f"Toolchain self-test error: {e}")
            utils.show_conf_error_windows(f"Toolchain self-test error!")
            return

        # Actions after loading project
        self.button_run.setEnabled(True)
        self.button_settings.setEnabled(True)

        # TODO: Add to recent files
        # self._add_recent_project(full_path_name)

        sim_logger.info(f'Project file "{os.path.splitext(self._project_file['name'])[0]}" loaded successfully.')

    def _add_recent_project(self, file_path):
        if not os.path.exists(CONFIGURATION_FILE):
            sim_logger.error("Configuration file does not exist.")
            return

        try:
            with open(CONFIGURATION_FILE, "r") as file:
                config = yaml.safe_load(file) or {"recent_projects": []}

            if "recent_projects" not in config:
                config["recent_projects"] = []

            if file_path not in config["recent_projects"]:
                config["recent_projects"].append(file_path)

            with open(CONFIGURATION_FILE, "w") as file:
                yaml.dump(config, file, default_flow_style=False)

            # Add to recent projects
            self._configuration_file['recent_projects'].append(file_path)

            sim_logger.info(f"Added {file_path} to recent projects.")
        except Exception as e:
            sim_logger.error(f"Failed to update recent projects: {e}")

    def _update_project_settings(self, settings):
        self._project_file['generate_inference_engine'] = settings['generate_inference_engine']
        self._project_file['enable_benchmark'] = settings['enable_benchmark']
        self._project_file['inference_rate'] = settings['inference_rate']
        self._project_file['inferences_n'] = settings['inferences_n']
        self._project_file['show_graphs'] = settings['show_graphs']

    def open_settings_window(self):
        dialog = SettingsWindow(project_file=self._project_file, logo=self.logo_icon)
        if dialog.exec_():
            settings = dialog.get_settings()
            self._update_project_settings(settings)
            for key, val in settings.items():
                sim_logger.info(f"Settings applied successfully: {key} {val}")

    def open_help_window(self):
        # Check if any help window is already open
        if self.pdf_window:  # If list is not empty
            for window in self.pdf_window:
                if window.isVisible():  # Check if the window is still open
                    window.raise_()
                    window.activateWindow()
                    return  # Exit after bringing the existing window to focus

        # Open a new one if no existing window was found
        user_guide = PDFViewer(logo=self.logo_icon, assets_path=self.tmp_assets_path)
        user_guide.show()
        self.pdf_window.append(user_guide)

    def open_about_window(self):
        dialog = AboutWindow(font_family=self.font_family, logo=self.logo_icon, assets_path=self.tmp_assets_path)
        dialog.exec_()

    def execution_start(self):

        if not self._is_thread_in_progress:
            sim_logger.info("Execution started...")
            self.button_run.setIcon(self.button_run_icon_2)
            self.button_settings.setEnabled(False)
            self._is_thread_in_progress = True
            self.thread_engine = QThread()
            self.benchmark_perf = self.BenchmarkPerformance(self, self._project_file)
            self.benchmark_perf.moveToThread(self.thread_engine)
            self.thread_engine.started.connect(self.benchmark_perf.run)
            self.benchmark_perf.progress_updated.connect(self.progress_bar.setValue)
            self.benchmark_perf.finished.connect(self.execution_finished)
            self.benchmark_perf.finished.connect(self.thread_engine.quit)
            self.benchmark_perf.finished.connect(self.benchmark_perf.deleteLater)
            self.thread_engine.finished.connect(self.thread_engine.deleteLater)
            self.thread_engine.start()
            self.progress_bar.setMaximum(0)

            # Init vars
            self.inferences_n = self._project_file['inferences_n']
            # Clear all figures
            self._clear_figures()
        else:
            sim_logger.info("Execution stopped")
            self.benchmark_perf.stop()

    def execution_start_inference(self):
        self.progress_bar.setMaximum(100)

    def execution_finished(self):
        # sim_logger.info("Execution finished")
        self._is_thread_in_progress = False
        self.button_settings.setEnabled(True)
        self.button_run.setIcon(self.button_run_icon_1)
        self.button_run.repaint()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(100)
        QApplication.processEvents()

    def is_execution_finished(self):
        # Check if inferences are over
        if self.inference_cnt_plot > self.inferences_n:
            if self._project_file['show_graphs'] is False:
                self._show_plot_graph()
                self._show_histogram()
            return True
        else:
            return False

    @property
    def inference_counter(self):
        return int((self.inference_cnt_plot / self.inferences_n) * 100)

    def _show_histogram(self):
        self.ax_2.cla()
        empty_histogram = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        error_categories = np.array([-4, -3, -2, -1, 0, 1, 2, 3, 4])
        dx = 0.9
        dy = 0.2
        hist_length = len(self.histograms_last_four)
        if hist_length == 1:
            inference_ids_1 = np.full(9, 1)
            inference_ids_2 = np.full(9, 0)
            inference_ids_3 = np.full(9, -1)
            inference_ids_4 = np.full(9, -2)
            hist_1 = np.array(self.histograms_last_four[-1])
            hist_2 = np.array(empty_histogram)
            hist_3 = np.array(empty_histogram)
            hist_4 = np.array(empty_histogram)
            self.ax_2.set_yticks([-2, -1, 0, 1])
            self.ax_2.set_ylim(1, -2)
        elif hist_length == 2:
            inference_ids_1 = np.full(9, 2)
            inference_ids_2 = np.full(9, 1)
            inference_ids_3 = np.full(9, 0)
            inference_ids_4 = np.full(9, -1)
            hist_1 = np.array(self.histograms_last_four[-1])
            hist_2 = np.array(self.histograms_last_four[-2])
            hist_3 = np.array(empty_histogram)
            hist_4 = np.array(empty_histogram)
            self.ax_2.set_yticks([-1, 0, 1, 2])
            self.ax_2.set_ylim(2, -1)
        elif hist_length == 3:
            inference_ids_1 = np.full(9, 3)
            inference_ids_2 = np.full(9, 2)
            inference_ids_3 = np.full(9, 1)
            inference_ids_4 = np.full(9, 0)
            hist_1 = np.array(self.histograms_last_four[-1])
            hist_2 = np.array(self.histograms_last_four[-2])
            hist_3 = np.array(self.histograms_last_four[-3])
            hist_4 = np.array(empty_histogram)
            self.ax_2.set_yticks([0, 1, 2, 3])
            self.ax_2.set_ylim(3, 0)
        elif hist_length == 4:
            inference_ids_1 = np.full(9, self.inference_cnt_hist)
            inference_ids_2 = np.full(9, self.inference_cnt_hist - 1)
            inference_ids_3 = np.full(9, self.inference_cnt_hist - 2)
            inference_ids_4 = np.full(9, self.inference_cnt_hist - 3)
            hist_1 = np.array(self.histograms_last_four[-1])
            hist_2 = np.array(self.histograms_last_four[-2])
            hist_3 = np.array(self.histograms_last_four[-3])
            hist_4 = np.array(self.histograms_last_four[-4])
            self.ax_2.set_yticks([self.inference_cnt_hist - 3, self.inference_cnt_hist - 2, self.inference_cnt_hist - 1,
                                  self.inference_cnt_hist])
            self.ax_2.set_ylim(self.inference_cnt_hist, self.inference_cnt_hist - 3)
        else:
            inference_ids_1 = np.full(9, 0)
            inference_ids_2 = np.full(9, -1)
            inference_ids_3 = np.full(9, -2)
            inference_ids_4 = np.full(9, -3)
            hist_1 = np.array(empty_histogram)
            hist_2 = np.array(empty_histogram)
            hist_3 = np.array(empty_histogram)
            hist_4 = np.array(empty_histogram)
            self.ax_2.set_yticks([0, 0, 0, 0])
            self.ax_2.set_ylim(0, -3)
        self.ax_2.bar3d(error_categories, inference_ids_1, np.zeros_like(hist_1), dx, dy, hist_1, color='#5b95c2',
                        alpha=1.0)
        self.ax_2.bar3d(error_categories, inference_ids_2, np.zeros_like(hist_2), dx, dy, hist_2, color='#5b95c2',
                        alpha=0.5)
        self.ax_2.bar3d(error_categories, inference_ids_3, np.zeros_like(hist_3), dx, dy, hist_3, color='#5b95c2',
                        alpha=0.2)
        self.ax_2.bar3d(error_categories, inference_ids_4, np.zeros_like(hist_4), dx, dy, hist_4, color='#5b95c2',
                        alpha=0.1)
        self.ax_2.set_xticks([-4, -3, -2, -1, 0, 1, 2, 3, 4])
        self.ax_2.set_zlim(0, self.histograms_z_max)
        self.ax_2.set_xlabel("Error Category", fontsize=8)
        self.ax_2.set_ylabel("Inferences", fontsize=8)
        self.ax_2.set_zlabel("Error Count", fontsize=8)
        self.ax_2.view_init(azim=-45, elev=15, roll=0.1)
        self.canvas_2.draw()

    def update_histogram(self, data):

        self.histograms_last_four.append(data)
        if len(self.histograms_last_four) > 4:
            self.histograms_last_four.pop(0)
        max_z = max([max(hist) for hist in self.histograms_last_four])
        if max_z > self.histograms_z_max:
            self.histograms_z_max = max_z

        if self._project_file['show_graphs']:
            self._show_histogram()

        self.inference_cnt_hist += 1

    def _show_plot_graph(self):
        self.ax_1b.clear()
        stats_text = (f"Inferences: {self.inference_cnt_plot}\nMinimum: {self.latency_min:.2f}\n"
                      f"Maximum: {self.latency_max:.2f}\nAverage: {self.latency_avg:.2f}")
        self.ax_1b.text(0.05, 0.95, stats_text, transform=self.ax_1b.transAxes, fontsize=9,
                        verticalalignment='top', horizontalalignment='left', wrap=True, linespacing=1.5)
        self.ax_1b.set_xlabel("Statistics", fontsize=8)
        self.ax_1b.set_xticks([])
        self.ax_1b.set_yticks([])
        self.ax_1b.set_frame_on(True)

        if self.inference_cnt_plot > self.inferences_max:
            self.ax_1a.set_xlim(self.x_data[0], self.x_data[-1])
            self.ax_1a.plot(self.x_data, self.y_data, '#5b95c2', linewidth=0.8)
            self.canvas_1.draw()
        elif self.inference_cnt_plot > 1:
            self.ax_1a.plot(self.x_data, self.y_data, '#5b95c2', linewidth=0.8)
            self.canvas_1.draw()

    def update_plot_graph(self, y):

        # Update x, y data
        self.x_data.append(self.inference_cnt_plot)
        self.y_data.append(y)

        if self.inference_cnt_plot > self.inferences_max:
            self.y_data.pop(0)
            self.x_data.pop(0)

        # Minimum/Maximum Latency
        if y < self.latency_min:
            self.latency_min = y
        if y > self.latency_max:
            self.latency_max = y
        # Average Latency
        self.latency_avg_sum += y
        self.latency_avg = self.latency_avg_sum / self.inference_cnt_plot

        # Show plot graph
        if self._project_file['show_graphs']:
            self._show_plot_graph()

        # Update inference counter
        self.inference_cnt_plot += 1

    def update_memory_table(self, data, data_lib):

        table_data = []
        for key, values in data.items():
            row = [key] + values  # Add the key as the first column followed by its values
            table_data.append(row)
        table_data.append([' '])

        # Ensure all rows have the same number of columns (fill missing values with empty string if needed)
        for row in table_data:
            while len(row) < 5:
                row.append('')

        # Size
        self.ax_3a.clear()
        self.ax_3a.axis("off")

        table = self.ax_3a.table(cellText=table_data,
                                 colLabels=["Memory Section", "Used [Bytes]", "Used [%]",
                                            "Remain [Bytes]", "Total [Bytes]"],
                                 loc="center", cellLoc="left", edges='vertical')

        title = "Device Memory Usage"
        self.ax_3a.text(0.5, 1.05, title, ha='center', va='bottom', fontsize=9,
                        weight='bold', transform=self.ax_3a.transAxes)
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.auto_set_column_width([0, 1, 2, 3, 4])
        table.scale(1, 1.1)

        for (i, j), cell in table.get_celld().items():
            if i == 0:
                cell.set_text_props(weight='bold')
            cell.set_facecolor("#000000")
            cell.set_linewidth(0.1)

        # Size component
        self.ax_3b.clear()
        self.ax_3b.axis("off")
        table = self.ax_3b.table(cellText=data_lib, colLabels=["Memory Section", "Size [Bytes]"],
                                 loc="center", cellLoc="left", edges='vertical')
        title = "Inference Engine Memory Usage"
        self.ax_3b.text(0.5, 1.05, title, ha='center', va='bottom', fontsize=9, weight='bold',
                        transform=self.ax_3b.transAxes)
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.auto_set_column_width([0, 1])
        table.scale(1, 1.1)

        for (i, j), cell in table.get_celld().items():
            if i == 0:
                cell.set_text_props(weight='bold')
            cell.set_facecolor("#000000")
            cell.set_linewidth(0.1)

        self.canvas_3.draw()

    class BenchmarkPerformance(QObject):

        finished = Signal()
        progress_updated = Signal(int)

        def __init__(self, outer_instance, project_file):
            super().__init__()

            # Main variables
            self._stop_flag = False
            self.engine_main_instance = outer_instance

            # Project variables
            self.tf_lite_model = project_file['model_file']
            self.output_path = project_file['output_directory']
            self.dataset_input = project_file['input_dataset']
            self.dataset_output = project_file['output_dataset']
            self.idf_path = project_file['toolchain_path']
            self.settings_inf_rate = project_file['inference_rate']
            self.settings_inferences_n = project_file['inferences_n']
            self.toolchain_esp_idf_key = project_file['idf_id']
            self.generate_inference_engine = project_file['generate_inference_engine']
            self.enable_benchmark = project_file['enable_benchmark']

            # Serial variables
            self.serial_port = ""
            self.serial_baud_rate = 115200
            self.cycles = []
            self.histograms = []

            # Toolchain variables
            self.sizes_component = []
            self.memory_usage_summary = {}
            self.start_processing = False
            self.size_headers_idx = 0

            self.size_component_headers = [
                "Total Size",
                "IRAM", "   .text (1)", "   .vectors",
                "DIRAM", "   .bss", "   .data", "   .text (2)",
                "Flash Code", "   .text (3)",
                "Flash Data", "   .rodata", "   .appdesc",
                "RTC FAST", "   .rtc_reserved"
            ]

            self.size_headers_v = [
                "DIRAM", "   .bss", "  .data", "   .text (1)",
                "Flash Code", "   .text (2)",
                "Flash Data", "   .rodata", "   .appdesc",
                "IRAM", "   .text (3)", "   .vectors",
                "RTC FAST", "   .rtc_reserved"
            ]

        def run(self):
            try:
                if self.generate_inference_engine is True:
                    # Generate engine
                    self.generate_engine_model()
                # Check if benchmark is enabled
                if self.enable_benchmark is True:
                    # Generate validator
                    self.generate_validator()
                    # Device Build and Flash
                    if self.device_build_and_flash():
                        # Device monitor
                        self.device_monitor()
            except Exception as e:
                sim_logger.error(e)

            self.finished.emit()

        def stop(self):
            self._stop_flag = True

        def generate_engine_model(self):
            # Start
            sim_logger.info("Generating engine...")

            # Step 1
            sim_logger.info("De-serializing the TFlite model...")
            model_deserialized = model_converter(self.tf_lite_model)

            # Step 2
            sim_logger.info("Processing buffers...")
            buffers, definitions_dict, typedefs_dict = generate_buffers(model_deserialized)

            # Step 3
            sim_logger.info("Generating files...")
            generate_public_files(buffers, definitions_dict, typedefs_dict, self.output_path)

            # Completed
            sim_logger.info("Engine generated successfully!")

            return True

        def generate_validator(self):
            # Start
            sim_logger.info("Generating validator...")

            # Step 1
            sim_logger.info("Processing buffers...")
            data_input = pd.read_csv(self.dataset_input, header=None)
            dataset_output = pd.read_csv(self.dataset_output, header=None)

            # TODO: For testing
            TEST_PART = False
            TEST_CNT = 1
            cnt = TEST_CNT

            # Step 2
            sim_logger.info("Converting to code...")
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
            dataset_input_code = utils.convert_c_arrays_to_code(c_arrays_inputs, 'input', 'int8_t')
            dataset_output_code = utils.convert_c_arrays_to_code(c_arrays_outputs, 'output', 'int8_t')

            # Replace variables
            validation_c_file = (VALIDATION_C
                                 .replace("{dataset_input_code}", str(dataset_input_code))
                                 .replace("{dataset_output_code}", str(dataset_output_code)))
            validation_h_file = VALIDATION_H.replace("{dataset_rows}", str(rows)).replace("{dataset_columns}",
                                                                                          str(columns))
            # App main
            main_c_file = (VALIDATION_MAIN_C
                           .replace("{inference_rate}", str(self.settings_inf_rate))
                           .replace("{inferences_n}", str(self.settings_inferences_n)))

            # Step 3
            sim_logger.info("Generating files...")
            utils.generate_file(os.path.abspath(os.path.join(self.output_path, PATH_MAIN, FILENAME_VALIDATION_C)),
                                validation_c_file)
            utils.generate_file(os.path.abspath(os.path.join(self.output_path, PATH_MAIN, FILENAME_VALIDATION_H)),
                                validation_h_file)
            utils.generate_file(os.path.abspath(os.path.join(self.output_path, PATH_MAIN, FILENAME_MAIN_C)),
                                main_c_file)
            # Completed
            sim_logger.info("Validator generated successfully!")

            return True

        def device_build_and_flash(self):
            # Start
            sim_logger.info("Building and flashing project...")

            os.chdir(self.output_path)
            idf_cmd_init = os.path.join(self.idf_path, 'idf_cmd_init.bat')
            idf_build_flash = 'idf.py size size-components flash'
            command = f'"{idf_cmd_init}" {self.toolchain_esp_idf_key} & {idf_build_flash}'
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
                                       text=True,
                                       encoding='utf-8', errors='replace')

            # Wait for step 1
            flashing_in_progress = False
            for line in process.stdout:
                line = line.strip()
                if line:
                    sim_logger.info(f"[Toolchain]: {line}")
                    # Process toolchain output
                    self._process_toolchain_line(line)
                    # Find serial port
                    self._find_com_port(line)

                # IMPORTANT NOTE: DO NOT STOP DURING FLASHING
                if 'Connecting...' in line:
                    flashing_in_progress = True

                if self._stop_flag and not flashing_in_progress:
                    process.terminate()
                    QThread.sleep(3)
                    if process.poll() is None:
                        process.kill()
                    sim_logger.error("Build terminated!")
                    return False

            process.wait()

            # Completed
            last_error_line = None
            # Log warnings for all but the last line
            for error in process.stderr:
                error_line = error.strip()
                # Log the previous line as a warning
                if last_error_line:
                    sim_logger.warn(last_error_line)
                last_error_line = error_line

            # Check return code
            if process.returncode != 0:
                if last_error_line:
                    sim_logger.error(
                        f"Command failed with return code {process.returncode}. Last error: {last_error_line}")
                sim_logger.error("Build failed!")
                return False

            else:
                # If the command succeeds, log the last error line (if any) as a warning
                if last_error_line:
                    sim_logger.warn(last_error_line)
                sim_logger.info("Build completed successfully")

            return True

        def device_monitor(self):
            sim_logger.info("Monitoring started...")
            try:
                with serial.Serial(self.serial_port, self.serial_baud_rate, timeout=5) as ser:
                    sim_logger.info(f"Listening on {self.serial_port} at {self.serial_baud_rate} baud rate...")

                    # Inference Start
                    self.engine_main_instance.execution_start_inference()

                    while True:

                        # Read and process line
                        line = ser.readline().decode('utf-8', errors='ignore').strip()
                        if line:
                            self._process_serial_line(line)

                        # if ser.in_waiting > 0:
                        #     data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                        #     for line in data.splitlines():
                        #         self._process_serial_line(line)

                        # Update progress
                        self.progress_updated.emit(self.engine_main_instance.inference_counter)

                        # Stop condition
                        if self._stop_flag or self.engine_main_instance.is_execution_finished():
                            break
                    ser.close()
                    sim_logger.info("Monitoring completed successfully")
            except serial.SerialException as e:
                sim_logger.error(f"Monitoring failed with error: {e}")
                return False

            return True

        def _process_toolchain_line(self, line):

            if not self.start_processing and "Memory Type Usage Summary" in line:
                self.start_processing = True
                self.size_headers_idx = 0

            if self.start_processing:
                numbers = re.findall(r"\d+\.\d+|\d+", line)
                if numbers:
                    self.memory_usage_summary[self.size_headers_v[self.size_headers_idx]] = numbers
                    self.size_headers_idx += 1
                    if self.size_headers_idx >= len(self.size_headers_v):
                        self.start_processing = False
                        # print(self.memory_usage_summary)

            if " libnn.a" in line:
                numbers = list(map(int, re.findall(r'\d+', line)))
                self.sizes_component = list(zip(self.size_component_headers, numbers))
                first_element = self.sizes_component.pop(0)
                self.sizes_component.append(first_element)

                # Update memory tables
                self.engine_main_instance.update_memory_table(self.memory_usage_summary, self.sizes_component)

        def _process_serial_line(self, line):
            parts = line.strip().split(',')
            if "cycles" in parts[0]:
                self.engine_main_instance.update_plot_graph(int(parts[1]))
            elif "histogram" in parts[0]:
                histogram = list(map(int, parts[1:]))
                self.engine_main_instance.update_histogram(histogram)

        def _find_com_port(self, line):
            match = re.search(r"Serial port COM(\d+)", line)
            if match:
                self.serial_port = "COM" + match.group(1)



