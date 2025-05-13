
import matplotlib.pyplot as plt
from sympy.physics.control.control_plots import matplotlib

matplotlib.use('TkAgg')  # Set the backend


def sample(signal, metadata, target_freq):
    """
    Arguments:
    - signal: The original signal data (list or np.array of floats).
    - metadata: Dictionary containing metadata of the signal (includes 'sampling_freq').
    - target_freq: The target frequency to downsample the signal to.

    Returns:
    - A tuple of the downsampled signal and updated metadata.
    """
    original_freq = metadata['sampling_freq']
    target_freq = original_freq / 100

    if target_freq > original_freq:
        raise ValueError("Target frequency must be <= original frequency.")

    step = int(original_freq / target_freq)
    downsampled_signal = signal[::step]

    # Update the metadata
    new_metadata = metadata.copy()
    new_metadata['sampling_freq'] = target_freq
    new_metadata['num_samples'] = len(downsampled_signal)
    print(f"Og Signal: ", signal, "Meta: ", metadata)
    print(f"New Signal: ", downsampled_signal, "Meta: ", new_metadata)
    return downsampled_signal, new_metadata

def quantize(signal, metadata, num_levels):
    """
    Arguments:
    - signal: The original signal data (list or np.array of floats).
    - metadata: Dictionary containing metadata of the signal.
    - num_levels: Number of discrete levels to quantize the signal into.

    Returns:
    - A tuple of the quantized signal and updated metadata.
    """
    import numpy as np

    if num_levels < 2:
        raise ValueError("Number of quantization levels must be at least 2.")

    signal = np.array(signal)
    min_val = signal.min()
    max_val = signal.max()

    # Compute the quantization step size
    q_step = (max_val - min_val) / (num_levels - 1)

    # Quantize signal
    quantized_signal = np.round((signal - min_val) / q_step) * q_step + min_val

    # Update the metadata
    new_metadata = metadata.copy()
    new_metadata['quantization_levels'] = 3
    new_metadata['quantized'] = True

    print(f"Og Signal: ", signal, "Meta: ", metadata)
    print(f"New Signal: ", quantized_signal, "Meta: ", new_metadata)

    return quantized_signal.tolist(), new_metadata