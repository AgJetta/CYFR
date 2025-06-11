# Signal Types

DIGITAL_SIGNAL_PROCESSING = 'Cyfrowe przetwarzanie sygnałów'

UNIFORM_NOISE = 'Szum jednostajny'
GAUSSIAN_NOISE = 'Szum gaussowski'
SINUSOIDAL_SIGNAL = 'Sygnał sinusoidalny'
HALF_WAVE_RECTIFIED = 'Sygnał wyprostowany jednopołówkowo'
FULL_WAVE_RECTIFIED = 'Sygnał wyprostowany dwupołówkowo'
SQUARE_WAVE = 'Sygnał prostokątny'
SYMMETRICAL_SQUARE_WAVE = 'Sygnał prostokątny symetryczny'
TRIANGULAR_WAVE = 'Sygnał trójkątny'
UNIT_STEP_FUNCTION = 'Skok jednostkowy'
UNIT_IMPULSE = 'Impuls jednostkowy'
UNIT_NOISE = 'Szum jednostkowy'

SIGNAL_TYPES = [
    UNIFORM_NOISE,
    GAUSSIAN_NOISE,
    SINUSOIDAL_SIGNAL,
    HALF_WAVE_RECTIFIED,
    FULL_WAVE_RECTIFIED,
    SQUARE_WAVE,
    SYMMETRICAL_SQUARE_WAVE,
    TRIANGULAR_WAVE,
    UNIT_STEP_FUNCTION,
    UNIT_IMPULSE,
    UNIT_NOISE
] 

LOADED_SIGNAL = 'Wczytany sygnał'

# Parameter Labels
AMPLITUDE = 'Amplituda'
START_TIME = 'Czas początkowy'
DURATION = 'Czas trwania'
PERIOD = 'Częstotliwość sygnału'
DUTY_CYCLE = 'Współczynnik wypełnienia'
STEP_TIME = 'Czas skoku'
FIRST_SAMPLE_INDEX = 'Pierwszego próbki'
PEAK_SAMPLE_INDEX = 'Próbka ze skokiem ampl.'
NUMBER_OF_SAMPLES = 'Liczba próbek'
SAMPLE_RATE = 'Częstotliwość próbkowania'
PROBABILITY = 'Prawdopodobieństwo'
HISTOGRAM_BINS = 'Przedziały histogramu'

# Signal Parameters
MEAN_VALUE = 'Wartość średnia'
ABSOLUTE_MEAN_VALUE = 'Wartość średnia bezwzględna'
RMS_VALUE = 'Wartość skuteczna'
VARIANCE = 'Wariancja'
AVERAGE_POWER = 'Moc średnia sygnału'

# Button Labels
SAVE_SIGNAL = 'Zapisz sygnał'
LOAD_SIGNAL = 'Wczytaj sygnał'
SIGNAL_OPERATIONS = 'Operacje na sygnałach'
TEXT_REPRESENTATION = 'Reprezentacja tekstowa'
GENERATE_SIGNAL = 'Generuj sygnał'

# Plot Labels
SIGNAL_TYPE = 'Typ sygnału'
AMPLITUDE_AXIS = 'A'
TIME_AXIS = 't[s]'
SAMPLE_AXIS = 'N'
FREQUENCY_AXIS = 'f'
SIGNAL_HISTOGRAM = 'Histogram sygnału'
SIGNAL_PARAMETERS = 'Parametry sygnału:'

# Histogram Options
CONTINUOUS = 'Ciągły'
BINS_20 = '20 przedziałów'
BINS_15 = '15 przedziałów'
BINS_10 = '10 przedziałów'
BINS_5 = '5 przedziałów'

# Messages
NO_SIGNAL = 'Brak sygnału.'
NO_SIGNAL_TO_SAVE = 'Brak sygnału do zapisania.'
SIGNAL_SAVED = 'Sygnał zapisany pomyślnie.'
SIGNAL_LOADED = 'Sygnał wczytany pomyślnie.'
ERROR_LOADING = 'Błąd wczytywania sygnału: {}'
ERROR_SAVING = 'Błąd zapisywania sygnału: {}'
ERROR_SAVING_TEXT = 'Błąd zapisywania reprezentacji tekstowej: {}'
TEXT_REPRESENTATION_SAVED = 'Reprezentacja tekstowa zapisana pomyślnie.'

