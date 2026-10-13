Este documento es una guía para los diferentes archivos presentes en este repositorio de Github.
Se recomienda leer en primer lugar el documento Informe_1.pdf en el cual se mencionan todos los cambios de hardware realizados en los ASV.
Se adjunta, además, una carpeta comprimida llamada Diseños 3D.rar que contiene todos los archivos de diseños 3D de piezas creadas para este proyecto. Para abrir dichos archivos editables en su extensión .sdlprt o .sdlasm, se debe utilizar la herramienta Solidworks en su versión 2019 o posterior. De no tener dicha herramienta, se pueden abrir los archivos de sólo lectura .stl para su impresión directa. 
Las impresiones 3D fueron realizadas en plástico PLA blanco o negro con altura de capa de 0.2 [mm]. Sin embargo, algunas piezas como el soporte del módulo GPS se imprimió en plástico PETG blanco con la misma altura de capa. 
Una vez montado el hardware, se debe cargar el firmware al autopiloto Pixhawk de cada bote. Para ello, además de toda configuración al autopiloto a realizar, se debe descargar e instalar el software QGroundControl (ahora en adelante referido como QGC) a una computadora con Windows o Linux. 
En la carpeta Firmware PX4.rar se encuentra el archivo px4_fmu-v5_rover.px4 el cual es el firmware ya compilado y  debe ser cargado mediante el QGC. 
Tras cargar el firmware, se deben configurar una serie de parámetros. Se puede saltar este paso cargando el archivo backup_parametros.params. Pero 
•	Airframe: se debe escoger el Generic Rover Differential
•	Sensors:  se deben calibrar los sensores Compass, Gyroscope, Accelerometer y Level Horizon. Para cada sensor, el QGC menciona el procedimiento de calibración del mismo. 
•	Radio: se deben identificar las señales producidas por el control remoto mediante el comando Calibrate. En caso de que el control remoto no se esté asociado con el receptor del mismo, leer el inciso LINK PROCEDURE (T6K/R3006SB) en la página 37 del documento Futaba T6K User Manual.pdf.
•	Flight Modes: En la misma, definir los siguientes valores:
o	Mode Channel: 6
o	Mode 1: Manual
o	Mode 2: Unnasigned
o	Mode 3: Unnasigned
o	Mode 4: Position
o	Mode 5: Unnasigned
o	Mode 6: Offboard
o	Arm switch channel: 5
o	Emergency Switch Channel: Unnasigned
o	Offboard Switch Channel: Unnasigned
o	Landing Gear Switch Channel: Unnasigned
o	Return Switch Chanel: Unnasigned
•	Actuators: En el apartado PWM MAIN:
o	MAIN 1-2: OneShot
o	MAIN 1: Left Motor
	 Disarmed=1500
	Minimum=1100
	Maximum=1900
	Rev Range=True
o	MAIN 2: Right Motor
	Mismos parámetros que para el MAIN 1
o	Todos los demás valores de MAIN dejar en Disabled
•	Power: 
o	Battery Source 1: Disabled
o	Battery Source 2: Power Module
	Number of cells=4
	Empty voltaje per cell = 3.7 V
	Full voltage per cell = 4.2 V
	Voltage Divider se define mediante las instrucciones al tocar el botón Calculate
	Amps per volt no es necesario tocar por una posible incompatibilidad o daño del amperímetro del modulo PM07 
o	ESC PWM Calibration: antes de realizarlo, definir previamente todos los parametros anteriormente citados y el autopiloto debe estar conectado directamente a la computadora mediante el cable USB. Seguir las instrucciones mencionadas al tocar el botón Calibrate.
•	Parameters:
o	MAN_ARM_GESTURE: Disabled
o	NAV_ACC_RAD: 0.5 m
o	PP_LOOKAHD_GAIN: 0.1
o	PP_LOOKAHD_MAX: 5 m
o	PP_LOOKAHD_MIN: 2 m
o	RD_MAX_THR_YAW_R: 0.9 m/s
o	RD_WHEEL_TRACK: 1 m
o	SER_TEL2_BAUD: 115200 8N1
o	SDLOG_MISSION: All mission messages
o	SDLOG_MODE: when armed until disarm
o	RO_ACCEL_LIM: -1
o	RO_DECEL_LIM: -1
o	RO_JERK_LIM: -1
o	RO_SPEED_I: 0
o	RO_SPEED_LIM: 2
o	RO_SPEED_P: 0
o	RO_SPEED_TH: 0.1
o	RO_YAW_ACCEL_LIM: -1
o	RO_YAW_DECEL_LIM: -1
o	RO_YAW_P: 5
o	RO_YAW_RATE_I: 10
o	RO_YAW_RATE_LIM: 73
o	RO_YAW_RATE_P: 1
o	RO_YAW_RATE_TH: 0
o	RO_YAW_STICK_DZ: 0
o	CAL_MAG0_PRIO: Disabled
o	CAL_MAG1_PRIO: High

La carpeta px4_custom_logging_routine contiene una carpeta al que hay que copiarla a la raíz de la memoria SD del autopiloto para poder asegurar una transmisión adecuada de los datos necesarios para la navegación en el modo Offboard. 
Tras ello, se puede probar una serie de códigos tanto en una computadora como en una RaspberryPi. 
Todos los códigos presentados se ejecutan en Python, y se debe instalar la librería pymavlink previamente.  El primer código a probar es mavlink¬¬-_nedread_threaded_test.py con el cual se muestra en pantalla el angulo de yaw, posición X e Y y el voltaje de la batería. 
Se debe tomar en cuenta el puerto serial asignado en la computadora para ejecutar el código anteriormente mencionado. En la línea 12, definir como UAV_PORT=’COMX’ según el puerto COM numero X en el caso de usar una computadora con Windows. Reemplazar por UAV_PORT=’/dev/serial0’ en caso de usar una RaspberryPi asumiendo que se usa un cable que conecta el puerto TELEM2 del autopiloto al puerto Serial0 de la RaspberryPi.
Una vez dicho código funciona, se puede utilizar el código mavlink_offboardcontrol_test.py para enviar comandos de movimiento al bote. En el mismo, se deben definir los puntos X e Y relativos al frente del bote cuando está en la costa. Los valores yaw0, x0_ned e y0¬_ned se determinan ejecutando el código mavlink¬¬¬_nedread_threaded_test.py anteriormente mencionado con el bote estando en la bahía con su frente apuntando al lago. Cambiar el parámetro UAV_DRIVE_INTERVAL si se desea que el bote esté mas tiempo en un mismo punto. Una vez se ejecuta este código, se debe poner el autopiloto en el modo Offboard.
Tras ello, se puede probar la intercomunicación serial utilizando los códigos serial_read.py y serial¬_write.py. Estos códigos se hicieron para comprobar que se puede enviar cualquier tipo de información utilizando los modulos de telemetria del autopiloto. Se debe desconectar el modulo de telemetria del autopiloto y conectarla a la RaspberryPi mediante un cable USB. 
Se incluye, finalmente, las rutas realizadas por los botes en archivos KML legibles en Google Earth en la carpeta rutas.


