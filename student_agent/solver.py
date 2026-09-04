"""
Write your own solver in the scan_callback function
"""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

# ==========================================
# These four parameters MUST add up to exactly 30!
# ==========================================
TOP_SPEED = 6
ACCELERATION = 6
TURN_SPEED = 8
SENSOR_RANGE = 10

class StudentSolver(Node):
    def __init__(self):
        super().__init__('student_solver')
        
        # subscriber to read sensor values (L,F,R)
        self.scan_sub = self.create_subscription(
            LaserScan,
            '/mouse/scan',
            self.scan_callback,
            10
        )
        
        # publisher to send movement commands
        self.cmd_pub = self.create_publisher(
            Twist,
            '/mouse/cmd_vel',
            10
        )
        
        self.get_logger().info("Student Solver Node initialized successfully.")
        self.get_logger().info(f"Stats -> Speed: {TOP_SPEED}, Accel: {ACCELERATION}, Turn: {TURN_SPEED}, Range: {SENSOR_RANGE}")

    def scan_callback(self, msg):
        d_left = msg.ranges[0]
        d_front = msg.ranges[1]
        d_right = msg.ranges[2]
        
        cmd = Twist()
        
        # 1. IMMEDIATE THREAT: Front wall approaching
        # If the wall is closer than 0.65, it will kill forward momentum instantly and spin right.
        if d_front < 0.65:
            cmd.linear.x = 0.0
            cmd.angular.z = -2.5  # Sharp, aggressive right pivot
            
        # 2. OPPORTUNITY: Left gap detected
        # The moment the left wall vanishes, it will begin arcing left into the new corridor.
        elif d_left > 0.85:
            # We move slightly forward while turning to ensure the chassis clears the inner corner
            cmd.linear.x = 0.6
            cmd.angular.z = 1.5   # Smooth left curve
            
        # 3. CORRIDOR CRUISING: Safe to drive
        # We have a wall on our left and open space ahead. 
        else:
            cmd.linear.x = 3.0    # High speed straightaway drive
            
            # P-Controller: Mathematically locks the robot exactly 0.5 units away from the left wall
            target_distance = 0.5 
            error = d_left - target_distance
            
            # If it drifts right, it steers left. If it drifts left, it steers right. 
            cmd.angular.z = error * 4.0 
            
        self.cmd_pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = StudentSolver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

