from PyQt5.QtWidgets import QMessageBox

import json
import struct
from logic_signal_conversion import *
from strings import *
from filtering import (
    design_lowpass_filter, design_highpass_filter, apply_filter
)


class SignalFileHandler:
    @staticmethod
    def save_signal(filename, signal_data, metadata: dict = None, start_time=0, sampling_freq=1, is_complex=False,
                    duration=None):
        # If metadata is provided, use its values and override the arguments
        if metadata is not None:
            start_time = metadata.get('start_time', start_time)
            sampling_freq = metadata.get('sampling_freq', sampling_freq)
            is_complex = metadata.get('is_complex', is_complex)
            num_samples = metadata.get('num_samples', len(signal_data))
            duration = metadata.get('duration', duration if duration is not None else num_samples / sampling_freq)
        else:
            num_samples = len(signal_data)
            # Calculate duration if not provided

        print("Saving signal, metadata")
        print(metadata)
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

    @staticmethod
    def perform_signal_filtering(signal, metadata, operation,
                                 filtering_frequency=None, num_of_taps=None, is_hanning_window=False):
        if filtering_frequency is None or num_of_taps is None:
            raise ValueError("Filtering frequency and number of taps must be provided.")

        sampling_freq = metadata.get("sampling_freq")
        if sampling_freq is None:
            raise ValueError("Sampling frequency is missing in metadata.")

        nyquist = sampling_freq / 2.0
        normalized_cutoff = filtering_frequency / nyquist

        if not (0 < normalized_cutoff < 1):
            raise ValueError("Cutoff frequency must be between 0 and Nyquist frequency.")

        # Window type
        if is_hanning_window:
            window_type = 'hann'
        else:
            window_type = 'boxcar'

        if operation == LOW_PASS_FILTER:
            filter_function = design_lowpass_filter
        elif operation == HIGH_PASS_FILTER:
            filter_function = design_highpass_filter
        else:
            raise ValueError(f"Unsupported operation: {operation}")

        K = np.floor(sampling_freq / filtering_frequency)
        filtered_signal = apply_filter(signal, filter_function(num_of_taps, K, window_type))

        new_metadata = metadata.copy()
        new_metadata["filtering_frequency"] = filtering_frequency
        new_metadata["num_of_taps"] = num_of_taps
        new_metadata["is_hanning_window"] = is_hanning_window

        return filtered_signal, new_metadata


    def perform_convolution(signal1, signal2, metadata1=None, metadata2=None):
        """
        Perform 1D discrete convolution of signal1 with signal2.
        Assumes signal1 is h(k) and signal2 is x(n).
        """
        M = len(signal1)
        N = len(signal2)
        output_length = M + N - 1
        result = np.zeros(output_length)

        print("DEBUG INFO:")
        print(f"Length of signal1 (h): {M}")
        print(f"Length of signal2 (x): {N}")
        print(f"Output length: {output_length}")
        print(f"Max/Min of signal1: {np.max(signal1)} / {np.min(signal1)}")
        print(f"Max/Min of signal2: {np.max(signal2)} / {np.min(signal2)}")
        print("-" * 40)

        result = np.convolve(signal1, signal2, mode='full')

        print("-" * 40)

        print(f"Max value in result: {np.max(result)}")
        print(f"Min value in result: {np.min(result)}")
        print("=" * 60)

        # Calculate new metadata
        start_time1 = metadata1.get("start_time", 0.0) if metadata1 else 0.0
        start_time2 = metadata2.get("start_time", 0.0) if metadata2 else 0.0

        if metadata2 and "sampling_freq" in metadata2:
            sampling_freq = metadata2["sampling_freq"]
        elif metadata1 and "sampling_freq" in metadata1:
            sampling_freq = metadata1["sampling_freq"]
        else:
            sampling_freq = 1.0  # fallback default

        num_samples = output_length
        duration = num_samples / sampling_freq if sampling_freq != 0 else 0

        new_metadata = {
            "start_time": start_time1 + start_time2,
            "sampling_freq": sampling_freq,
            "num_samples": num_samples,
            "duration": duration,
        }

        print("\nNEW METADATA:")
        print(new_metadata)
        print(f"Max value in result: {np.max(result)}")
        print(f"Min value in result: {np.min(result)}")
        print("=" * 60)

        print("NEW METADATA")
        print(new_metadata)
        return result, new_metadata

    @staticmethod
    def perform_correlation(signal1, signal2, signal1_metadata, signal2_metadata):
        M = len(signal1)
        N = len(signal2)
        output_length = M + N - 1

        result = np.correlate(signal1, signal2, mode='full')

        start_time1 = signal1_metadata.get("start_time", 0.0) if signal1_metadata else 0.0
        start_time2 = signal2_metadata.get("start_time", 0.0) if signal2_metadata else 0.0

        if signal2_metadata and "sampling_freq" in signal2_metadata:
            sampling_freq = signal2_metadata["sampling_freq"]
        elif signal1_metadata and "sampling_freq" in signal1_metadata:
            sampling_freq = signal1_metadata["sampling_freq"]
        else:
            sampling_freq = 1.0  # fallback default

        num_samples = output_length
        duration = num_samples / sampling_freq if sampling_freq != 0 else 0

        new_metadata = {
            "start_time": start_time1 + start_time2,
            "sampling_freq": sampling_freq,
            "num_samples": num_samples,
            "duration": duration,
        }

        return result, new_metadata

