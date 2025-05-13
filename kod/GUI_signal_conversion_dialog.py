import numpy as np

from logic_signal_file_handler import SignalFileHandler
from strings import *
from PyQt5.QtWidgets import QButtonGroup, QDialog, QFileDialog, QHBoxLayout, QLabel, QLineEdit, QMessageBox, \
    QPushButton, QRadioButton, QTextEdit, QVBoxLayout, QFormLayout, QComboBox, QGroupBox


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

        params_layout = QFormLayout()
        self.sampling_rate_input = QLineEdit()
        self.quantization_level_input = QLineEdit()
        self.sample_rate_period = QLineEdit()

        params_layout.addRow(SAMPLE_FREQ, self.sampling_rate_input)
        params_layout.addRow(PERIOD, self.sample_rate_period)
        params_layout.addRow(QUANTIZATION_LVL, self.quantization_level_input)


        params_group = QGroupBox(SIGNAL_PARAMETERS)
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)

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
                    # print(f"PARAMETRY: ", params_text)
                    self.signal1_data = signal_data
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

            print(self.signal1_data, metadata_text, operation)
            result_signal = SignalFileHandler.perform_signal_conversion(
                self.signal1_data, metadata_dict, operation
            )

            save_filename, _ = QFileDialog.getSaveFileName(self, SAVE_RESULT, "", "Binary Files (*.bin)")
            if save_filename:
                SignalFileHandler.save_signal(save_filename, result_signal)

                self.parent().generate_signal_from_file(save_filename)
                self.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", ERROR_OPERATION_FAILED.format(str(e)))


