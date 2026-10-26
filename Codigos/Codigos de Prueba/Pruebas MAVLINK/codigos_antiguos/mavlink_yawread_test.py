#python mavlink_yawread_test.py
from pymavlink import mavutil
from time import time,sleep
import math 


#This program  gets the attitude error by this mean:

# pitch_rate_sp = MC_PITCH_P*(pitch_sp-pitch)
# pitch_rate_sp = MC_PITCH_P*pitch_err
# pitch_err     = pitch_rate_sp/MC_PITCH_P

#Then, with this pitch error, the desired CMG control force is computed through a PID controller.
#The PID controller output has a range of -1 to 1 (non-excluding)



#I do this way because of simplicity instead of calling  for actual pitch angle and desired pitch angle separately. This is because it takes less
#MAVLINK stream bandwith just to call for one topic (angular rate setpoint on this case). 

#The Pixhawk attitude controller works like this: It takes the attitude error (which is equal to the desired attitude minus actual atittude) and compute 
#the desired angular rate by just multiplying the attitude error to a proportional constant. 
#Then, with this desired angular rate, it computes the angular rate error and compute the desired torque control forces trough an
#angular rate PID controller.

#It is assumed that MAVLINK connection to Pixhawk is through serial port

#CONNECTION TYPE                    : (UAV_PORT,UAV_BAUDRATE)
#-----------------------------------:-----------------------------
#TELEMETRY MODULE ON WIN10          : ('COM7',57600)
#TELEM2 PORT TO FTDI MODULE ON WIN10: ('COM11',115200) 
#TELEM2 PORT TO FTDI MODULE ON RPI4B: ('/dev/ttyUSB0',baud=115200)
#TELEM2 PORT TO UART0 ON RPI4B      : ('/dev/serial0',baud=115200)

UAV_PORT='COM12' #UAV SERIAL PORT 
UAV_BAUDRATE=57600 #UAV BAUDRATE PORT
#UAV_PORT='/dev/serial0' #UAV SERIAL PORT 
#UAV_BAUDRATE=115200 #UAV BAUDRATE PORT

UAV_CONNECTION_RETRY_TIME2WAIT=2 #TIME TO WAIT WHEN A CONNECTION RETRY MUST BE DONE
UAV_HEARTBEAT_TIMEOUT=5          #TIME TO WAIT TO ASSUME A HEARTBEAT CALL HAS FAILED
UAV_READPARAM_TIMEOUT=20         #TIME TO WAIT TO ASSUME A READPARAM CALL HAS FAILED
UAV_RECVMATCH_TIMEOUT =2         #TIME TO WAIT TO ASSUME A RECVMATCH CALL HAS FAILED
UAV_DISPUPD_INTERVAL=0.5           #TIME TO WAIT BETWEEN SCREEN UPDATES
   

print("I will print yaw angle coming from the Pixhawk...") 
  
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
sebas_uav=UAV(UAV_PORT,UAV_BAUDRATE) 

time_ant=time()
time_ant_display=time_ant
update_count=0


#Initiate the control loop until program finishes
while True:
    try:
        #Call for desired angular rate topic
        att=sebas_uav.recv_match(type='ATTITUDE',blocking=False, timeout=UAV_RECVMATCH_TIMEOUT)
    #To kill the program...press Ctrl+C
    except KeyboardInterrupt:
        print('Keyboard interrupt catched, finishing...')
        exit()
    except:
        #Retry everything if connection fails
        print('Connection failed, reconnecting...')
        sleep(UAV_CONNECTION_RETRY_TIME2WAIT)
        sebas_uav=UAV(UAV_PORT,UAV_BAUDRATE)
        time_ant=time()
        time_ant_display=time_ant
        update_count=0
    else:
        if att:
            #Obtain yaw angle and yaw rate. Do not expect a very high sample rate because of the MAVLINK "bootleneck"
            time_actual=time()
            if time_actual!=time_ant:
                yaw=att.yaw
                yawrate=att.yawspeed
                time_ant=time_actual
                update_count+=1
    if (time()-time_ant_display) >= UAV_DISPUPD_INTERVAL:
        rate=update_count/UAV_DISPUPD_INTERVAL
        update_count=0
        time_ant_display=time()            
        print("Yaw: "+ str(yaw*(180/math.pi)) +"[deg] Yaw rate: " + str(yawrate*(180/math.pi)) + "  [deg/s]  Average rate: " + str(rate) + " [Hz]")
                
