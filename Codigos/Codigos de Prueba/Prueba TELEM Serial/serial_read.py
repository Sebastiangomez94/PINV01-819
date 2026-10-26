import serial
import time

# Configure the serial port
# Replace 'COM3' (Windows) or '/dev/ttyUSB0' (Linux/Mac) with your actual port
SERIAL_PORT = 'COM12' 
BAUD_RATE = 57600

try:
    # Open the serial port with a 1-second timeout
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud.")
    
    # Optional: Brief pause to let the serial connection stabilize
    time.sleep(2) 

    while True:
        # Check if there is data waiting in the buffer
        if ser.in_waiting > 0:
            # Read a line of data until a newline ('\n') character is found
            raw_data = ser.readline()
            
            # Decode bytes to a string and strip whitespace/newlines (\r\n)
            clean_string = raw_data.decode('utf-8').rstrip()
            
            # Print the clean string to the console
            print(clean_string)
            
except serial.SerialException as e:
    print(f"Error opening or communicating with serial port: {e}")

except KeyboardInterrupt:
    print("\nProgram interrupted by user. Closing serial port...")

finally:
    # Ensure the serial port is closed safely when exiting
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Serial port closed.")
