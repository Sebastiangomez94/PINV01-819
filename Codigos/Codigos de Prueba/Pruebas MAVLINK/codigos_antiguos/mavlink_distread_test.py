#python mavlink_distread_test.py
from pymavlink import mavutil
from time import time,sleep
import math 


#It is assumed that MAVLINK connection to Pixhawk is through serial port

#CONNECTION TYPE                    : (UAV_PORT,UAV_BAUDRATE)
#-----------------------------------:-----------------------------
#TELEMETRY MODULE ON WIN10          : ('COM7',57600)
#TELEM2 PORT TO FTDI MODULE ON WIN10: ('COM11',115200) 
#TELEM2 PORT TO FTDI MODULE ON RPI4B: ('/dev/ttyUSB0',baud=115200)
#TELEM2 PORT TO UART0 ON RPI4B      : ('/dev/serial0',baud=115200)

UAV_PORT='COM5' #UAV SERIAL PORT 
UAV_BAUDRATE=57600 #UAV BAUDRATE PORT

UAV_CONNECTION_RETRY_TIME2WAIT=2 #TIME TO WAIT WHEN A CONNECTION RETRY MUST BE DONE
UAV_HEARTBEAT_TIMEOUT =5          #TIME TO WAIT TO ASSUME A HEARTBEAT CALL HAS FAILED
UAV_READPARAM_TIMEOUT =20         #TIME TO WAIT TO ASSUME A READPARAM CALL HAS FAILED
UAV_RECVMATCH_TIMEOUT =2         #TIME TO WAIT TO ASSUME A RECVMATCH CALL HAS FAILED
UAV_DISPUPD_INTERVAL  =0.2           #TIME TO WAIT BETWEEN SCREEN UPDATES
   

print("I will print LIDARLITE current distance coming from the Pixhawk...") 
  
#This function creates a Mavlink port and checks for a heartbeat to ensure connection stability and,
#then, it reads the pith controller proportional parameter

def UAV(port,baudrate):
    connection=None
    while connection is None:
        try:
            connection=mavutil.mavlink_connection(port,baud=baudrate)
            print("Connection successful. Waiting for heartbeat")
            connection.wait_heartbeat(timeout=UAV_HEARTBEAT_TIMEOUT)
        except:
            print('Connection failed and/or no heartbeat, retrying...')
            sleep(UAV_CONNECTION_RETRY_TIME2WAIT)
            continue
        else:
            print("Got a hearbeat.")
            return connection
            break
      

#Create the MAVLINK connection and get the pitch controller parameter              
test_uav=UAV(UAV_PORT,UAV_BAUDRATE) 

time_ant=time()
time_ant_display=time_ant
update_count=0
distance=0
rate=0

#Initiate the control loop until program finishes
while True:
    try:
        #Call for desired angular rate topic
        dist_sensor=test_uav.recv_match(type='DISTANCE_SENSOR',blocking=False, timeout=UAV_RECVMATCH_TIMEOUT)
    #To kill the program...press Ctrl+C
    except KeyboardInterrupt:
        print('Keyboard interrupt catched, finishing...')
        exit()
    except:
        #Retry everything if connection fails
        print('Connection failed, reconnecting...')
        sleep(UAV_CONNECTION_RETRY_TIME2WAIT)
        test_uav=UAV(UAV_PORT,UAV_BAUDRATE)
        time_ant=time()
        time_ant_display=time_ant
        update_count=0
    else:
        if dist_sensor:
            #Obtain distance measured from LIDAR. Do not expect a very high sample rate because of the MAVLINK "bootleneck"
            time_actual=time()
            if time_actual!=time_ant:
                distance=dist_sensor.current_distance
                time_ant=time_actual
                update_count+=1
    if (time()-time_ant_display) >= UAV_DISPUPD_INTERVAL:
        rate=update_count/UAV_DISPUPD_INTERVAL
        update_count=0
        time_ant_display=time()            
        print("Current distance: "+ str(distance/100) +"[m] Average update rate: " + str(rate) + " [Hz]")
                
