
import matplotlib.pyplot as plt
from sympy.physics.control.control_plots import matplotlib

matplotlib.use('TkAgg')  # Set the backend

import numpy as np


def sample(signal, metadata, target_freq):

    # Extract the original sampling frequency from the metadata
    original_freq = metadata.get('sampling_freq', None)
    if original_freq is None:
        raise ValueError("Original sampling frequency not found in metadata.")

    # Calculate the downsampling factor
    downsampling_factor = original_freq / target_freq
    if downsampling_factor < 1:
        raise ValueError("Target frequency must be lower than the original frequency.")
    # print("Downsampling: ", downsampling_factor)
    # Perform the downsampling by selecting every nth sample
    downsampled_signal = signal[::int(downsampling_factor)]

    new_metadata = metadata.copy()
    new_metadata['sampling_freq'] = target_freq  # New frequency
    new_metadata['num_samples'] = len(downsampled_signal)  # Update number of samples

    return downsampled_signal, new_metadata


def quantize(signal, metadata, num_levels=16):

    # Get the range of the signal (min and max values)
    min_val = np.min(signal)
    max_val = np.max(signal)

    # Calculate the quantization step size
    step_size = (max_val - min_val) / (num_levels - 1)

    # Perform quantization by scaling the signal and rounding it to the nearest level
    quantized_signal = np.round((signal - min_val) / step_size) * step_size + min_val

    # Update metadata with quantization information
    quantized_metadata = metadata.copy()
    quantized_metadata['num_levels'] = num_levels
    quantized_metadata['min_value'] = min_val
    quantized_metadata['max_value'] = max_val
    quantized_metadata['step_size'] = step_size

    # print(f"Quantization with {num_levels} levels:")
    # print(f"Signal range: {min_val} to {max_val}")
    # print(f"Step size: {step_size}")

    return quantized_signal, quantized_metadata

def extrapolate(signal, metadata, target_frequency):
    # Calculate time arrays
    original_fs = metadata['sampling_freq']
    duration = len(signal) / original_fs
    
    sample_times = np.linspace(0, duration, len(signal), endpoint=False)
    target_times = np.linspace(0, duration, int(duration * target_frequency), endpoint=False)
    
    # Use array indexing for efficiency
    indices = np.searchsorted(sample_times, target_times, side='right') - 1
    indices = np.clip(indices, 0, len(signal) - 1)
    
    extrapolated_signal = signal[indices]
    extrapolated_metadata = metadata.copy()
    extrapolated_metadata['sampling_freq'] = target_frequency
    extrapolated_metadata['num_samples'] = len(extrapolated_signal)
    return extrapolated_signal, extrapolated_metadata

def interpolate(signal, metadata, target_frequency):
    # Calculate time arrays
    original_fs = metadata['sampling_freq']
    duration = len(signal) / original_fs
    
    sample_times = np.linspace(0, duration, len(signal), endpoint=False)
    target_times = np.linspace(0, duration, int(duration * target_frequency), endpoint=False)
    
    interpolated_signal = np.interp(target_times, sample_times, signal)
    interpolated_metadata = metadata.copy()
    interpolated_metadata['sampling_freq'] = target_frequency
    interpolated_metadata['num_samples'] = len(interpolated_signal)
    
    return interpolated_signal, interpolated_metadata

def reconstruct(signal, metadata, target_frequency):
    original_fs = metadata['sampling_freq']
    duration = len(signal) / original_fs
    
    sample_times = np.linspace(0, duration, len(signal), endpoint=False)
    target_times = np.linspace(0, duration, int(duration * target_frequency), endpoint=False)
    
    reconstructed = np.zeros(len(target_times))
    T = 1/original_fs  # Sample period
    
    for n in range(len(signal)):
        # Calculate sinc contribution for each sample
        sinc_values = np.sinc((target_times - sample_times[n]) / T)
        reconstructed += signal[n] * sinc_values
        
    reconstructed_metadata = metadata.copy()
    reconstructed_metadata['sampling_freq'] = target_frequency
    reconstructed_metadata['num_samples'] = len(reconstructed)
    return reconstructed, reconstructed_metadata