from logic_signal_file_handler import SignalFileHandler
from strings import *
from PyQt5.QtWidgets import QButtonGroup, QDialog, QFileDialog, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QRadioButton, QTextEdit, QVBoxLayout

class SignalOperationDialog(QDialog):
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

        operation_layout = QHBoxLayout()
        self.operation_group = QButtonGroup()
        operations = [OPERATION_ADD, OPERATION_SUBTRACT, OPERATION_MULTIPLY, OPERATION_DIVIDE]
        for op in operations:
            radio_btn = QRadioButton(op)
            self.operation_group.addButton(radio_btn)
            operation_layout.addWidget(radio_btn)
        layout.addLayout(operation_layout)

        perform_btn = QPushButton(PERFORM_OPERATION)
        perform_btn.clicked.connect(self.perform_operation)
        layout.addWidget(perform_btn)

        self.setLayout(layout)

        self.signal1_data = None
        self.signal2_data = None

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
                else:
                    self.signal2_params.setText(params_text)
                    self.signal2_data = signal_data
            except Exception as e:
                QMessageBox.critical(self, "Error", ERROR_LOADING.format(str(e)))

    def perform_operation(self):
        if self.signal1_data is None or self.signal2_data is None:
            QMessageBox.critical(self, "Error", ERROR_LOAD_BOTH)
            return

        selected_op = self.operation_group.checkedButton()
        if not selected_op:
            QMessageBox.critical(self, "Error", ERROR_SELECT_OPERATION)
            return

        operation = selected_op.text()

        try:
            result_signal = SignalFileHandler.perform_signal_operation(
                self.signal1_data,
                self.signal2_data,
                operation
            )

            save_filename, _ = QFileDialog.getSaveFileName(self, SAVE_RESULT, "", "Binary Files (*.bin)")
            if save_filename:
                SignalFileHandler.save_signal(save_filename, result_signal)

                self.parent().generate_signal_from_file(save_filename)
                self.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", ERROR_OPERATION_FAILED.format(str(e)))