import numpy as np
from strings import (MEAN_VALUE, ABSOLUTE_MEAN_VALUE, RMS_VALUE, 
                    VARIANCE, AVERAGE_POWER)


class SignalGenerator:
    @staticmethod
    def generate_uniform_noise(amplitude, start_time, duration, sampling_rate=1000):
        t = np.linspace(start_time, start_time + duration, int(duration * sampling_rate))
        noise = np.random.uniform(-amplitude, amplitude, len(t))  # U(-A, A)
        return t, noise

    @staticmethod
    def generate_gaussian_noise(amplitude, start_time, duration, sampling_rate=1000):
        t = np.linspace(start_time, start_time + duration, int(duration * sampling_rate))
        noise = amplitude * np.random.normal(0, 1, len(t))  # u = 0, sigma = 1
        return t, noise

    @staticmethod
    def generate_sinusoidal(amplitude, period, start_time, duration, sampling_rate=1000):
        t = np.linspace(start_time, start_time + duration, int(duration * sampling_rate))
        signal = amplitude * np.sin(2 * np.pi * (t - start_time) / period)
        return t, signal

    @staticmethod
    def generate_half_wave_rectified(amplitude, period, start_time, duration, sampling_rate=1000):
        t = np.linspace(start_time, start_time + duration, int(duration * sampling_rate))
        sin_wave = np.sin(2 * np.pi * (t - start_time) / period)
        signal = amplitude / 2 * (sin_wave + np.abs(sin_wave))
        return t, signal

    @staticmethod
    def generate_full_wave_rectified(amplitude, period, start_time, duration, sampling_rate=1000):
        t = np.linspace(start_time, start_time + duration, int(duration * sampling_rate))
        sin_wave = np.sin(2 * np.pi * (t - start_time) / period)
        signal = amplitude * np.abs(sin_wave)
        return t, signal

    @staticmethod
    def generate_square_wave(amplitude, period, start_time, duration, duty_cycle=0.5, sampling_rate=1000):
        t = np.linspace(start_time, start_time + duration, int(duration * sampling_rate))
        signal = amplitude * (((t - start_time) % period) / period <= duty_cycle).astype(float)
        return t, signal

    @staticmethod
    def generate_symmetric_square_wave(amplitude, period, start_time, duration, duty_cycle=0.5, sampling_rate=1000):
        t, signal = SignalGenerator.generate_square_wave(amplitude, period, start_time, duration, duty_cycle, sampling_rate)
        signal[signal == 0] = -amplitude
        return t, signal

    @staticmethod
    def generate_triangular_wave(amplitude, period, start_time, duration, duty_cycle=0.5, sampling_rate=1000):
        t = np.linspace(start_time, start_time + duration, int(duration * sampling_rate))
        phase = (t - start_time) % period / period
        signal = amplitude * (2 * np.abs(2 * (phase - duty_cycle)) - 1)
        return t, signal

    @staticmethod
    def generate_unit_step(amplitude, start_time, duration, step_time=None, sampling_rate=1000):
        t = np.linspace(start_time, start_time + duration, int(duration * sampling_rate))
        signal = np.zeros_like(t)
        mask = t > step_time
        signal[mask] = amplitude
        signal[t == step_time] = amplitude / 2
        return t, signal

    @staticmethod
    def generate_unit_impulse(amplitude, first_sample_index, peak_sample_index, number_of_samples, sampling_rate=1000):
        t = np.arange(first_sample_index, first_sample_index + number_of_samples) / sampling_rate
        signal = np.zeros_like(t)
        peak_index = peak_sample_index - first_sample_index
        if 0 <= peak_index < len(signal):
            signal[peak_index] = amplitude
        return t, signal

    @staticmethod
    def generate_unit_noise(amplitude, start_time, duration, sampling_rate=1000, probability=0.5):
        t = np.linspace(start_time, start_time + duration, int(duration * sampling_rate))
        signal = amplitude * np.random.binomial(1, probability, len(t))
        return t, signal

    @staticmethod
    def calculate_signal_parameters(signal):
        return {
            MEAN_VALUE: np.mean(signal),
            ABSOLUTE_MEAN_VALUE: np.mean(np.abs(signal)),
            RMS_VALUE: np.sqrt(np.mean(signal**2)),
            VARIANCE: np.var(signal),
            AVERAGE_POWER: np.mean(signal**2)
        }