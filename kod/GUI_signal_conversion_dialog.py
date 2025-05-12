import numpy as np

from logic_signal_file_handler import SignalFileHandler
from strings import *
from PyQt5.QtWidgets import QButtonGroup, QDialog, QFileDialog, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QRadioButton, QTextEdit, QVBoxLayout


class SignalConversionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(SIGNAL_OPERATION_DIALOG_TITLE)
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


        operation_layout = QHBoxLayout()
        self.operation_group = QButtonGroup()
        operations = [SAMPLING, QUANTIZATION, EXTRAPOLATION, INTERPOLATION, RECONSTRUCTION]
        for op in operations:
            radio_btn = QRadioButton(op)
            self.operation_group.addButton(radio_btn)
            operation_layout.addWidget(radio_btn)
        layout.addLayout(operation_layout)



        perform_btn = QPushButton(PERFORM_CONVERSION)
        perform_btn.clicked.connect(self.perform_conversion)
        layout.addWidget(perform_btn)


        self.setLayout(layout)

        self.signal1_data = None


    def perform_downsampling(self):
        # Example downsampling operation
        original_freq = 1000  # Example original frequency
        target_freq = 500  # Example target frequency
        downsampled_signal = SignalFileHandler.sample(self.signal1_data, original_freq, target_freq)

        save_filename, _ = QFileDialog.getSaveFileName(self, SAVE_RESULT, "", "Binary Files (*.bin)")
        if save_filename:
            SignalFileHandler.save_signal(save_filename, downsampled_signal)

            self.parent().generate_signal_from_file(save_filename)
            self.close()

    def perform_quantization(self):
        # Example quantization operation
        num_levels = 8  # Example quantization levels
        quantized_signal = self.quantize_signal(self.signal1_data, num_levels)

        save_filename, _ = QFileDialog.getSaveFileName(self, SAVE_RESULT, "", "Binary Files (*.bin)")
        if save_filename:
            SignalFileHandler.save_signal(save_filename, quantized_signal)

            self.parent().generate_signal_from_file(save_filename)
            self.close()


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

            except Exception as e:
                QMessageBox.critical(self, "Error", ERROR_LOADING.format(str(e)))


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
            result_signal = SignalFileHandler.perform_signal_conversion(
                self.signal1_data,
                operation
            )

            save_filename, _ = QFileDialog.getSaveFileName(self, SAVE_RESULT, "", "Binary Files (*.bin)")
            if save_filename:
                SignalFileHandler.save_signal(save_filename, result_signal)

                self.parent().generate_signal_from_file(save_filename)
                self.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", ERROR_OPERATION_FAILED.format(str(e)))



    def quantize_signal(self, signal, num_levels):
        # Normalize the signal to range [0, 1] and apply quantization
        min_val = np.min(signal)
        max_val = np.max(signal)
        normalized_signal = (signal - min_val) / (max_val - min_val)

        # Quantize by scaling and rounding to nearest level
        quantized_signal = np.round(normalized_signal * (num_levels - 1)) / (num_levels - 1)

        # Rescale back to original range
        quantized_signal = quantized_signal * (max_val - min_val) + min_val
        return quantized_signal


class SamplingDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sampling Frequency Input")

        self.layout = QVBoxLayout()

        self.label = QLabel("Enter target sampling frequency (Hz):")
        self.freq_input = QLineEdit()
        self.freq_input.setPlaceholderText("e.g., 500")

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.freq_input)
        self.layout.addWidget(self.ok_button)

        self.setLayout(self.layout)

    def get_frequency(self):
        try:
            return int(self.freq_input.text())
        except ValueError:
            return None
