import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QPushButton, QLabel, QDoubleSpinBox, 
                            QSpinBox, QGroupBox, QGridLayout)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class DistanceSensorSimulator:
    def __init__(self, 
                 time_unit=1e-9, # nanoseconds
                 signal_velocity=3e8,   # m/s
                 sampling_frequency=1e9,  #  (Hz)
                 buffer_length=1024,   
                 probe_period=1e-6,      # microseconds
                 report_period=0.1):  # seconds
        
        self.time_unit = time_unit
        self.signal_velocity = signal_velocity
        self.fs = sampling_frequency
        self.dt = 1 / sampling_frequency
        self.buffer_length = buffer_length
        self.probe_period = probe_period
        self.report_period = report_period
        
        self.probe_signal = self._generate_probe_signal()
        
        self.tx_buffer = np.zeros(buffer_length)
        self.rx_buffer = np.zeros(buffer_length)
        
        self.current_time = 0
        
    def _generate_probe_signal(self):
        t = np.linspace(0, self.probe_period, int(self.probe_period * self.fs))
        
        f1 = 1 / self.probe_period      
        f2 = 3 / self.probe_period     
        
        signal = (np.sin(2 * np.pi * f1 * t) + 
                 0.5 * np.cos(2 * np.pi * f2 * t))
        
        return signal / np.max(np.abs(signal))
    
    def get_object_position(self, time):
        initial_distance = 100  # meters
        velocity = 10  # m/s
        return initial_distance + velocity * time
    
    def generate_received_signal(self, distance):
        round_trip_delay = 2 * distance / self.signal_velocity
        delay_samples = int(round_trip_delay * self.fs)
        
        received = np.zeros_like(self.probe_signal)
        if delay_samples < len(self.probe_signal) and delay_samples > 0:
            samples_to_copy = len(self.probe_signal) - delay_samples
            if samples_to_copy > 0:
                received[delay_samples:delay_samples + samples_to_copy] = self.probe_signal[:samples_to_copy]
        elif delay_samples == 0:
            received = self.probe_signal.copy()
        
        return received
    
    def update_buffers(self, distance):
        tx_signal = self.probe_signal[:self.buffer_length]
        rx_signal = self.generate_received_signal(distance)[:self.buffer_length]

        if len(tx_signal) < self.buffer_length:
            tx_signal = np.pad(tx_signal, (0, self.buffer_length - len(tx_signal)))
        if len(rx_signal) < self.buffer_length:
            rx_signal = np.pad(rx_signal, (0, self.buffer_length - len(rx_signal)))
            
        self.tx_buffer = tx_signal
        self.rx_buffer = rx_signal
    
    def perform_correlation_analysis(self):
        correlation = np.correlate(self.rx_buffer, self.tx_buffer, mode='full')
        
        center_idx = len(correlation) // 2
        
        right_half = correlation[center_idx:]
        max_idx = np.argmax(right_half)
        
        time_delay = max_idx * self.dt
        
        total_distance = self.signal_velocity * time_delay
        measured_distance = total_distance / 2
        
        return measured_distance, correlation, max_idx
    
    def simulate_measurement(self, actual_distance):
        self.update_buffers(actual_distance)
        
        measured_distance, correlation, delay_idx = self.perform_correlation_analysis()
        
        return measured_distance, correlation, delay_idx
    
    def run_simulation(self, simulation_time=10.0):
        times = []
        actual_distances = []
        measured_distances = []
        errors = []
        
        t = 0
        last_report_time = 0
        
        def moving_object(t):
            if t < 5:
                return 50 + 5 * t
            else:
                return 75 - 5 * (t - 5)
        
        self.get_object_position = moving_object
        
        while t < simulation_time:
            actual_dist = self.get_object_position(t)
        
            if t - last_report_time >= self.report_period:
                measured_dist, _, _ = self.simulate_measurement(actual_dist)
                
                times.append(t)
                actual_distances.append(actual_dist)
                measured_distances.append(measured_dist)
                errors.append(abs(measured_dist - actual_dist))
                
                last_report_time = t
            
            t += self.time_unit * 1000 
        
        return times, actual_distances, measured_distances, errors

class SimulationThread(QThread):
    finished = pyqtSignal(list, list, list, list)
    
    def __init__(self, simulator, simulation_time):
        super().__init__()
        self.simulator = simulator
        self.simulation_time = simulation_time
    
    def run(self):
        times, actual, measured, errors = self.simulator.run_simulation(self.simulation_time)
        self.finished.emit(times, actual, measured, errors)

