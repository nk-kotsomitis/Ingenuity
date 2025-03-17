# Copyright (C) 2025 Ingenuity
# Licensed under the GNU General Public License v3.0

import os.path

from PySide6.QtCore import QObject, QThread, Signal, QTimer, Qt
from PySide6.QtWidgets import (QDialog, QLineEdit, QSpinBox, QMessageBox, QVBoxLayout, QHBoxLayout, QWidget,
                               QPushButton, QFileDialog, QTabWidget, QLabel, QTabBar, QTextEdit, QScrollArea,
                               QLayout, QMenuBar, QProgressBar, QStatusBar, QMainWindow, QMenu, QCheckBox,
                               QWidgetAction, QDialogButtonBox)
from PySide6.QtGui import QImage, QIcon, QAction, QFont, QFontDatabase, QIntValidator, QPixmap
import sys
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtPdf import QPdfDocument
from configuration import VERSION_INGENUITY, BUILD_INGENUITY


class ProjectWindow(QDialog):
    def __init__(self, parent=None, project_file=None):
        super().__init__(parent)
        self.setWindowTitle("Project Details")
        self.setFixedSize(300, 200)


class AboutWindow(QDialog):
    def __init__(self, parent=None, font_family=None, logo=None, assets_path=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        if logo:
            self.setWindowIcon(logo)
        self.setFixedSize(280, 240)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        self.buttonBox.rejected.connect(self.close)

        if font_family is None:
            custom_font = QFont("Verdana", 16)
        else:
            custom_font = QFont(font_family, 16)

        self.logo = QLabel("ingenuity.")
        self.logo.setFont(custom_font)
        self.logo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.logo.setFixedHeight(50)

        self.line_1 = QLabel("Version " + VERSION_INGENUITY)
        self.line_2 = QLabel("Built on " + BUILD_INGENUITY)

        self.github_icon = QLabel()
        self.github_icon.setPixmap(QPixmap(os.path.join(assets_path, "github.png")).scaled(24, 24,
        Qt.AspectRatioMode.KeepAspectRatio, Qt.SmoothTransformation))

        # TODO: Add projects github when published, not mine
        self.github_label = QLabel('<a href="https://github.com/nk-kotsomitis/ingenuity">GitHub Repository</a>')
        self.github_label.setOpenExternalLinks(True)
        self.github_layout = QHBoxLayout()
        self.github_layout.addWidget(self.github_icon)
        self.github_layout.addWidget(self.github_label)
        self.github_layout.addStretch(1)

        self.linkedin_icon = QLabel()
        self.linkedin_icon.setPixmap(QPixmap(os.path.join(assets_path, "linkedin.png")).scaled(24, 24,
        Qt.AspectRatioMode.KeepAspectRatio, Qt.SmoothTransformation))
        self.linkedin_label = QLabel('<a href="https://www.linkedin.com/in/nick-kotsomitis/">Connect on LinkedIn</a>')
        self.linkedin_label.setOpenExternalLinks(True)
        self.linkedin_layout = QHBoxLayout()
        self.linkedin_layout.addWidget(self.linkedin_icon)
        self.linkedin_layout.addWidget(self.linkedin_label)
        self.linkedin_layout.addStretch(1)

        self.box_layout = QVBoxLayout()
        self.box_layout.addWidget(self.logo)
        self.box_layout.addSpacing(20)
        self.box_layout.addWidget(self.line_1)
        self.box_layout.addWidget(self.line_2)
        self.box_layout.addLayout(self.github_layout)
        self.box_layout.addLayout(self.linkedin_layout)
        self.box_layout.addStretch(1)
        self.box_layout.addSpacing(30)
        self.box_layout.addWidget(self.buttonBox, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(self.box_layout)


class SettingsWindow(QDialog):
    def __init__(self, parent=None, project_file=None, logo=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        if logo:
            self.setWindowIcon(logo)
        # self.setFixedSize(600, 300)
        self.setMinimumHeight(200)
        inputs_width = 100

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # Value 00
        self.param_00 = QHBoxLayout()
        self.label_00 = QLabel("Generate Inference Engine")
        self.input_generate_inference_engine = QCheckBox(self)
        self.input_generate_inference_engine.setChecked(bool(project_file['generate_inference_engine']))
        self.param_00.addWidget(self.label_00)
        self.param_00.addWidget(self.input_generate_inference_engine, alignment=Qt.AlignmentFlag.AlignRight)

        # Value 01
        self.param_01 = QHBoxLayout()
        self.label_01 = QLabel("Enable Benchmark")
        self.input_enable_benchmark = QCheckBox(self)
        self.input_enable_benchmark.setChecked(bool(project_file['enable_benchmark']))
        self.param_01.addWidget(self.label_01)
        self.param_01.addWidget(self.input_enable_benchmark, alignment=Qt.AlignmentFlag.AlignRight)

        # Value 1
        self.param_1 = QHBoxLayout()
        self.label_1 = QLabel("Enter inference rate in milliseconds [0, 1000]")
        self.input_inf_rate = QSpinBox(self)
        self.input_inf_rate.setRange(0, 1000)
        self.input_inf_rate.setValue(int(project_file['inference_rate']))
        self.input_inf_rate.setFixedWidth(inputs_width)
        self.param_1.addWidget(self.label_1)
        self.param_1.addWidget(self.input_inf_rate)

        # Value 2
        self.param_2 = QHBoxLayout()
        self.label_1 = QLabel("Enter number of inferences [1, 10<sup>9</sup>]")
        self.input_inf_n = QSpinBox(self)
        self.input_inf_n.setRange(1, 1000000000)
        self.input_inf_n.setValue(int(project_file['inferences_n']))
        self.input_inf_n.setFixedWidth(inputs_width)
        self.param_2.addWidget(self.label_1)
        self.param_2.addWidget(self.input_inf_n)

        # Value 3
        self.param_3 = QHBoxLayout()
        self.label_2 = QLabel("Show graphs during runtime")
        self.input_show_graphs = QCheckBox(self)
        self.input_show_graphs.setChecked(bool(project_file['show_graphs']))
        self.param_3.addWidget(self.label_2)
        self.param_3.addWidget(self.input_show_graphs, alignment=Qt.AlignmentFlag.AlignRight)

        self.box_layout = QVBoxLayout()
        self.box_layout.addLayout(self.param_00)
        self.box_layout.addLayout(self.param_01)
        self.box_layout.addLayout(self.param_1)
        self.box_layout.addLayout(self.param_2)
        self.box_layout.addLayout(self.param_3)
        self.box_layout.addStretch(1)
        self.box_layout.addWidget(self.buttonBox, alignment=Qt.AlignmentFlag.AlignBottom)
        self.setLayout(self.box_layout)

    def get_settings(self):
        settings = {
                    'generate_inference_engine': self.input_generate_inference_engine.isChecked(),
                    'enable_benchmark': self.input_enable_benchmark.isChecked(),
                    'inference_rate': self.input_inf_rate.value(),
                    'inferences_n': self.input_inf_n.value(),
                    'show_graphs': self.input_show_graphs.isChecked()
        }
        return settings


class PDFViewer(QMainWindow):
    def __init__(self, logo=None, assets_path=None):
        super().__init__()

        self.setWindowTitle("User's Manual")
        if logo:
            self.setWindowIcon(logo)
        self.setGeometry(300, 100, 870, 600)
        # self.showMaximized()

        # Create PDF Viewer
        self.pdf_view = QPdfView()
        self.pdf_doc = QPdfDocument(self)

        # Load the PDF document
        self.pdf_doc.load(os.path.join(assets_path, "User's Manual.pdf"))
        self.pdf_view.setDocument(self.pdf_doc)

        # Enable two-page mode
        self.pdf_view.setPageMode(QPdfView.PageMode.MultiPage)

        # Set up layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.pdf_view)
        self.setCentralWidget(central_widget)
