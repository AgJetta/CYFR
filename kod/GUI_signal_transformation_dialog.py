import numpy as np
from logic_signal_file_handler import SignalFileHandler
from strings import *
from PyQt5.QtWidgets import QButtonGroup, QDialog, QFileDialog, QHBoxLayout, QLabel, QLineEdit, QMessageBox, \
    QPushButton, QRadioButton, QTextEdit, QVBoxLayout, QGroupBox, QFormLayout, QComboBox
from logic_comparisons import mean_squared_error, signal_to_noise_ratio, peak_signal_to_noise_ratio, max_difference

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
        method_select_group = QGroupBox("Wybierz metodę analizy sygnału")
        method_select_layout = QHBoxLayout()

        self.method_group = QButtonGroup()
        self.fourier_radio = QRadioButton("Transformacja Fouriera")
        self.wavelet_radio = QRadioButton("Transformacja Falkowa")

        self.method_group.addButton(self.fourier_radio)
        self.method_group.addButton(self.wavelet_radio)

        method_select_layout.addWidget(self.fourier_radio)
        method_select_layout.addWidget(self.wavelet_radio)
        method_select_group.setLayout(method_select_layout)

        layout.addWidget(method_select_group)

        # --- Grupa: Transformacje Fouriera ---
        self.fourier_group = QGroupBox("Transformacje Fouriera")
        fourier_layout = QVBoxLayout()

        self.fourier_button_group = QButtonGroup()
        fourier_transforms = ["FFT"]  # Możesz dodać inne, np. "DCT"
        for ft in fourier_transforms:
            btn = QRadioButton(ft)
            self.fourier_button_group.addButton(btn)
            fourier_layout.addWidget(btn)

        self.fourier_group.setLayout(fourier_layout)
        layout.addWidget(self.fourier_group)

        # --- Grupa: Transformacje Falkowe ---
        self.wavelet_group = QGroupBox("Transformacja Falkowa")
        wavelet_layout = QVBoxLayout()
        wavelet_layout.addWidget(QLabel("Transformacja falkowa (jeden poziom)"))

        self.wavelet_combo = QComboBox()
        self.wavelet_combo.addItems(["DB4", "DB6", "DB8"])
        wavelet_layout.addWidget(self.wavelet_combo)

        self.wavelet_group.setLayout(wavelet_layout)
        layout.addWidget(self.wavelet_group)

        # --- Przycisk wykonania ---
        perform_btn = QPushButton(PERFORM_CONVERSION)
        perform_btn.clicked.connect(self.perform_conversion)
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


    def load_signal(self, path_input):
        filename, _ = QFileDialog.getOpenFileName(self, LOAD_SIGNAL, "", "Binary Files (*.bin)")
        if filename:
            path_input.setText(filename)

            try:
                metadata, signal_data = SignalFileHandler.load_signal(filename)
                params_text = f"{METADATA_LABEL}\n"
                for key, value in metadata.items():
                    params_text += f"{key}: {value}\n"

                if path_input == self.signal1_path:
                    self.signal1_params.setText(params_text)
                    self.signal1_data = signal_data
                    # For debugging purposes, you can print out the signal data
                    # print(f"PARAMETRY: ", params_text)
                    # print(f"SIGNAL: ", signal_data)
            except Exception as e:
                QMessageBox.critical(self, "Error", ERROR_LOADING.format(str(e)))

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

    def perform_conversion(self):
        if self.signal1_data is None:
            QMessageBox.critical(self, "Error", ERROR_LOAD_BOTH)
            return

        selected_op = self.operation_group.checkedButton()
        if not selected_op:
            QMessageBox.critical(self, "Error", ERROR_SELECT_OPERATION)
            return

        operation = selected_op.text()

        try:
            metadata_text = self.signal1_params.toPlainText()
            metadata_dict = self.parse_metadata_text(metadata_text)

            # Read frequency and quantization level from inputs
            frequency = self.sampling_rate_input.text().strip()
            quantization_lvl = self.quantization_level_input.text().strip()

            # Convert to appropriate types or set to None if empty
            frequency = int(frequency) if frequency else None
            quantization_lvl = int(quantization_lvl) if quantization_lvl else None

            # Pass the inputs to the conversion function
            result_signal, result_metadata = SignalFileHandler.perform_signal_conversion(
                self.signal1_data, metadata_dict, operation,
                frequency=frequency, quantization_lvl=quantization_lvl
            )

            save_filename, _ = QFileDialog.getSaveFileName(self, SAVE_RESULT, "", "Binary Files (*.bin)")
            if save_filename:
                SignalFileHandler.save_signal(save_filename, result_signal, metadata=result_metadata)
                self.parent().generate_signal_from_file(save_filename)
                self.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", ERROR_OPERATION_FAILED.format(str(e)))
