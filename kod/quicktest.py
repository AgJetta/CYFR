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
    
    # Calculate impulse response based on equation (4) from context
    h = np.zeros(M)
    center = (M - 1) // 2
    
    for n in range(M):
        if n == center:
            # For n = (M-1)/2, h(n) = 2/K
            h[n] = 2.0 / K
        else:
            # For other cases: sin(2π(n-(M-1)/2)/K) / (π(n-(M-1)/2))
            arg = 2 * np.pi * (n - center) / K
            h[n] = np.sin(arg) / (np.pi * (n - center))
    
    # Apply window function
    if window_type == 'hann':
        # Hanning window from equation (6): w(n) = 0.5 - 0.5*cos(2πn/M)
        window = np.array([0.5 - 0.5 * np.cos(2 * np.pi * n / M) for n in range(M)])
        h = h * window
    # For boxcar window, no multiplication needed (rectangular window = 1)
    
    return h

def design_highpass_filter(M, K, window_type='hann'):
    """
    Design a highpass FIR filter using spectral inversion of lowpass filter.
    
    Parameters:
    M: Number of filter coefficients (should be odd)
    K: Parameter defining cutoff frequency (fo = fp/K)
    window_type: 'boxcar' or 'hann'
    
    Returns:
    h: Filter impulse response coefficients
    """
    # Start with lowpass filter
    h_lp = design_lowpass_filter(M, K, window_type)
    
    # Convert to highpass using spectral inversion
    # Subtract from delta function (impulse at center)
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
    mode: 'same', 'full', or 'valid'
          - 'same': Output same length as input signal
          - 'full': Full convolution (len(signal) + len(filter) - 1)
          - 'valid': Only where filter completely overlaps signal
    
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

def plot_filter_response(h, title, fs=1.0):
    """
    Plot filter impulse response and frequency response.
    """
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))
    
    # Plot impulse response
    ax1.stem(range(len(h)), h)
    ax1.set_title(f'{title} - Impulse Response')
    ax1.set_xlabel('Sample n')
    ax1.set_ylabel('h(n)')
    ax1.grid(True)
    
    # Calculate frequency response
    N = 512  # Number of frequency points
    H = np.fft.fft(h, N)
    freqs = np.fft.fftfreq(N, 1/fs)[:N//2]
    
    # Plot magnitude response (linear scale)
    ax2.plot(freqs, np.abs(H[:N//2]))
    ax2.set_title(f'{title} - Magnitude Response (Linear)')
    ax2.set_xlabel('Frequency')
    ax2.set_ylabel('|H(f)|')
    ax2.grid(True)
    
    # Plot magnitude response (logarithmic scale)
    ax3.plot(freqs, 20 * np.log10(np.abs(H[:N//2]) + 1e-10))
    ax3.set_title(f'{title} - Magnitude Response (dB)')
    ax3.set_xlabel('Frequency')
    ax3.set_ylabel('|H(f)| [dB]')
    ax3.grid(True)
    ax3.set_ylim([-80, 10])
    
    plt.tight_layout()
    return fig

# Demonstration and testing
if __name__ == "__main__":
    # Filter parameters
    M = 25  # Number of coefficients (odd)
    K = 8   # Cutoff parameter (fo = fp/K)
    fs = 1000  # Sampling frequency
    
    print("Designing digital filters based on the window method...")
    print(f"Filter order: M = {M}")
    print(f"Cutoff parameter: K = {K}")
    print(f"Cutoff frequency: fo = fs/K = {fs/K} Hz")
    
    # Design filters
    h_lp_boxcar = design_lowpass_filter(M, K, 'boxcar')
    h_hp_hann = design_highpass_filter(M, K, 'hann')
    
    # Create test signal (combination of low and high frequency components)
    t = np.linspace(0, 1, fs, endpoint=False)
    low_freq = 50   # Hz
    high_freq = 300  # Hz
    test_signal = (np.sin(2 * np.pi * low_freq * t) + 
                   0.5 * np.sin(2 * np.pi * high_freq * t) + 
                   0.1 * np.random.randn(len(t)))  # Add some noise
    
    # Apply filters
    filtered_lp = apply_filter(test_signal, h_lp_boxcar)
    filtered_hp = apply_filter(test_signal, h_hp_hann)
    
    # Plot results
    plt.figure(figsize=(12, 10))
    
    # Original signal
    plt.subplot(3, 1, 1)
    plt.plot(t[:200], test_signal[:200])
    plt.title('Original Signal (50 Hz + 300 Hz + noise)')
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude')
    plt.grid(True)
    
    # Lowpass filtered signal
    plt.subplot(3, 1, 2)
    plt.plot(t[:200], filtered_lp[:200])
    plt.title('Lowpass Filtered (Boxcar Window)')
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude')
    plt.grid(True)
    
    # Highpass filtered signal
    plt.subplot(3, 1, 3)
    plt.plot(t[:200], filtered_hp[:200])
    plt.title('Highpass Filtered (Hann Window)')
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude')
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()
    
    # Plot filter characteristics
    plot_filter_response(h_lp_boxcar, "Lowpass Filter (Boxcar Window)", fs)
    plt.show()
    
    plot_filter_response(h_hp_hann, "Highpass Filter (Hann Window)", fs)
    plt.show()
    
    # Print filter coefficients
    print("\nLowpass Filter Coefficients (Boxcar Window):")
    print([f"{coeff:.6f}" for coeff in h_lp_boxcar])
    
    print("\nHighpass Filter Coefficients (Hann Window):")
    print([f"{coeff:.6f}" for coeff in h_hp_hann])