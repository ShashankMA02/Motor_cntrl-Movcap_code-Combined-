import time
import csv
from dynamixel_sdk import *

# Control table addresses
ADDR_MX_TORQUE_ENABLE = 24
ADDR_MX_GOAL_POSITION = 30
ADDR_MX_PRESENT_POSITION = 36
ADDR_MX_TORQUE_MAX = 14

# Protocol version
PROTOCOL_VERSION = 1.0

# Default settings
DXL_MAIN_ID = 5
DXL_IDS = [1, 2, 3, 4, 5, 6]
BAUDRATE = 1000000
DEVICENAME = '/dev/ttyUSB0'
TORQUE_ENABLE = 1
TORQUE_DISABLE = 0
DXL_MINIMUM_POSITION_VALUE = 2048
DXL_EVEN_MAX_POSITION_VALUE = 2387
DXL_ODD_MAX_POSITION_VALUE = 1710
DXL_MOVING_STATUS_THRESHOLD = 20
STEP_SIZE_MAIN = -10
STEP_SIZE = 10
TORQUE_MAX_LEVEL = 300

# Initialize PortHandler and PacketHandler
portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)

# Function to open the serial port
def open_port():
    if portHandler.openPort():
        print("Succeeded to open the port")
    else:
        print("Failed to open the port")
        quit()

# Function to set baudrate
def set_baudrate():
    if portHandler.setBaudRate(BAUDRATE):
        print("Succeeded to change the baudrate")
    else:
        print("Failed to change the baudrate")
        quit()

# Function to enable torque for a motor
def enable_torque(dxl_id):
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_MX_TORQUE_ENABLE, TORQUE_ENABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to enable torque for Dynamixel ID {dxl_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")
        quit()
    elif dxl_error != 0:
        print(f"Error encountered while enabling torque for Dynamixel ID {dxl_id}: {packetHandler.getRxPacketError(dxl_error)}")
        quit()
    else:
        print(f"Dynamixel ID {dxl_id} has been successfully connected")

# Function to set torque level for a motor
def set_torque_level(dxl_id, torque_level):
    dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, dxl_id, ADDR_MX_TORQUE_MAX, torque_level)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to set torque level for Dynamixel ID {dxl_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")
        quit()
    elif dxl_error != 0:
        print(f"Error encountered while setting torque level for Dynamixel ID {dxl_id}: {packetHandler.getRxPacketError(dxl_error)}")
        quit()
    else:
        print(f"Torque level set to {torque_level} for Dynamixel ID {dxl_id}")

# Function to set goal position for a motor
def set_goal_position(dxl_id, goal_position):
    dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, dxl_id, ADDR_MX_GOAL_POSITION, goal_position)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to set goal position for Dynamixel ID {dxl_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")
    elif dxl_error != 0:
        print(f"Error encountered while setting goal position for Dynamixel ID {dxl_id}: {packetHandler.getRxPacketError(dxl_error)}")

# Function to read present position of a motor
def read_present_position(dxl_id):
    dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read2ByteTxRx(portHandler, dxl_id, ADDR_MX_PRESENT_POSITION)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to read present position for Dynamixel ID {dxl_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")
    elif dxl_error != 0:
        print(f"Error encountered while reading present position for Dynamixel ID {dxl_id}: {packetHandler.getRxPacketError(dxl_error)}")
    return dxl_present_position

# Function to close the serial port
def close_port():
    portHandler.closePort()

# Function to move a motor to a new position and log its position at each step
def move_motor(dxl_id, start_position, end_position, step_size, log_motor_positions, filename):
    goal_position = start_position

    while (goal_position >= end_position if step_size < 0 else goal_position <= end_position):
        set_goal_position(dxl_id, goal_position)

        while True:
            present_position = read_present_position(dxl_id)
            print(f"[ID:{dxl_id:03d}] GoalPos:{goal_position:03d}  PresPos:{present_position:03d}")

            if abs(goal_position - present_position) <= DXL_MOVING_STATUS_THRESHOLD:
                break

            time.sleep(0.1)

        motor_positions = [read_present_position(id) for id in DXL_IDS]
        log_motor_positions(filename, motor_positions)
        goal_position += step_size

    # Reset to home position
    set_goal_position(dxl_id, start_position)
    while True:
        present_position = read_present_position(dxl_id)
        print(f"[ID:{dxl_id:03d}] ResetPos:{start_position:03d}  PresPos:{present_position:03d}")

        if abs(start_position - present_position) <= DXL_MOVING_STATUS_THRESHOLD:
            break

        time.sleep(0.1)

# Function to initialize CSV file
def init_csv_file(filename):
    try:
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Motor1_Position', 'Motor2_Position', 'Motor3_Position', 'Motor4_Position', 'Motor5_Position', 'Motor6_Position'])
    except IOError as e:
        print(f"Error initializing CSV file {filename}: {e}")
        quit()

# Function to log motor positions
def log_motor_positions(filename, motor_positions):
    try:
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(motor_positions)
    except IOError as e:
        print(f"Error logging positions to CSV file {filename}: {e}")

# Main function
def main():
    open_port()
    set_baudrate()

    # Initialize CSV file
    csv_filename = '1_main5_motpos.csv'
    init_csv_file(csv_filename)

    while True:
        # Decrement the main motor (motor 1) in steps of -50
        for goal_position_main in range(DXL_MINIMUM_POSITION_VALUE, DXL_ODD_MAX_POSITION_VALUE - 1, STEP_SIZE_MAIN):
            set_goal_position(DXL_MAIN_ID, goal_position_main)

            while True:
                present_position_main = read_present_position(DXL_MAIN_ID)
                print(f"[ID:{DXL_MAIN_ID:03d}] GoalPos:{goal_position_main:03d}  PresPos:{present_position_main:03d}")

                if abs(goal_position_main - present_position_main) <= DXL_MOVING_STATUS_THRESHOLD:
                    break

                time.sleep(0.1)

            # Move all other motors and log positions
            motor_positions = [read_present_position(DXL_MAIN_ID)]  # Start with the main motor position

            for dxl_id in [2, 4, 6]:
                move_motor(dxl_id, DXL_MINIMUM_POSITION_VALUE, DXL_EVEN_MAX_POSITION_VALUE, STEP_SIZE, log_motor_positions, csv_filename)
                motor_positions.append(read_present_position(dxl_id))

            for dxl_id in [1, 3]:
                move_motor(dxl_id, DXL_MINIMUM_POSITION_VALUE, DXL_ODD_MAX_POSITION_VALUE, -STEP_SIZE, log_motor_positions, csv_filename)
                motor_positions.append(read_present_position(dxl_id))

            # Log positions to CSV after each step of the main motor
            motor_positions = [read_present_position(dxl_id) for dxl_id in DXL_IDS]
            print(f"Logging all motor positions: {motor_positions}")
            log_motor_positions(csv_filename, motor_positions)
            print("Logged all motor positions.")

if __name__ == "__main__":
    main()
