#To send trajectory points to a PX4 autopilot via MAVLink, use the SET_POSITION_TARGET_LOCAL_NED message (#84) or the TRAJECTORY_REPRESENTATION_WAYPOINT message (#332). 
#The local NED message is the most widely supported method for offboard control.
#
#Prerequisites:
#Flight Mode: PX4 must be in Offboard Mode.
#Stream Rate: You must stream target points continuously (at least 2Hz, ideally 10Hz–20Hz).  PX4 will exit offboard mode if it stops receiving messages.
#Coordinate System: Position inputs must use the MAV_FRAME_LOCAL_NED frame (North, East, Down, where Down is negative altitude).

#The type_mask tells the flight controller which fields to ignore. If you forget to configure this, the drone may ignore your coordinates or behave erratically.
#Position Control Only: 0x0DC7 (Ignore velocity, acceleration, yaw rate)
#Velocity Control Only: 0x0DC0 (Ignore position, acceleration, yaw rate)
#Position + Velocity: 0x0D40 (Ignore acceleration, yaw rate)

#Before PX4 accepts these points, ensure your GCS or script is continuously sending a heartbeat message alongside the data stream. PX4 requires a steady stream of HEARTBEAT messages from the offboard component (Component ID 191 or similar).


#Learn more about position mode bitmasks: https://ardupilot.org/dev/docs/copter-commands-in-guided-mode.html

from pymavlink import mavutil
import math
from time import time,sleep

# 1. Connect to the vehicle (UDP, TCP, or Serial)
# Change '127.0.0.1:14540' to your connection string
UAV_PORT='COM15' #UAV SERIAL PORT 
UAV_BAUDRATE= 57600 #UAV BAUDRATE PORT
UAV_DRIVE_INTERVAL = 15 #HOW MUCH TIME THE ASV HAS TO REACH AND STAY TO A POINT
master = mavutil.mavlink_connection(UAV_PORT,baud=UAV_BAUDRATE)

master.wait_heartbeat()

# 2. Define target parameters
boot_time = 0 # System boot time (can be 0 for auto-fill)
target_system = master.target_system
target_component = master.target_component
coordinate_frame = mavutil.mavlink.MAV_FRAME_LOCAL_NED

# 3. Bitmask selection
# Tell PX4 which values to ignore. 
# To use Position ONLY, ignore velocity, acceleration, force, and yawrate.
# (1 << 0) Ignore Position X
# (1 << 1) Ignore Position Y
# (1 << 2) Ignore Position Z
# (1 << 3) Ignore Velocity X ... and so on.
position_only_bitmask = 0b110111111100  # Hex: Ignore EVERYTHING but the Force Set, X and Y control

def body2ned(x_body,y_body,yaw):
    x_ned = math.cos(yaw)*x_body - math.sin(yaw)*y_body # x_ned meters to the North
    y_ned = math.sin(yaw)*x_body + math.cos(yaw)*y_body # y_ned meters to the East
    return x_ned,y_ned

x_sps_body = [0.0,15.,30.,30.,15.0,15.0,0.0]  # x_sp_body meters to the front of the ASV
y_sps_body = [0.0,0.0,0.0,15.0,15.0,15.0,0.0]  # y_sp_body meters to the left  of the ASV 
len_sp     = len(x_sps_body)

x_sp_ned = 0 
y_sp_ned = 0

yaw0   = 200*(math.pi/180)
x0_ned = -4
y0_ned = -9
# 4. Target Coordinates (NED: North, East, Down)
#x_sp_ned,y_sp_ned = body2ned(x_body,y_body,initial_yaw)
#

time_ant = time()
i=0
# 5. Continuous Stream Loop (Offboard requirement)
while True:
    if i<len_sp:
        if((time()-time_ant)>UAV_DRIVE_INTERVAL):
            x_sp_prima_ned,y_sp_prima_ned = body2ned(x_sps_body[i],y_sps_body[i],yaw0)
            x_sp_ned = x_sp_prima_ned + x0_ned
            y_sp_ned = y_sp_prima_ned + y0_ned
            time_ant = time()
            print("Desired X: "+ str(x_sp_ned) +"[m]  Desired Y: " + str(y_sp_ned) + "[m]")
            i=i+1 
    master.mav.set_position_target_local_ned_send(
        boot_time,          # time_boot_ms
        target_system,      # target_system
        target_component,   # target_component
        coordinate_frame,   # coordinate_frame
        position_only_bitmask, # type_mask
        x_sp_ned, y_sp_ned, 0, # x, y, z positions
        0, 0, 0,            # vx, vy, vz velocities (ignored by bitmask)
        0, 0, 0,            # afx, afy, afz accelerations (ignored by bitmask)
        0, 0                # yaw, yaw_rate
    )
    sleep(0.1) # Send at 10Hz
