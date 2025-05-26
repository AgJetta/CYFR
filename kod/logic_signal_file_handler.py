from PyQt5.QtWidgets import QMessageBox

import json
import struct
from logic_signal_conversion import *
from strings import *


class SignalFileHandler:
    @staticmethod
    def save_signal(filename, signal_data, metadata=None, start_time=0, sampling_freq=1, is_complex=False,
                    duration=None):
        # If metadata is provided, use its values and override the arguments
        if metadata is not None:
            start_time = metadata.get('start_time', start_time)
            sampling_freq = metadata.get('sampling_freq', sampling_freq)
            is_complex = metadata.get('is_complex', is_complex)
            num_samples = metadata.get('num_samples', len(signal_data))
            duration = metadata.get('duration', duration)
        else:
            num_samples = len(signal_data)
            # Calculate duration if not provided
            if duration is None:
                duration = num_samples / sampling_freq

        # Build metadata
        metadata = {
            'start_time': start_time,
            'sampling_freq': sampling_freq,
            'is_complex': is_complex,
            'num_samples': num_samples,
            'duration': duration
        }

        # Write to file
        with open(filename, 'wb') as f:
            metadata_json = json.dumps(metadata).encode('utf-8')
            f.write(struct.pack('I', len(metadata_json)))
            f.write(metadata_json)

            if is_complex:
                # Write complex signal (real and imaginary parts)
                for value in signal_data:
                    f.write(struct.pack('dd', value.real, value.imag))
            else:
                # Write real signal
                for value in signal_data:
                    f.write(struct.pack('d', value))  # Double precision float


    @staticmethod
    def load_signal(filename):
        with open(filename, 'rb') as f:
            # Read and unpack the metadata length
            metadata_len = struct.unpack('I', f.read(4))[0]

            # Read and decode metadata
            metadata_json = f.read(metadata_len).decode('utf-8')
            metadata = json.loads(metadata_json)

            # Load the signal data based on whether it is complex or real
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

            # Return both metadata (including duration) and signal data
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
    def perform_signal_conversion(signal, metadata, operation, frequency = None, quantization_lvl = None):
        if operation == SAMPLING:
            downsampled_signal, downsampled_metadata = sample(signal, metadata, frequency)
            return downsampled_signal, downsampled_metadata
        elif operation == QUANTIZATION:
            quantized_signal, quantized_metadata = quantize(signal, metadata, quantization_lvl)
            return quantized_signal, quantized_metadata
        elif operation == EXTRAPOLATION:
            return extrapolate(signal, metadata, frequency)  # Extrapolation logic remains the same
        elif operation == INTERPOLATION:
            return interpolate(signal, metadata, frequency)  # Implement the first-order interpolation
        elif operation == RECONSTRUCTION:
            return reconstruct(signal, metadata, frequency)  # Implement sinc-based reconstruction

        else:
            raise ValueError(f"Unsupported operation: {operation}")

    def perform_convolution(signal1, signal2, metadata1=None, metadata2=None):
        """
        Perform 1D discrete convolution of signal1 with signal2.
        Assumes signal1 is h(k) and signal2 is x(n).
        """
        M = len(signal1)
        N = len(signal2)
        output_length = M + N - 1
        result = np.zeros(output_length)

        for n in range(output_length):
            for k in range(M):
                if 0 <= n - k < N:
                    result[n] += signal1[k] * signal2[n - k]

        # Calculate new metadata
        start_time1 = metadata1.get("start_time", 0.0) if metadata1 else 0.0
        start_time2 = metadata2.get("start_time", 0.0) if metadata2 else 0.0

        # Pick sampling frequency from the input signal (signal2) if available, else signal1
        sampling_freq = None
        if metadata2 and "sampling_freq" in metadata2:
            sampling_freq = metadata2["sampling_freq"]
        elif metadata1 and "sampling_freq" in metadata1:
            sampling_freq = metadata1["sampling_freq"]
        else:
            sampling_freq = 1.0  # fallback default

        is_complex = False
        if metadata1 and metadata1.get("is_complex", False):
            is_complex = True
        if metadata2 and metadata2.get("is_complex", False):
            is_complex = True

        num_samples = output_length
        duration = num_samples / sampling_freq if sampling_freq != 0 else 0

        new_metadata = {
            "start_time": start_time1 + start_time2,
            "sampling_freq": sampling_freq,
            "is_complex": is_complex,
            "num_samples": num_samples,
            "duration": duration,
        }

        print("NEW METADATA")
        print(new_metadata)
        return result, new_metadata
