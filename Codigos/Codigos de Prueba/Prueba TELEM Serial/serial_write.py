import time
import serial
#import secrets

# 1. Configure and open the serial port
# Replace 'COM3' with your specific port (e.g., '/dev/ttyUSB0' on Linux)
ser = serial.Serial(
    port="COM12", baudrate=57600, timeout=1  # Match the receiver's baud rate
)

#A very random number generator: secrets.randbelow(100)


# 2. Wait for the connection to initialize
# Crucial if connecting to microcontrollers like Arduino, which reset upon connection
time.sleep(1)
i=0
while True:

    try:
        time.sleep(.1)
        # Your target string
        message = "Packet with an integer number: " + str(i) + " "
        i=i+1
        # 3. Add a newline delimiter (common for line-by-line reading devices)
        message_with_newline = message + "\n"

        # 4. Encode the string to bytes and write to the serial port
        ser.write(message_with_newline.encode("utf-8"))

        print(f"Successfully sent: {message}")

    except Exception as e:
        print(f"An error occurred: {e}")
        ser.close()

    
