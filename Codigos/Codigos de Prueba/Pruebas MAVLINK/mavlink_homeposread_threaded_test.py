#python mavlink_yawread_test.py

#It is assumed that MAVLINK connection to Pixhawk is through serial port

#CONNECTION TYPE                    : (UAV_PORT,UAV_BAUDRATE)
#-----------------------------------:-----------------------------
#TELEMETRY MODULE ON WIN10          : ('COM7',57600)
#TELEM2 PORT TO FTDI MODULE ON WIN10: ('COM11',115200) 
#TELEM2 PORT TO FTDI MODULE ON RPI4B: ('/dev/ttyUSB0',baud=115200)
#TELEM2 PORT TO UART0 ON RPI4B      : ('/dev/serial0',baud=115200)

from pymavlink import mavutil
from time import time,sleep
import threading

UAV_PORT='COM12' #UAV SERIAL PORT 
UAV_BAUDRATE=57600 #UAV BAUDRATE PORT
#UAV_PORT='/dev/serial0' #UAV SERIAL PORT 
#UAV_BAUDRATE=115200 #UAV BAUDRATE PORT

UAV_CONNECTION_RETRY_TIME2WAIT=2 #TIME TO WAIT WHEN A CONNECTION RETRY MUST BE DONE
UAV_HEARTBEAT_TIMEOUT=5          #TIME TO WAIT TO ASSUME A HEARTBEAT CALL HAS FAILED
UAV_READPARAM_TIMEOUT=20         #TIME TO WAIT TO ASSUME A READPARAM CALL HAS FAILED
UAV_RECVMATCH_TIMEOUT =2         #TIME TO WAIT TO ASSUME A RECVMATCH CALL HAS FAILED
UAV_DISPUPD_INTERVAL=0.5         #TIME TO WAIT BETWEEN SCREEN UPDATES
   

print("I will print NED position coming from the Pixhawk...") 
  
#This function creates a Mavlink port and checks for a heartbeat to ensure connection stability and,
#then, it reads the pith controller proportional parameter

def UAV(port,baudrate):
    connection=None
    while connection is None:
        try:
            connection=mavutil.mavlink_connection(port,baud=baudrate)
            print("Connection successful. Waiting for heartbeat")
            connection.wait_heartbeat(timeout=UAV_HEARTBEAT_TIMEOUT)
        except Exception as e:
            print('Connection failed and/or no heartbeat, retrying...')
            print('Error:')
            print(e)
            sleep(UAV_CONNECTION_RETRY_TIME2WAIT)
            continue
        else:
            print("Got a hearbeat.")
            return connection
            break
      


#Create the MAVLINK connection and get the pitch controller parameter              
asv=UAV(UAV_PORT,UAV_BAUDRATE) 

time_ant_display=time()
x0=0
y0=0
homepos_defined = False

def messages_read():
     global x0,y0,homepos_defined
     while True:
        homepos = asv.recv_match(type='HOME_POSITION',blocking=False, timeout=UAV_RECVMATCH_TIMEOUT)
        if homepos:
            x0 = homepos.x
            y0 = homepos.y
            if (abs(x0)> 0.001) and (abs(y0)> 0.001):
                homepos_defined=True
            else:
                homepos_defined=False
messages_read_thread = threading.Thread(target=messages_read)
messages_read_thread.start()

                    
#Initiate the control loop until program finishes
while True:
    try:
        if (time()-time_ant_display) >= UAV_DISPUPD_INTERVAL:
                time_ant_display=time()            
                print("Home X: "+ str(x0) +"[m]  Home y: " + str(y0) + "[m] Homepos Defined: " + str(homepos_defined))                       
    #To kill the program...press Ctrl+C
    except KeyboardInterrupt:
        print('Keyboard interrupt catched, finishing...')
        exit()
    except:
        #Retry everything if connection fails
        print('Connection failed, reconnecting...')
        sleep(UAV_CONNECTION_RETRY_TIME2WAIT)
        asv=UAV(UAV_PORT,UAV_BAUDRATE)
        time_ant=time()
        time_ant_display=time_ant
        update_count=0

    
