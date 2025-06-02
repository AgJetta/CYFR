import numpy as np
import matplotlib.pyplot as plt

def design_lowpass_filter(M, K, window_type='boxcar'):
    """
    Design a lowpass FIR filter using the window method.
    
    Parameters:
    M: Number of filter coefficients (should be odd)
    K: Parameter defining cutoff frequency (fo = fp/K)
    window_type: 'boxcar' or 'hann'
    
    Returns:
    h: Filter impulse response coefficients
    """
    if M % 2 == 0:
        raise ValueError("M should be odd for symmetric filter")
    
    h = np.zeros(M)
    center = (M - 1) // 2
    
    for n in range(M):
        if n == center:
            # For n = (M-1)/2, h(n) = 2/K
            h[n] = 2.0 / K
        else:
            # Otherwise: sin(2π(n-(M-1)/2)/K) / (π(n-(M-1)/2))
            arg = 2 * np.pi * (n - center) / K
            h[n] = np.sin(arg) / (np.pi * (n - center))
    
    # Apply window function
    if window_type == 'hann':
        # w(n) = 0.5 - 0.5*cos(2πn/M)
        window = np.array([0.5 - 0.5 * np.cos(2 * np.pi * n / M) for n in range(M)])
        h = h * window

    return h

def design_highpass_filter(M, K, window_type='hann'):
    """
    Design a highpass FIR filter using spectral inversion of lowpass filter.
    
    Returns:
    h: Filter impulse response coefficients
    """
    h_lp = design_lowpass_filter(M, K, window_type)
    
    h_hp = -h_lp
    center = (M - 1) // 2
    h_hp[center] += 1  # Add unit impulse at center
    
    return h_hp

def apply_filter(signal, filter_coeffs, mode='same'):
    """
    Apply FIR filter to signal using convolution.
    Based on equation (3) from context: y(n) = Σ h(k)x(n-k)
    
    Parameters:
    signal: Input signal
    filter_coeffs: Filter impulse response coefficients
    
    Returns:
    filtered_signal: Output signal
    """
    if mode == 'same':
        # Ensure output length matches input signal length
        result = np.convolve(signal, filter_coeffs, mode='full')
        # Extract the central portion matching input length
        delay = len(filter_coeffs) // 2
        start_idx = delay
        end_idx = start_idx + len(signal)
        return result[start_idx:end_idx]
    else:
        return np.convolve(signal, filter_coeffs, mode=mode)