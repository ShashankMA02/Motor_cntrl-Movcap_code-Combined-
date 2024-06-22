# main_script.py

import subprocess
import signal
import time

# Define paths to your scripts
motor_control_script = "ODD_loop154.py" 
mocap_data_logger_script = "mocap_listen9_2_decimal_recording.py"

# Function to start subprocesses
def start_processes():
    global motor_control_process, mocap_data_logger_process

    motor_control_process = subprocess.Popen(motor_control_script, shell=True)
    mocap_data_logger_process = subprocess.Popen(mocap_data_logger_script, shell=True)

# Function to stop subprocesses
def stop_processes():
    motor_control_process.terminate()
    mocap_data_logger_process.terminate()

# Handle keyboard interrupt
def signal_handler(sig, frame):
    print("\nKeyboardInterrupt received. Stopping processes...")
    stop_processes()
    time.sleep(1)  # Wait for processes to terminate gracefully
    print("Processes stopped.")
    exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    print("Starting motor control and mocap data logger processes...")
    start_processes()

    try:
        while True:
            time.sleep(1)  # Keep the main script running until interrupted
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)
