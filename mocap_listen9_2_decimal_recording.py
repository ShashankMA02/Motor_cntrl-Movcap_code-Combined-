import rospy
import csv
import tf.transformations
from phasespace_msgs.msg import Rigids  # Replace with the actual message type

class MocapDataLogger:
    def __init__(self):
        rospy.init_node("mocap_data_logger")  # Initialize ROS node
        self.csv_filename = "1_main5_movcap1.csv"
        self.pose_data = None  # Store the most recent pose data
        self.pose_subscriber = rospy.Subscriber('/phasespace/rigids', Rigids, self.mocap_callback)
        self.record_count = 0  # Variable to count the number of records saved

        # Define the home position
        self.home_position = [2118, 256, 312, -3, -1, -70]
        self.initialized = False

        # Write the header to the CSV file
        with open(self.csv_filename, mode='w') as file:  # Use 'w' mode to create a new file or overwrite the existing one
            writer = csv.writer(file)
            writer.writerow(['x_mm', 'y_mm', 'z_mm', 'roll_deg', 'pitch_deg', 'yaw_deg'])
        print("CSV file initialized with header")

    def mocap_callback(self, msg):
        # Extract position and orientation data for the rigid body with id: 1
        for rigid_body in msg.rigids:
            if rigid_body.id == 1:
                # Convert position from meters to millimeters and round to 1 or 2 decimal places
                x_mm = round(rigid_body.x * 1000, 3)
                y_mm = round(rigid_body.y * 1000, 3)
                z_mm = round(rigid_body.z * 1000 - 845, 3)  # Subtract the platform height in mm and round

                # Convert quaternion to Euler angles in degrees and round to 1 or 2 decimal places
                euler = tf.transformations.euler_from_quaternion(
                    [rigid_body.qx, rigid_body.qy, rigid_body.qz, rigid_body.qw])
                roll_deg = round(euler[0] * 180.0 / 3.141592653589793, 3)
                pitch_deg = round(euler[1] * 180.0 / 3.141592653589793, 3)
                yaw_deg = round(euler[2] * 180.0 / 3.141592653589793, 3)

                if not self.initialized:
                    self.home_position = [x_mm, y_mm, z_mm, roll_deg, pitch_deg, yaw_deg]
                    self.initialized = True
                    print("Home position set to:", self.home_position)

                self.pose_data = [
                    round(x_mm - self.home_position[0], 2),
                    round(y_mm - self.home_position[1], 2),
                    round(z_mm - self.home_position[2], 2),
                    round(roll_deg - self.home_position[3], 2),
                    round(pitch_deg - self.home_position[4], 2),
                    round(yaw_deg - self.home_position[5], 2)
                ]
                print("Received pose data for rigid body 1:", self.pose_data)  # Debugging statement
                break  # Assuming we only care about the first occurrence of id: 1

    def save_to_csv(self):
        if self.pose_data:
            with open(self.csv_filename, mode='a') as file:
                writer = csv.writer(file)
                writer.writerow(self.pose_data)
            self.record_count += 1
            print("Data recorded at:", rospy.Time.now(), "Total records:", self.record_count)

    def run(self):
        rate = rospy.Rate(10)  # Set rate to 1 Hz
        while not rospy.is_shutdown():
            self.save_to_csv()
            rate.sleep()


if __name__ == "__main__":
    mocap_logger = MocapDataLogger()
    mocap_logger.run()
