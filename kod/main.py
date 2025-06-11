import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QComboBox, QDoubleSpinBox, 
                             QPushButton, QGridLayout, QTextEdit, QStackedWidget, 
                             QSpinBox, QFileDialog, QMessageBox)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from GUI_signal_conversion_dialog import SignalConversionDialog
from GUI_signal_correlation_dialog import SignalCorrelationDialog
from GUI_singal_convolution_diaog import SignalConvolutionDialog
from logic_signal_generator import SignalGenerator
from logic_signal_file_handler import SignalFileHandler
from GUI_signal_operation_dialog import SignalOperationDialog
from GUI_signal_comparison_dialog import SignalComparisonDialog
from GUI_signal_filter_dialog import SignalFilterDialog
from GUI_signal_transformation_dialog import SignalTransformationDialog
from strings import *

class DSPApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(DIGITAL_SIGNAL_PROCESSING)
        self.setGeometry(100, 100, 1400, 800)

        main_widget = QWidget()
        main_layout = QHBoxLayout()
        
        left_panel = self.create_left_panel()
        middle_panel = self.create_middle_panel()
        right_panel = self.create_right_panel()
        
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(middle_panel, 3)
        main_layout.addWidget(right_panel, 1)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        self.signal_type_combo.setCurrentIndex(0)
        self.update_parameter_inputs()
        self.generate_signal()
        
        self.current_signal_data = None
        self.current_signal_metadata = None

    def create_left_panel(self):
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        self.add_operation_buttons(left_layout)
        self.add_signal_type_selection(left_layout)
        self.add_parameter_widgets(left_layout)
        self.add_generate_button(left_layout)
        
        left_panel.setLayout(left_layout)
        return left_panel

    def create_middle_panel(self):
        middle_panel = QWidget()
        middle_layout = QVBoxLayout()
        
        self.signal_figure, (self.signal_ax, self.histogram_ax) = plt.subplots(2, 1, figsize=(10, 8))
        self.signal_canvas = FigureCanvas(self.signal_figure)
        middle_layout.addWidget(self.signal_canvas)
        
        middle_panel.setLayout(middle_layout)
        return middle_panel

    def create_right_panel(self):
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        self.parameters_text = QTextEdit()
        self.parameters_text.setReadOnly(True)
        right_layout.addWidget(QLabel(SIGNAL_PARAMETERS))
        right_layout.addWidget(self.parameters_text)
        
        right_panel.setLayout(right_layout)
        return right_panel

    def add_operation_buttons(self, layout):
        save_btn = QPushButton(SAVE_SIGNAL)
        save_btn.clicked.connect(self.save_current_signal)
        
        load_btn = QPushButton(LOAD_SIGNAL)
        load_btn.clicked.connect(self.load_signal)
        
        operations_btn = QPushButton(SIGNAL_OPERATIONS)
        operations_btn.clicked.connect(self.show_signal_operations)
        
        text_repr_btn = QPushButton(TEXT_REPRESENTATION)
        text_repr_btn.clicked.connect(self.show_text_representation)

        conversion_btn = QPushButton(CONVERSION)
        conversion_btn.clicked.connect(self.show_signal_conversions)

        comparison_btn = QPushButton(SIGNAL_COMPARISON)
        comparison_btn.clicked.connect(self.show_signal_comparison)

        convolution_btn = QPushButton(CONVOLUTION)
        convolution_btn.clicked.connect(self.show_signal_convolution)

        filter_btn = QPushButton(FILTER)
        filter_btn.clicked.connect(self.show_signal_filter)

        correlation_btn = QPushButton(CORRELATION)
        correlation_btn.clicked.connect(self.show_signal_correlation)

        transformation_btn = QPushButton(TRANSFORMATION)
        transformation_btn.clicked.connect(self.show_signal_transformation)


        layout.addWidget(save_btn)
        layout.addWidget(load_btn)
        layout.addWidget(operations_btn)
        layout.addWidget(text_repr_btn)
        layout.addWidget(conversion_btn)
        layout.addWidget(comparison_btn)
        layout.addWidget(convolution_btn)
        layout.addWidget(filter_btn)
        layout.addWidget(correlation_btn)
        layout.addWidget(transformation_btn)


    def add_comparison_button(self, layout):
        comparison_btn = QPushButton(SIGNAL_COMPARISON)
        comparison_btn.clicked.connect(self.show_signal_comparison)
        layout.addWidget(comparison_btn)


    def add_signal_type_selection(self, layout):
        signal_type_label = QLabel(SIGNAL_TYPE + ':')
        self.signal_type_combo = QComboBox()
        self.signal_type_combo.addItems(SIGNAL_TYPES)
        self.signal_type_combo.currentIndexChanged.connect(self.update_parameter_inputs)
        layout.addWidget(signal_type_label)
        layout.addWidget(self.signal_type_combo)

    def add_parameter_widgets(self, layout):
        parameters_widget = QWidget()
        parameters_layout = QVBoxLayout()
        
        self.create_common_parameters(parameters_layout)
        self.create_periodic_parameters(parameters_layout)
        self.create_duty_cycle_parameters(parameters_layout)
        self.create_unit_step_parameters(parameters_layout)
        self.create_unit_impulse_parameters(parameters_layout)
        self.create_unit_noise_parameters(parameters_layout)
        self.create_histogram_parameters(parameters_layout)
        
        parameters_widget.setLayout(parameters_layout)
        layout.addWidget(parameters_widget)

    def create_common_parameters(self, layout):
        common_params_widget = QWidget()
        common_params_layout = QGridLayout()
        
        common_parameters = [
            (AMPLITUDE, 1.0, 0.0, 100.0),
            (START_TIME, 0.0, -100.0, 100.0),
            (DURATION, 5.0, 0.01, 100.0),
            (SAMPLE_RATE, 1000, 2, 100000)
        ]
        
        self.common_parameter_inputs = {}
        for i, (name, default, min_val, max_val) in enumerate(common_parameters):
            label = QLabel(name)
            if name == SAMPLE_RATE:
                spinbox = QDoubleSpinBox()
                spinbox.setDecimals(0)
                spinbox.setSingleStep(1)
            else:
                spinbox = QDoubleSpinBox()
                spinbox.setDecimals(6)
                spinbox.setSingleStep(0.001)
            spinbox.setRange(min_val, max_val)
            spinbox.setValue(default)
            spinbox.setButtonSymbols(QDoubleSpinBox.NoButtons)
            common_params_layout.addWidget(label, i, 0)
            common_params_layout.addWidget(spinbox, i, 1)
            self.common_parameter_inputs[name] = spinbox
        
        common_params_widget.setLayout(common_params_layout)
        layout.addWidget(common_params_widget)

    def create_periodic_parameters(self, layout):
        periodic_params_widget = QWidget()
        periodic_params_layout = QGridLayout()
        
        periodic_parameters = [(PERIOD, 1.0, -100000, 100000.0)]
        
        self.periodic_parameter_inputs = {}
        for i, (name, default, min_val, max_val) in enumerate(periodic_parameters):
            label = QLabel(name)
            spinbox = QDoubleSpinBox()
            spinbox.setRange(min_val, max_val)
            spinbox.setValue(default)
            spinbox.setDecimals(7)
            spinbox.setSingleStep(0.001)
            periodic_params_layout.addWidget(label, i, 0)
            periodic_params_layout.addWidget(spinbox, i, 1)
            self.periodic_parameter_inputs[name] = spinbox
        
        periodic_params_widget.setLayout(periodic_params_layout)
        
        periodic_params_container = QWidget()
        periodic_params_container_layout = QVBoxLayout()
        periodic_params_container_layout.addWidget(periodic_params_widget)
        periodic_params_container.setLayout(periodic_params_container_layout)
        layout.addWidget(periodic_params_container)
        periodic_params_container.setVisible(False)
        self.periodic_params_container = periodic_params_container

    def create_duty_cycle_parameters(self, layout):
        duty_cycle_params_widget = QWidget()
        duty_cycle_params_layout = QGridLayout()
        
        duty_cycle_parameters = [(DUTY_CYCLE, 0.5, 0.0, 1.0)]
        
        self.duty_cycle_parameter_inputs = {}
        for i, (name, default, min_val, max_val) in enumerate(duty_cycle_parameters):
            label = QLabel(name)
            spinbox = QDoubleSpinBox()
            spinbox.setRange(min_val, max_val)
            spinbox.setValue(default)
            duty_cycle_params_layout.addWidget(label, i, 0)
            duty_cycle_params_layout.addWidget(spinbox, i, 1)
            self.duty_cycle_parameter_inputs[name] = spinbox
        
        duty_cycle_params_widget.setLayout(duty_cycle_params_layout)
        
        duty_cycle_params_container = QWidget()
        duty_cycle_params_container_layout = QVBoxLayout()
        duty_cycle_params_container_layout.addWidget(duty_cycle_params_widget)
        duty_cycle_params_container.setLayout(duty_cycle_params_container_layout)
        layout.addWidget(duty_cycle_params_container)
        duty_cycle_params_container.setVisible(False)
        self.duty_cycle_params_container = duty_cycle_params_container

    def create_unit_step_parameters(self, layout):
        unit_step_params_widget = QWidget()
        unit_step_params_layout = QGridLayout()
        
        unit_step_parameters = [(STEP_TIME, 2.5, 0.0, 10.0)]
        
        self.unit_step_parameter_inputs = {}
        for i, (name, default, min_val, max_val) in enumerate(unit_step_parameters):
            label = QLabel(name)
            spinbox = QDoubleSpinBox()
            spinbox.setRange(min_val, max_val)
            spinbox.setValue(default)
            unit_step_params_layout.addWidget(label, i, 0)
            unit_step_params_layout.addWidget(spinbox, i, 1)
            self.unit_step_parameter_inputs[name] = spinbox
        
        unit_step_params_widget.setLayout(unit_step_params_layout)
        
        unit_step_params_container = QWidget()
        unit_step_params_container_layout = QVBoxLayout()
        unit_step_params_container_layout.addWidget(unit_step_params_widget)
        unit_step_params_container.setLayout(unit_step_params_container_layout)
        layout.addWidget(unit_step_params_container)
        unit_step_params_container.setVisible(False)
        self.unit_step_params_container = unit_step_params_container

    def create_unit_impulse_parameters(self, layout):
        unit_impulse_params_widget = QWidget()
        unit_impulse_params_layout = QGridLayout()
        
        unit_impulse_parameters = [
            (FIRST_SAMPLE_INDEX, 25, 0, 10000),
            (PEAK_SAMPLE_INDEX, 50, 0, 10000),
            (NUMBER_OF_SAMPLES, 100, 1, 10000)
        ]
        
        self.unit_impulse_parameter_inputs = {}
        for i, (name, default, min_val, max_val) in enumerate(unit_impulse_parameters):
            label = QLabel(name)
            if name in [FIRST_SAMPLE_INDEX, PEAK_SAMPLE_INDEX, NUMBER_OF_SAMPLES]:
                spinbox = QSpinBox()
            else:
                spinbox = QDoubleSpinBox()
            spinbox.setRange(min_val, max_val)
            spinbox.setValue(default)
            unit_impulse_params_layout.addWidget(label, i, 0)
            unit_impulse_params_layout.addWidget(spinbox, i, 1)
            self.unit_impulse_parameter_inputs[name] = spinbox
        
        unit_impulse_params_widget.setLayout(unit_impulse_params_layout)
        
        unit_impulse_params_container = QWidget()
        unit_impulse_params_container_layout = QVBoxLayout()
        unit_impulse_params_container_layout.addWidget(unit_impulse_params_widget)
        unit_impulse_params_container.setLayout(unit_impulse_params_container_layout)
        layout.addWidget(unit_impulse_params_container)
        unit_impulse_params_container.setVisible(False)
        self.unit_impulse_params_container = unit_impulse_params_container

    def show_signal_transformation(self):
        dialog = SignalTransformationDialog(self)
        dialog.exec_()
    def create_unit_noise_parameters(self, layout):
        unit_noise_params_widget = QWidget()
        unit_noise_params_layout = QGridLayout()
        
        unit_noise_parameters = [
            (PROBABILITY, 0.5, 0.0, 1.0)
        ]
        
        self.unit_noise_parameter_inputs = {}
        for i, (name, default, min_val, max_val) in enumerate(unit_noise_parameters):
            label = QLabel(name)
            spinbox = QDoubleSpinBox()
            spinbox.setRange(min_val, max_val)
            spinbox.setValue(default)
            unit_noise_params_layout.addWidget(label, i, 0)
            unit_noise_params_layout.addWidget(spinbox, i, 1)
            self.unit_noise_parameter_inputs[name] = spinbox
        
        unit_noise_params_widget.setLayout(unit_noise_params_layout)
        
        unit_noise_params_container = QWidget()
        unit_noise_params_container_layout = QVBoxLayout()
        unit_noise_params_container_layout.addWidget(unit_noise_params_widget)
        unit_noise_params_container.setLayout(unit_noise_params_container_layout)
        layout.addWidget(unit_noise_params_container)
        unit_noise_params_container.setVisible(False)
        self.unit_noise_params_container = unit_noise_params_container

    def create_histogram_parameters(self, layout):
        histogram_params_widget = QWidget()
        histogram_params_layout = QGridLayout()
        
        histogram_label = QLabel(HISTOGRAM_BINS + ':')
        self.histogram_combo = QComboBox()
        self.histogram_combo.addItems([
            CONTINUOUS,
            BINS_20,
            BINS_15,
            BINS_10,
            BINS_5,
        ])
        
        histogram_params_layout.addWidget(histogram_label, 0, 0)
        histogram_params_layout.addWidget(self.histogram_combo, 0, 1)
        
        histogram_params_widget.setLayout(histogram_params_layout)
        layout.addWidget(histogram_params_widget)

    def add_generate_button(self, layout):
        generate_button = QPushButton(GENERATE_SIGNAL)
        generate_button.clicked.connect(self.generate_signal)
        layout.addWidget(generate_button)

    def update_parameter_inputs(self):
        """Set parameter visibility in GUI based on signal type"""
        signal_type = self.signal_type_combo.currentText()
        
        self.periodic_params_container.setVisible(False)
        self.duty_cycle_params_container.setVisible(False)
        self.unit_step_params_container.setVisible(False)
        self.unit_impulse_params_container.setVisible(False)
        self.unit_noise_params_container.setVisible(False)
        
        if signal_type == UNIT_IMPULSE:
            self.common_parameter_inputs[START_TIME].setVisible(False)
            self.common_parameter_inputs[DURATION].setVisible(False)
            self.common_parameter_inputs[SAMPLE_RATE].setVisible(True)
            self.unit_impulse_params_container.setVisible(True)
        else:
            self.common_parameter_inputs[START_TIME].setVisible(True)
            self.common_parameter_inputs[DURATION].setVisible(True)
            self.common_parameter_inputs[SAMPLE_RATE].setVisible(True)
        
        if signal_type in [SINUSOIDAL_SIGNAL, HALF_WAVE_RECTIFIED, 
                         FULL_WAVE_RECTIFIED, SQUARE_WAVE, 
                         SYMMETRICAL_SQUARE_WAVE, TRIANGULAR_WAVE]:
            self.periodic_params_container.setVisible(True)
            
            if signal_type in [SQUARE_WAVE, SYMMETRICAL_SQUARE_WAVE, TRIANGULAR_WAVE]:
                self.duty_cycle_params_container.setVisible(True)
        
        elif signal_type == UNIT_STEP_FUNCTION:
            self.unit_step_params_container.setVisible(True)

        elif signal_type == UNIT_NOISE:
            self.unit_noise_params_container.setVisible(True)

    def clear_all_plot_parameters(self):
        self.signal_ax.clear()
        self.histogram_ax.clear()
        self.signal_ax.relim()
        self.histogram_ax.relim()
        self.signal_ax.autoscale()
        self.histogram_ax.autoscale()

    def generate_signal(self):
        self.clear_all_plot_parameters()
        
        signal_type = self.signal_type_combo.currentText()
        amplitude = self.common_parameter_inputs[AMPLITUDE].value()
        start_time = self.common_parameter_inputs[START_TIME].value()
        duration = self.common_parameter_inputs[DURATION].value()

        
        t, signal = self.generate_signal_by_type(signal_type, amplitude, start_time, duration)
        self.current_signal_data = signal
        
        self.plot_signal_and_histogram(t, signal, signal_type, TIME_AXIS)
        
        params = SignalGenerator.calculate_signal_parameters(signal)
        param_text = '\n'.join([f'{k}: {v:.4f}' for k, v in params.items()])
        self.parameters_text.setText(param_text)
        
        self.signal_figure.tight_layout()
        self.signal_canvas.draw()

    def plot_signal_and_histogram(self, t, signal, signal_type, x_axis_label=TIME_AXIS):
        self.clear_all_plot_parameters()

        self.signal_ax.set_facecolor('#f0f0f0')
        self.signal_ax.grid(True, color='white', linestyle='-', alpha=0.3)
        
        self.signal_ax.axhline(y=0, color='purple', linestyle='--', alpha=0.3)
        self.signal_ax.axvline(x=0, color='purple', linestyle='--', alpha=0.3)
        
        if signal_type == UNIT_IMPULSE or signal_type == UNIT_NOISE:
            self.signal_ax.plot(t, signal, 'ro', markersize=3)
        else:
            self.signal_ax.plot(t, signal, color='red', linewidth=0.8)
        self.signal_ax.set_title(f'{signal_type}')
        self.signal_ax.set_xlabel(x_axis_label)
        self.signal_ax.set_ylabel(AMPLITUDE_AXIS)
        
        self.histogram_ax.set_facecolor('#f0f0f0')
        
        histogram_option = self.histogram_combo.currentText()
        if histogram_option == BINS_5:
            bins = 5
        elif histogram_option == BINS_10:
            bins = 10
        elif histogram_option == BINS_15:
            bins = 15
        elif histogram_option == BINS_20:
            bins = 20
        else:  # Continuous
            bins = 'auto'
            
        self.histogram_ax.hist(signal, bins=bins, edgecolor='black')
        self.histogram_ax.set_title(SIGNAL_HISTOGRAM)
        self.histogram_ax.set_xlabel(AMPLITUDE_AXIS)
        self.histogram_ax.set_ylabel(FREQUENCY_AXIS)

    def generate_signal_from_file(self, filename):
        try:
            # Load signal and metadata
            metadata, signal_data = SignalFileHandler.load_signal(filename)

            self.current_signal_data = signal_data
            self.current_signal_metadata = metadata

            # Update the GUI with loaded signal metadata
            if SAMPLE_RATE in self.common_parameter_inputs:
                self.common_parameter_inputs[SAMPLE_RATE].setValue(metadata['sampling_freq'])
            if START_TIME in self.common_parameter_inputs:
                self.common_parameter_inputs[START_TIME].setValue(metadata['start_time'])
            if DURATION in self.common_parameter_inputs:
                self.common_parameter_inputs[DURATION].setValue(metadata['duration'])

            # Clear previous plot
            self.signal_ax.clear()
            self.histogram_ax.clear()

            # Use metadata 'duration' directly to calculate the time array
            time_array = np.linspace(
                metadata['start_time'],
                metadata['start_time'] + metadata['duration'],  # Use 'duration' from metadata
                len(signal_data)
            )
            print(metadata);
            # Plot the signal and histogram
            self.plot_signal_and_histogram(time_array, signal_data, filename, TIME_AXIS)

            # Calculate and display signal parameters
            params = SignalGenerator.calculate_signal_parameters(signal_data)
            param_text = '\n'.join([f'{k}: {v:.4f}' for k, v in params.items()])
            self.parameters_text.setText(param_text)

            # Adjust layout and redraw the canvas
            self.signal_figure.tight_layout()
            self.signal_canvas.draw()

        except Exception as e:
            QMessageBox.critical(self, "Error", ERROR_LOADING.format(str(e)))


    def show_signal_operations(self):
        dialog = SignalOperationDialog(self)
        dialog.exec_()


    def show_signal_conversions(self):
        dialog = SignalConversionDialog(self)
        dialog.exec_()

    def show_signal_comparison(self):
        dialog = SignalComparisonDialog(self)
        dialog.exec_()

    def show_signal_convolution(self):
        dialog = SignalConvolutionDialog(self)
        dialog.exec_()

    def show_signal_filter(self):
        dialog = SignalFilterDialog(self)
        dialog.exec_()

    def show_signal_correlation(self):
        dialog = SignalCorrelationDialog(self)
        dialog.exec_()


    def show_text_representation(self):
        if self.current_signal_data is None:
            QMessageBox.critical(self, "Error", NO_SIGNAL)
            return
        
        filename, _ = QFileDialog.getSaveFileName(self, "Save Text Representation", "", "Text Files (*.txt)")
        if filename:
            try:
                temp_filename = os.path.join(os.path.dirname(filename), 'temp_signal.bin')
                SignalFileHandler.save_signal(
                    temp_filename, 
                    self.current_signal_data,
                    start_time=self.common_parameter_inputs[START_TIME].value(),
                    sampling_freq=self.common_parameter_inputs[SAMPLE_RATE].value(),
                    duration=self.common_parameter_inputs[DURATION].value()
                )
                
                text_repr = SignalFileHandler.text_representation(temp_filename)
                os.remove(temp_filename)
                
                with open(filename, 'w') as f:
                    f.write(text_repr)
                
                QMessageBox.information(self, "Success", TEXT_REPRESENTATION_SAVED)
            except Exception as e:
                QMessageBox.critical(self, "Error", ERROR_SAVING_TEXT.format(str(e)))



    def generate_signal_by_type(self, signal_type, amplitude, start_time, duration, sampling_rate=None):
        sampling_rate = self.common_parameter_inputs[SAMPLE_RATE].value() if sampling_rate is None else sampling_rate
        
        if signal_type == UNIFORM_NOISE:
            return SignalGenerator.generate_uniform_noise(amplitude, start_time, duration, sampling_rate)
        elif signal_type == GAUSSIAN_NOISE:
            return SignalGenerator.generate_gaussian_noise(amplitude, start_time, duration, sampling_rate)
        elif signal_type == SINUSOIDAL_SIGNAL:
            period = self.periodic_parameter_inputs[PERIOD].value()
            return SignalGenerator.generate_sinusoidal(amplitude, period, start_time, duration, sampling_rate)
        elif signal_type == HALF_WAVE_RECTIFIED:
            period = self.periodic_parameter_inputs[PERIOD].value()
            return SignalGenerator.generate_half_wave_rectified(amplitude, period, start_time, duration, sampling_rate)
        elif signal_type == FULL_WAVE_RECTIFIED:
            period = self.periodic_parameter_inputs[PERIOD].value()
            return SignalGenerator.generate_full_wave_rectified(amplitude, period, start_time, duration, sampling_rate)
        elif signal_type == SQUARE_WAVE:
            period = self.periodic_parameter_inputs[PERIOD].value()
            duty_cycle = self.duty_cycle_parameter_inputs[DUTY_CYCLE].value()
            return SignalGenerator.generate_square_wave(amplitude, period, start_time, duration, duty_cycle, sampling_rate)
        elif signal_type == SYMMETRICAL_SQUARE_WAVE:
            period = self.periodic_parameter_inputs[PERIOD].value()
            duty_cycle = self.duty_cycle_parameter_inputs[DUTY_CYCLE].value()
            return SignalGenerator.generate_symmetric_square_wave(amplitude, period, start_time, duration, duty_cycle, sampling_rate)
        elif signal_type == TRIANGULAR_WAVE:
            period = self.periodic_parameter_inputs[PERIOD].value()
            duty_cycle = self.duty_cycle_parameter_inputs[DUTY_CYCLE].value()
            return SignalGenerator.generate_triangular_wave(amplitude, period, start_time, duration, duty_cycle, sampling_rate)
        elif signal_type == UNIT_STEP_FUNCTION:
            step_time = self.unit_step_parameter_inputs[STEP_TIME].value()
            return SignalGenerator.generate_unit_step(amplitude, start_time, duration, step_time, sampling_rate)
        elif signal_type == UNIT_IMPULSE:
            first_sample_index = self.unit_impulse_parameter_inputs[FIRST_SAMPLE_INDEX].value()
            peak_sample_index = self.unit_impulse_parameter_inputs[PEAK_SAMPLE_INDEX].value()
            number_of_samples = self.unit_impulse_parameter_inputs[NUMBER_OF_SAMPLES].value()
            return SignalGenerator.generate_unit_impulse(amplitude, first_sample_index, peak_sample_index, number_of_samples, sampling_rate)
        elif signal_type == UNIT_NOISE:
            probability = self.unit_noise_parameter_inputs[PROBABILITY].value()
            return SignalGenerator.generate_unit_noise(amplitude, start_time, duration, sampling_rate, probability)

    def save_current_signal(self):
        if self.current_signal_data is None:
            QMessageBox.critical(self, "Error", NO_SIGNAL_TO_SAVE)
            return
        
        filename, _ = QFileDialog.getSaveFileName(self, "Save Signal", "", "Binary Files (*.bin)")
        if filename:
            try:
                SignalFileHandler.save_signal(
                    filename, 
                    self.current_signal_data,
                    start_time=self.common_parameter_inputs[START_TIME].value(),
                    sampling_freq=self.common_parameter_inputs[SAMPLE_RATE].value(),
                    duration = self.common_parameter_inputs[DURATION].value()
                )
                QMessageBox.information(self, "Success", SIGNAL_SAVED)
            except Exception as e:
                QMessageBox.critical(self, "Error", ERROR_SAVING.format(str(e)))
    
    def load_signal(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Signal File", "", "Binary Files (*.bin)")
        if filename:
            self.generate_signal_from_file(filename)

def main():
    app = QApplication(sys.argv)
    main_window = DSPApplication()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    import numpy as np
    import matplotlib.pyplot as plt


    main()