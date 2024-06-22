import subprocess

def main():
    print("Starting motor control and mocap data logger processes...")

    # Specify absolute paths to your scripts
    script1_path = "/home/focas-main/catkin_hexa_ws/Motor_cntrl+Movcap_code/ODD_loop154.py"
    script2_path = "/home/focas-main/catkin_hexa_ws/Motor_cntrl+Movcap_code/mocap_listen9_2_decimal_recording.py"

    try:
        # Start subprocess for script1
        proc1 = subprocess.Popen(['/bin/python', script1_path])

        # Start subprocess for script2
        proc2 = subprocess.Popen(['/bin/python', script2_path])

        # Wait for keyboard interrupt (Ctrl+C)
        proc1.wait()
        proc2.wait()

    except KeyboardInterrupt:
        print("\nKeyboardInterrupt received. Stopping processes...")

        # Terminate subprocesses if interrupted
        proc1.terminate()
        proc2.terminate()

        # Wait for subprocesses to terminate
        proc1.wait()
        proc2.wait()

    print("Processes stopped.")

if __name__ == "__main__":
    main()
