import numpy as np
from PyQt5.QtWidgets import QMessageBox

import json
import struct
from logic_signal_conversion import *
from strings import *


class SignalFileHandler:
    @staticmethod
    def save_signal(filename, signal_data, start_time=0, sampling_freq=1, is_complex=False):
        import struct
        import json

        metadata = {
            'start_time': start_time,
            'sampling_freq': sampling_freq,
            'is_complex': is_complex,
            'num_samples': len(signal_data)
        }

        with open(filename, 'wb') as f:
            metadata_json = json.dumps(metadata).encode('utf-8')
            f.write(struct.pack('I', len(metadata_json)))
            f.write(metadata_json)

            if is_complex:
                # Write complex signal (pairs of floats: real and imaginary parts)
                for value in signal_data:
                    f.write(struct.pack('dd', value.real, value.imag))
            else:
                # Write real signal (single double precision float)
                for value in signal_data:
                    f.write(struct.pack('d', value))  # Double precision float

    @staticmethod
    def load_signal(filename):

        with open(filename, 'rb') as f:
            metadata_len = struct.unpack('I', f.read(4))[0]

            metadata_json = f.read(metadata_len).decode('utf-8')
            metadata = json.loads(metadata_json)

            signal_data = []
            if metadata['is_complex']:
                # Load complex signal (pairs of floats: real and imaginary parts)
                while True:
                    value_bytes = f.read(16)  # 16 bytes for two doubles (real + imaginary)
                    if not value_bytes:
                        break
                    real, imag = struct.unpack('dd', value_bytes)
                    signal_data.append(complex(real, imag))  # Create a complex number
            else:
                # Load real signal (single double precision float)
                while True:
                    value_bytes = f.read(8)  # 8 bytes for one double
                    if not value_bytes:
                        break
                    signal_data.append(struct.unpack('d', value_bytes)[0])

            return metadata, np.array(signal_data)

    @staticmethod
    def text_representation(filename):
        metadata, signal_data = SignalFileHandler.load_signal(filename)

        text_repr = "Signal Metadata:\n"
        for key, value in metadata.items():
            text_repr += f"{key}: {value}\n"

        text_repr += "\nSignal Data:\n"
        for i, value in enumerate(signal_data):
            if isinstance(value, complex):
                text_repr += f"Sample {i}: Real={value.real}, Imaginary={value.imag}\n"
            else:
                text_repr += f"Sample {i}: {value}\n"

        return text_repr

    @staticmethod
    def perform_signal_operation(signal1, signal2, operation):
        if len(signal1) != len(signal2):
            QMessageBox.critical(None, "Error", "Signals must be of the same length.")
            return None

        if operation == OPERATION_ADD:
            return signal1 + signal2
        elif operation == OPERATION_SUBTRACT:
            return signal1 - signal2
        elif operation == OPERATION_MULTIPLY:
            return signal1 * signal2
        elif operation == OPERATION_DIVIDE:
            # Prevent division by zero
            signal2_safe = signal2.copy()
            signal2_safe[signal2_safe == 0] = 1e-10
            return signal1 / signal2_safe
        else:
            raise ValueError(f"Unsupported operation: {operation}")

    @staticmethod
    def perform_signal_conversion(signal1, operation):
        if operation == SAMPLING:
            print("\nWykonuję downsampling sygnału...")
            print(f"Sygnał przed: ", signal1)
            original_freq = 1000
            target_freq = 500
            downsampled_signal = sample(signal1, original_freq, target_freq)
            return downsampled_signal
        elif operation == QUANTIZATION:
            return signal1
        elif operation == EXTRAPOLATION:
            return signal1
        elif operation == INTERPOLATION:
            return signal1
        elif operation == RECONSTRUCTION:
            return signal1
        else:
            raise ValueError(f"Unsupported operation: {operation}")


