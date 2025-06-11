import numpy as np
import pywt  # For wavelet transforms
from scipy.fft import fft
def perform_dif_fft(signal, metadata):
    """
    Perform a basic DIF FFT (using numpy/scipy's FFT).
    """
    # Ensure signal is a numpy array
    signal = np.asarray(signal, dtype=np.complex64 if metadata.get("is_complex", False) else np.float32)

    fft_result = fft(signal)

    sampling_freq = metadata.get("sampling_freq", 1.0)
    num_samples = len(fft_result)
    duration = num_samples / sampling_freq if sampling_freq != 0 else 0

    new_metadata = {
        "start_time": metadata.get("start_time", 0.0),
        "sampling_freq": sampling_freq,
        "is_complex": True,
        "num_samples": num_samples,
        "duration": duration,
    }

    return fft_result, new_metadata

def perform_wavelet_transform(signal, metadata, wavelet_name):
    """
    Perform a discrete wavelet transform using PyWavelets.
    """
    signal = np.asarray(signal, dtype=np.float32)

    coeffs = pywt.wavedec(signal, wavelet=wavelet_name.lower())
    flattened_coeffs, coeff_slices = pywt.coeffs_to_array(coeffs)

    sampling_freq = metadata.get("sampling_freq", 1.0)
    num_samples = len(flattened_coeffs)
    duration = num_samples / sampling_freq if sampling_freq != 0 else 0

    new_metadata = {
        "start_time": metadata.get("start_time", 0.0),
        "sampling_freq": sampling_freq,
        "is_complex": False,
        "num_samples": num_samples,
        "duration": duration,
        "wavelet": wavelet_name,
    }

    return flattened_coeffs, new_metadata