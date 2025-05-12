import numpy as np
from logic_signal_file_handler import SignalFileHandler
from strings import *
from PyQt5.QtWidgets import QButtonGroup, QDialog, QFileDialog, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QRadioButton, QTextEdit, QVBoxLayout
from logic_comparisons import mean_squared_error, signal_to_noise_ratio, peak_signal_to_noise_ratio, max_difference


class SignalComparisonDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(SIGNAL_COMPARISON_DIALOG_TITLE)
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

        signal2_layout = QHBoxLayout()
        self.signal2_path = QLineEdit()
        self.signal2_path.setReadOnly(True)
        signal2_btn = QPushButton(LOAD_SIGNAL_2)
        signal2_btn.clicked.connect(lambda: self.load_signal(self.signal2_path))
        signal2_layout.addWidget(QLabel(SIGNAL_2_LABEL))
        signal2_layout.addWidget(self.signal2_path)
        signal2_layout.addWidget(signal2_btn)
        layout.addLayout(signal2_layout)

        self.signal2_params = QTextEdit()
        self.signal2_params.setReadOnly(True)
        layout.addWidget(self.signal2_params)

        compare_btn = QPushButton(PERFORM_COMPARISON)
        compare_btn.clicked.connect(self.perform_comparison)
        layout.addWidget(compare_btn)

        self.setLayout(layout)

        self.signal1_data = None
        self.signal2_data = None
        self.signal1_metadata = None
        self.signal2_metadata = None

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
                    self.signal1_metadata = metadata
                else:
                    self.signal2_params.setText(params_text)
                    self.signal2_data = signal_data
                    self.signal2_metadata = metadata
            except Exception as e:
                QMessageBox.critical(self, "Error", ERROR_LOADING.format(str(e)))

    
    def perform_comparison(self):
        if self.signal1_data is None or self.signal2_data is None:
            QMessageBox.critical(self, "Error", ERROR_LOAD_BOTH)
            return

        if len(self.signal1_data) != len(self.signal2_data):
            QMessageBox.critical(self, "Error", ERROR_N_SAMPLES)
            return
        
        # Draw both signals
        time_array1 = np.linspace(
                self.signal1_metadata['start_time'], 
                self.signal1_metadata['start_time'] + len(self.signal1_data)/self.signal1_metadata['sampling_freq'], 
                len(self.signal1_data)
            )
        time_array2 = np.linspace(
                self.signal2_metadata['start_time'], 
                self.signal2_metadata['start_time'] + len(self.signal2_data)/self.signal2_metadata['sampling_freq'], 
                len(self.signal2_data)
            )
        
        drawing_shortcut = self.parent()
        drawing_shortcut.signal_ax.clear()
        drawing_shortcut.histogram_ax.clear()
        # Plotting the signals
        drawing_shortcut.signal_ax.set_facecolor('#f0f0f0')
        drawing_shortcut.signal_ax.grid(True, color='white', linestyle='-', alpha=0.3)
        
        drawing_shortcut.signal_ax.axhline(y=0, color='purple', linestyle='--', alpha=0.3)
        drawing_shortcut.signal_ax.axvline(x=0, color='purple', linestyle='--', alpha=0.3)
        
        drawing_shortcut.signal_ax.plot(time_array1, self.signal1_data, color='red', linewidth=0.8)
        drawing_shortcut.signal_ax.plot(time_array2, self.signal2_data, color='blue', linewidth=0.8)
        drawing_shortcut.signal_ax.set_title(f'{COMPARISON_TITLE}')
        drawing_shortcut.signal_ax.set_xlabel(TIME_AXIS)
        drawing_shortcut.signal_ax.set_ylabel(AMPLITUDE_AXIS)
        
        drawing_shortcut.histogram_ax.set_facecolor('#f0f0f0')
        drawing_shortcut.histogram_ax.clear()

        drawing_shortcut.signal_figure.tight_layout()
        drawing_shortcut.signal_canvas.draw()

        self.calculate_comparisons()

        self.close()

    def calculate_comparisons(self):
        mse = mean_squared_error(self.signal1_data, self.signal2_data)
        snr = signal_to_noise_ratio(self.signal1_data, self.signal2_data)
        psnr = peak_signal_to_noise_ratio(self.signal1_data, self.signal2_data)
        md = max_difference(self.signal1_data, self.signal2_data)

        params = {
            'MSE': mse,
            'SNR': snr,
            'PSNR': psnr,
            'MD': md
        }

        param_text = '\n'.join([f'{k}: {v:.4f}' for k, v in params.items()])
        self.parent().parameters_text.setText(param_text)
        self.parent().parameters_text.setVisible(True)
        self.parent().parameters_text.setReadOnly(True)
