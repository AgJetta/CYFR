

def sample(signal, original_freq, target_freq):
    """
    Próbkuje sygnał do niższej częstotliwości próbkowania (downsampling).
    Zakłada, że sygnał to lista wartości (float) próbkowana z częstotliwością original_freq.
    """
    if target_freq > original_freq:
        raise ValueError("Target frequency must be <= original frequency.")

    step = int(original_freq / target_freq)
    return signal[::step]

