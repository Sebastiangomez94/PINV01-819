import time
from pymavlink import mavutil

# 1. Establish connection with Pixhawk 4 (adjust port/baudrate to match your physical link)
# e.g., '/dev/ttyTHS1' for serial companion computer link or '127.0.0.1:14540' for SITL simulation
connection = mavutil.mavlink_connection('127.0.0.1:14540')
connection.wait_heartbeat()
print(f"Heartbeat detected from system {connection.target_system} component {connection.target_component}")

# Target Global Coordinates (Example: San Francisco area)
# Latitude & Longitude must be integer scales: degrees * 1e7
TARGET_LAT = int(37.7749 * 1e7)
TARGET_LON = int(-122.4194 * 1e7)
TARGET_ALT = 30.0  # Altitude in meters (AMSL or WGS84 depending on PX4 EK2 parameter settings)
TARGET_YAW = 0.0   # Radians (0 = North)

def send_global_setpoint():
    """Streams a single SET_POSITION_TARGET_GLOBAL_INT message to PX4."""
    connection.mav.set_position_target_global_int_send(
        time_boot_ms=int(time.time() * 1000) & 0xFFFFFFFF,
        target_system=connection.target_system,
        target_component=connection.target_component,
        coordinate_frame=mavutil.mavlink.MAV_FRAME_GLOBAL_INT, # Standard WGS84 frame
        type_mask=GLOBAL_POS_MASK,                             # Fields to ignore
        lat_int=TARGET_LAT,                                    # Lat * 1e7
        lon_int=TARGET_LON,                                    # Lon * 1e7
        alt=TARGET_ALT,                                        # Alt in meters
        vx=0, vy=0, vz=0,                                      # Ignored by mask
        afx=0, afy=0, afz=0,                                   # Ignored by mask
        yaw=TARGET_YAW,                                        # Yaw angle
        yaw_rate=0                                             # Ignored by mask
    )

# 2. Stream setpoints BEFORE switching mode
# PX4 will refuse to enter OFFBOARD mode if it is not actively receiving commands.
print("Streaming initial setpoints...")
for _ in range(20):
    send_global_setpoint()
    time.sleep(0.1)  # 10 Hz stream rate

# 3. Request PX4 to enter OFFBOARD mode
# In PX4, OFFBOARD mode uses base_mode=0, custom_mode=6
connection.mav.set_mode_send(
    connection.target_system,
    mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
    6  # PX4 Main Mode: OFFBOARD
)
print("Offboard mode command sent.")

# 4. Maintain the Offboard Control Loop
# You must loop the setpoint transmissions continuously to avoid timeout failsafes.
try:
    print("Maintaining offboard loop. Press Ctrl+C to terminate.")
    while True:
        send_global_setpoint()
        time.sleep(0.1)  # Maintain 10 Hz frequency
except KeyboardInterrupt:
    print("Exiting control loop.")