# Signal Operation Dialog
SIGNAL_OPERATION_DIALOG_TITLE = 'Operacje na sygnałach'
SIGNAL_1_LABEL = 'Sygnał 1:'
SIGNAL_2_LABEL = 'Sygnał 2:'
LOAD_SIGNAL_1 = 'Wczytaj sygnał 1'
LOAD_SIGNAL_2 = 'Wczytaj sygnał 2'
METADATA_LABEL = 'Metadane:'
OPERATION_ADD = 'Dodawanie'
OPERATION_SUBTRACT = 'Odejmowanie'
OPERATION_MULTIPLY = 'Mnożenie'
OPERATION_DIVIDE = 'Dzielenie'
PERFORM_OPERATION = 'Wykonaj operację'
SAVE_RESULT = 'Zapisz wynik'
ERROR_LOAD_BOTH = 'Proszę wczytać oba sygnały.'
ERROR_SELECT_OPERATION = 'Proszę wybrać operację.'
ERROR_OPERATION_FAILED = 'Operacja nie powiodła się: {}'


# Signal Conversion Dialog
PERFORM_CONVERSION = 'Wykonaj konwersje'

QUANTIZATION = 'Kwantyzacja'
CONVERSION = 'Konwersja'
SAMPLING = 'Probkowanie'
EXTRAPOLATION = 'Ekstrapolacja'
INTERPOLATION = 'Interpolacja'
RECONSTRUCTION = 'Rekonstrukcja'
SAMPLE_FREQ = 'Częstotliwość próbkowania'
QUANTIZATION_LVL = 'Poziom Kwantyzacji'

SIGNAL_COMPARISON_DIALOG_TITLE = 'Porównanie sygnałów'
SIGNAL_COMPARISON = 'Porównanie sygnałów'
PERFORM_COMPARISON = 'Wykonaj porównanie'
ERROR_N_SAMPLES = 'Liczba próbek sygnałów musi być taka sama.'
COMPARISON_TITLE = 'Porównanie sygnałów'

#SINGAL CONVOLUTION
CONVOLUTION = 'Splot'
SIGNAL_CONVOLUTION_DIALOG_TITLE = 'Splot sygnałów'
PERFORM_CONVOLUTION = 'Wykonaj splot'
FILTER = 'Filtr'


#FILTER
LOW_PASS_FILTER = 'Filtr dolnoprzepustowy'
HIGH_PASS_FILTER ='Filtr górnoprzepustowy'
HANNING_WINDOW = 'Okno Hanninga'
CUT_OFF_FREQUENCY = 'Częstotliwość odcięcia'
NUM_OF_TAPS = 'Liczba współczynników'
PERFORM_FILTER = 'Przefiltruj'

SIGNAL_CORRELATION_DIALOG_TITLE = 'Analiza korelacyjna'
CORRELATION = 'Korelacja'
CORRELATION_ANALYSIS = 'Wykonaj analizę korelacyjna'


TRANSFORMATION = 'Transformacja'
SIGNAL_TRANSFORMATION = 'Transformacja sygnału'
FOURIER_TRANSFORMATION = 'Transformacja Fouriera'
WAVE_TRANSFORMATION = 'Transformacja Falkowa'
WAVE_TRANSFORMATION_PARAMS = 'Transformacja falkowa (jeden poziom)'
PERFORM_TRANSFORMATION = 'Wykonaj Transformację'
CHOOSE_TRANSFORMATION_METHOD = 'Wybierz metode transformacji'

LOAD_COMPLEX_SIGNAL = 'Wczytaj zespolony sygnał'
W1 = 'Wykres: część rzeczywista + część urojona'
W2 = 'Wykres: moduł liczby zespoklonej + argument w funkcji częstotliwości'
CHOOSE_DIAGRAM_TYPE = 'Wybierz rodzaj wykresu'
SHOW_COMPLEX_SIGNAL = 'Wyświetl zespolony sygnał'