class MplCanvas(FigureCanvasQTAgg):
    """Matplotlib canvas for PyQt5"""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super(MplCanvas, self).__init__(self.fig)

class DistanceSensorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Distance Sensor Simulator")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel for controls
        controls_panel = QWidget()
        controls_panel.setMaximumWidth(300)
        controls_layout = QVBoxLayout(controls_panel)
        
        # Title
        title = QLabel("Czujnik Odległości")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        controls_layout.addWidget(title)
        
        # Parameters group
        params_group = QGroupBox("Simulation Parameters")
        params_layout = QGridLayout(params_group)
        
        # Parameter controls
        self.time_unit_spin = QDoubleSpinBox()
        self.time_unit_spin.setDecimals(10)
        self.time_unit_spin.setRange(1e-12, 1e-6)
        self.time_unit_spin.setValue(1e-9)
        self.time_unit_spin.setSuffix(" s")
        params_layout.addWidget(QLabel("Jednostka Czasu:"), 0, 0)
        params_layout.addWidget(self.time_unit_spin, 0, 1)
        
        self.velocity_spin = QDoubleSpinBox()
        self.velocity_spin.setRange(1e6, 1e9)
        self.velocity_spin.setValue(3e8)
        self.velocity_spin.setSuffix(" m/s")
        params_layout.addWidget(QLabel("Prędkość sygnału:"), 1, 0)
        params_layout.addWidget(self.velocity_spin, 1, 1)
        
        self.sampling_freq_spin = QDoubleSpinBox()
        self.sampling_freq_spin.setRange(1e6, 1e12)
        self.sampling_freq_spin.setValue(1e9)
        self.sampling_freq_spin.setSuffix(" Hz")
        params_layout.addWidget(QLabel("Częstotliwośc próbkowania:"), 2, 0)
        params_layout.addWidget(self.sampling_freq_spin, 2, 1)
        
        self.buffer_length_spin = QSpinBox()
        self.buffer_length_spin.setRange(64, 40960)
        self.buffer_length_spin.setValue(1024)
        params_layout.addWidget(QLabel("Rozmiar bufora:"), 3, 0)
        params_layout.addWidget(self.buffer_length_spin, 3, 1)
        
        self.probe_period_spin = QDoubleSpinBox()
        self.probe_period_spin.setDecimals(8)
        self.probe_period_spin.setRange(1e-9, 1e-3)
        self.probe_period_spin.setValue(1e-6)
        self.probe_period_spin.setSuffix(" s")
        params_layout.addWidget(QLabel("Okres syg. sondującego:"), 4, 0)
        params_layout.addWidget(self.probe_period_spin, 4, 1)
        
        self.report_period_spin = QDoubleSpinBox()
        self.report_period_spin.setRange(0.01, 10.0)
        self.report_period_spin.setValue(0.5)
        self.report_period_spin.setSuffix(" s")
        params_layout.addWidget(QLabel("Okres Raportowania:"), 5, 0)
        params_layout.addWidget(self.report_period_spin, 5, 1)
        
        self.sim_time_spin = QDoubleSpinBox()
        self.sim_time_spin.setRange(1.0, 100.0)
        self.sim_time_spin.setValue(10.0)
        self.sim_time_spin.setSuffix(" s")
        params_layout.addWidget(QLabel("Czas trwania symulacji:"), 6, 0)
        params_layout.addWidget(self.sim_time_spin, 6, 1)
        
        controls_layout.addWidget(params_group)
        
        # Run button
        self.run_button = QPushButton("Uruchomić Symulację")
        self.run_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-size: 14px; padding: 10px; }")
        self.run_button.clicked.connect(self.run_simulation)
        controls_layout.addWidget(self.run_button)
        
        # Status label
        self.status_label = QLabel("Gotowe do symulacji")
        self.status_label.setStyleSheet("QLabel { color: #666; font-style: italic; }")
        controls_layout.addWidget(self.status_label)
        
        # Results group
        self.results_group = QGroupBox(" ")
        results_layout = QVBoxLayout(self.results_group)
        self.results_label = QLabel("Oczekujemy wyników...")
        results_layout.addWidget(self.results_label)
        controls_layout.addWidget(self.results_group)
        
        controls_layout.addStretch()
        
        # Right panel for plots
        self.canvas = MplCanvas(self, width=8, height=10, dpi=100)
        
        # Add panels to main layout
        main_layout.addWidget(controls_panel)
        main_layout.addWidget(self.canvas)
        
        # Thread for simulation
        self.sim_thread = None
    
    def run_simulation(self):
        """Start simulation in separate thread"""
        if self.sim_thread and self.sim_thread.isRunning():
            return
        
        self.run_button.setEnabled(False)
        self.status_label.setText("Symulacja w trakcie...")
        
        simulator = DistanceSensorSimulator(
            time_unit=self.time_unit_spin.value(),
            signal_velocity=self.velocity_spin.value(),
            sampling_frequency=self.sampling_freq_spin.value(),
            buffer_length=self.buffer_length_spin.value(),
            probe_period=self.probe_period_spin.value(),
            report_period=self.report_period_spin.value()
        )
        
        self.sim_thread = SimulationThread(simulator, self.sim_time_spin.value())
        self.sim_thread.finished.connect(self.on_simulation_finished)
        self.sim_thread.start()
    
    def on_simulation_finished(self, times, actual_distances, measured_distances, errors):
        self.run_button.setEnabled(True)
        self.status_label.setText("Symulacja zakończona")
        
        self.plot_results(times, actual_distances, measured_distances, errors)
    
    def plot_results(self, times, actual_distances, measured_distances, errors):
        """Plot simulation results"""
        self.canvas.fig.clear()
        
        # Create subplots
        ax1 = self.canvas.fig.add_subplot(2, 2, 1)
        ax2 = self.canvas.fig.add_subplot(2, 2, 2)
        ax3 = self.canvas.fig.add_subplot(2, 2, 3)
        ax4 = self.canvas.fig.add_subplot(2, 2, 4)
        
        # Distance comparison
        ax1.plot(times, actual_distances, 'b-', label='Prawdziwa odległość', linewidth=2)
        ax1.plot(times, measured_distances, 'r--', label='Zmierzona odległość', linewidth=2)
        ax1.set_xlabel('Czas (s)')
        ax1.set_ylabel('Odległość (m)')
        ax1.set_title('Porównanie odległości rzeczywistej i zmierzonej')
        ax1.legend()
        ax1.grid(True)
        
        # Error plot
        ax2.plot(times, errors, 'g-', linewidth=2)
        ax2.set_xlabel('Czas (s)')
        ax2.set_ylabel('Błąd bezwzględny (m)')
        ax2.set_title('Błąd bezwzględny')
        ax2.grid(True)
        
        # Create simulator for signal plots
        simulator = DistanceSensorSimulator(
            time_unit=self.time_unit_spin.value(),
            signal_velocity=self.velocity_spin.value(),
            sampling_frequency=self.sampling_freq_spin.value(),
            buffer_length=self.buffer_length_spin.value(),
            probe_period=self.probe_period_spin.value(),
            report_period=self.report_period_spin.value()
        )
        
        # Signal example
        actual_dist = actual_distances[-1] if actual_distances else 100
        simulator.update_buffers(actual_dist)
        t_signal = np.arange(len(simulator.tx_buffer)) * simulator.dt * 1e6
        
        ax3.plot(t_signal, simulator.tx_buffer, 'b-', label='Sondujący', linewidth=1)
        ax3.plot(t_signal, simulator.rx_buffer, 'r-', label='Odczytany', linewidth=1)
        ax3.set_xlabel('Time (μs)')
        ax3.set_ylabel('Amplitude')
        ax3.set_title('Porównanie sygnałów sondującego i odczytanego')
        ax3.legend()
        ax3.grid(True)
        
        # Correlation function
        _, correlation, max_idx = simulator.simulate_measurement(actual_dist)
        center_idx = len(correlation) // 2
        corr_time = (np.arange(len(correlation)) - center_idx) * simulator.dt * 1e6
        
        ax4.plot(corr_time, correlation, 'purple', linewidth=1)
        ax4.axvline(max_idx * simulator.dt * 1e6, color='red', linestyle='--', 
                   label=f'Max at {max_idx * simulator.dt * 1e6:.2f} μs')
        ax4.set_xlabel('Czas opóźnienia (μs)')
        ax4.set_ylabel('Korelacja')
        ax4.set_title('Funkcja korelacyjna')
        ax4.legend()
        ax4.grid(True)
        
        self.canvas.fig.tight_layout()
        self.canvas.draw()

def main():
    app = QApplication(sys.argv)
    window = DistanceSensorGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()