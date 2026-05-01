configuration_locations = [
    "~/.config/rottnest"
]

# File names within config locations
architectures_file_name = 'architectures'
executables_file_name = 'executables'

N_PROCESSES = 3 
SEGFAULT_SENTINEL_TIMEOUT_SECS = 20
REPORT_INTERVAL = 20
RESULT_INTERVAL = 50

# Bounds number of OMP threads spawned by numpy
OMP_NUM_THREADS = 1
MPLBACKEND = "Agg"
