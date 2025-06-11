import json
import struct

import numpy as np
from logic_signal_file_handler import SignalFileHandler
from strings import *
from PyQt5.QtWidgets import QButtonGroup, QDialog, QFileDialog, QHBoxLayout, QLabel, QLineEdit, QMessageBox, \
    QPushButton, QRadioButton, QTextEdit, QVBoxLayout, QGroupBox, QFormLayout, QComboBox, QCheckBox


class SignalLoadComnplexDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(LOAD_COMPLEX_SIGNAL)
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

        method_select_group = QGroupBox(CHOOSE_DIAGRAM_TYPE)
        method_select_layout = QVBoxLayout()

        self.method_group = QButtonGroup()
        self.w1 = QRadioButton(W1)
        self.w2 = QRadioButton(W2)

        self.method_group.addButton(self.w1)
        self.method_group.addButton(self.w2)

        method_select_layout.addWidget(self.w1)
        method_select_layout.addWidget(self.w2)
        method_select_group.setLayout(method_select_layout)

        layout.addWidget(method_select_group)

        # --- Przycisk wykonania ---
        perform_btn = QPushButton(SHOW_COMPLEX_SIGNAL)
        # perform_btn.clicked.connect(self.perform_transformation)
        layout.addWidget(perform_btn)


        self.setLayout(layout)

        self.signal1_data = None


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


