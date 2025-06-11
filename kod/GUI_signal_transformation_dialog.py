import json
import struct

import numpy as np
from logic_signal_file_handler import SignalFileHandler
from strings import *
from PyQt5.QtWidgets import QButtonGroup, QDialog, QFileDialog, QHBoxLayout, QLabel, QLineEdit, QMessageBox, \
    QPushButton, QRadioButton, QTextEdit, QVBoxLayout, QGroupBox, QFormLayout, QComboBox

class SignalTransformationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(TRANSFORMATION)
        self.setGeometry(200, 200, 500, 400)

        layout = QVBoxLayout()

        signal1_layout = QHBoxLayout()
        self.signal1_path = QLineEdit()
        self.signal1_path.setReadOnly(True)
        signal1_btn = QPushButton(LOAD_SIGNAL_1)
        signal1_btn.clicked.connect(lambda: self.load_signal(self.signal1_path))
        signal1_layout.addWidget(QLabel(SIGNAL_1_LABEL))
        signal1_layout.addWidget(self.signal1_path)
        signal1_layout.addWidget(signal1_btn)
        layout.addLayout(signal1_layout)

        self.signal1_params = QTextEdit()
        self.signal1_params.setReadOnly(True)
        layout.addWidget(self.signal1_params)

        params_layout = QFormLayout()
        self.sampling_rate_input = QLineEdit()
        self.quantization_level_input = QLineEdit()

        # --- Wybór typu transformacji ---
        method_select_group = QGroupBox(CHOOSE_TRANSFORMATION_METHOD)
        method_select_layout = QHBoxLayout()

        self.method_group = QButtonGroup()
        self.fourier_radio = QRadioButton(FOURIER_TRANSFORMATION)
        self.wavelet_radio = QRadioButton(WAVE_TRANSFORMATION)

        self.method_group.addButton(self.fourier_radio)
        self.method_group.addButton(self.wavelet_radio)

        method_select_layout.addWidget(self.fourier_radio)
        method_select_layout.addWidget(self.wavelet_radio)
        method_select_group.setLayout(method_select_layout)

        layout.addWidget(method_select_group)

        # --- Grupa: Transformacje Fouriera ---
        self.fourier_group = QGroupBox(FOURIER_TRANSFORMATION)
        fourier_layout = QVBoxLayout()

        self.fourier_button_group = QButtonGroup()
        fourier_transforms = ["DIF FFT"]  # Możesz dodać inne, np. "DCT"
        for ft in fourier_transforms:
            btn = QRadioButton(ft)
            self.fourier_button_group.addButton(btn)
            fourier_layout.addWidget(btn)

        self.fourier_group.setLayout(fourier_layout)
        layout.addWidget(self.fourier_group)

        # --- Grupa: Transformacje Falkowe ---
        self.wavelet_group = QGroupBox(WAVE_TRANSFORMATION)
        wavelet_layout = QVBoxLayout()
        wavelet_layout.addWidget(QLabel(WAVE_TRANSFORMATION_PARAMS))

        self.wavelet_combo = QComboBox()
        self.wavelet_combo.addItems(["DB4", "DB6", "DB8"])
        wavelet_layout.addWidget(self.wavelet_combo)

        self.wavelet_group.setLayout(wavelet_layout)
        layout.addWidget(self.wavelet_group)

        # --- Przycisk wykonania ---
        perform_btn = QPushButton(PERFORM_TRANSFORMATION)
        perform_btn.clicked.connect(self.perform_transformation)
        layout.addWidget(perform_btn)

        # --- Ukrywanie/pokazywanie odpowiednich grup
        self.fourier_radio.toggled.connect(self.toggle_transform_groups)
        self.wavelet_radio.toggled.connect(self.toggle_transform_groups)

        # Ustaw domyślnie np. Transformacja Fouriera
        self.fourier_radio.setChecked(True)
        self.toggle_transform_groups()  # Funkcja definiowana niżej

        self.setLayout(layout)

        self.signal1_data = None

    def toggle_transform_groups(self):
        if self.fourier_radio.isChecked():
            self.fourier_group.setVisible(True)
            self.wavelet_group.setVisible(False)
        elif self.wavelet_radio.isChecked():
            self.fourier_group.setVisible(False)
            self.wavelet_group.setVisible(True)


    def parse_metadata_text(self, text):
        lines = text.strip().split('\n')
        metadata = {}
        for line in lines[1:]:  # Skip the METADATA_LABEL line
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                # Try converting to appropriate data type
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                else:
                    try:
                        value = float(value) if '.' in value else int(value)
                    except ValueError:
                        pass
                metadata[key] = value
        return metadata

    @staticmethod
    def load_signal(filename):
        with open(filename, 'rb') as f:
            # Read metadata length (4 bytes = unsigned int)
            metadata_len = struct.unpack('I', f.read(4))[0]

            # Read metadata as JSON
            metadata_json = f.read(metadata_len).decode('utf-8')
            metadata = json.loads(metadata_json)

            num_samples = metadata.get("num_samples", 0)
            is_complex = metadata.get("is_complex", False)

            if is_complex:
                # Each complex sample = 16 bytes (2 doubles: real + imag)
                total_bytes = num_samples * 16
                raw = f.read(total_bytes)
                data = struct.unpack(f'{num_samples * 2}d', raw)  # unpack to flat list of doubles
                signal_data = np.array(data[::2]) + 1j * np.array(data[1::2])
            else:
                # Each real sample = 8 bytes (1 double)
                total_bytes = num_samples * 8
                raw = f.read(total_bytes)
                signal_data = np.array(struct.unpack(f'{num_samples}d', raw))

            return metadata, signal_data


    def perform_transformation(self):
        if self.signal1_data is None:
            QMessageBox.critical(self, "Error", ERROR_LOADING)
            return

        try:
            metadata_text = self.signal1_params.toPlainText()
            metadata_dict = self.parse_metadata_text(metadata_text)

            # Determine selected operation
            if self.fourier_radio.isChecked():
                selected_op = self.fourier_button_group.checkedButton()
                if not selected_op:
                    QMessageBox.critical(self, "Error", ERROR_SELECT_OPERATION)
                    return
                operation = selected_op.text()  # e.g., "DIF FFT"

            elif self.wavelet_radio.isChecked():
                operation = self.wavelet_combo.currentText()  # e.g., "DB4"
            else:
                QMessageBox.critical(self, "Error", ERROR_SELECT_OPERATION)
                return

            # print("OPERATION")
            # print(operation)

            # Perform transformation
            result_signal, result_metadata = SignalFileHandler.perform_signal_transformation(
                self.signal1_data, metadata_dict, operation
            )

            save_filename, _ = QFileDialog.getSaveFileName(self, SAVE_RESULT, "", "Binary Files (*.bin)")
            if save_filename:
                SignalFileHandler.save_signal(save_filename, result_signal, metadata=result_metadata)
                self.parent().generate_signal_from_file(save_filename)
                self.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", ERROR_OPERATION_FAILED.format(str(e)))
