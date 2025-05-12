import numpy as np

def mean_squared_error(original, reconstructed):
    """(C1) Mean Squared Error (MSE)"""
    original = np.array(original)
    reconstructed = np.array(reconstructed)
    return np.mean(np.abs(original - reconstructed) ** 2)

def signal_to_noise_ratio(original, reconstructed):
    """(C2) Signal-to-Noise Ratio (SNR)"""
    original = np.array(original)
    noise = original - np.array(reconstructed)
    signal_power = np.mean(np.abs(original) ** 2)
    noise_power = np.mean(np.abs(noise) ** 2)
    return 10 * np.log10(signal_power / noise_power) if noise_power != 0 else float('inf')

def peak_signal_to_noise_ratio(original, reconstructed):
    """(C3) Peak Signal-to-Noise Ratio (PSNR)"""
    mse = mean_squared_error(original, reconstructed)
    peak = np.max(np.abs(original))
    return 10 * np.log10((peak ** 2) / mse) if mse != 0 else float('inf')

def max_difference(original, reconstructed):
    """(C4) Maximum Difference (MD)"""
    return np.max(np.abs(np.array(original) - np.array(reconstructed)))

# # Example usage with loaded signals
# if __name__ == "__main__":
#     # Replace these with your actual signal arrays
#     signal1 = [1.0, 2.0, 3.0, 4.0]
#     signal2 = [1.1, 1.9, 3.2, 3.8]
#
#     print("MSE:", mean_squared_error(signal1, signal2))
#     print("SNR:", signal_to_noise_ratio(signal1, signal2), "dB")
#     print("PSNR:", peak_signal_to_noise_ratio(signal1, signal2), "dB")
#     print("Max Difference:", max_difference(signal1, signal2))
