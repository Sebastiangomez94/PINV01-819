import serial
import time
import math
import threading
from pymavlink import mavutil

# Puerto serial del módulo inalámbrico (Telemetría hacia GCS/Base)
SERIAL_PORT = '/dev/ttyUSB0'   # Ajusta según tu hardware
BAUD_RATE = 57600

# Puerto MAVLink: Conexión con Pixhawk/ArduPilot
UAV_PORT = '/dev/serial0'
UAV_BAUDRATE = 115200

COORD_TIMEOUT = 10.0   # Tiempo máximo sin recibir coordenadas deseadas
SEND_INTERVAL = 2      # Frecuencia mínima de envío a la Pixhawk (1/2 Hz)

# Conexión al puerto serial de radio
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
print(f"Conectado al puerto serial {SERIAL_PORT} a {BAUD_RATE} baud.")

# Conexión MAVLink a la controladora de vuelo (Pixhawk)
master = mavutil.mavlink_connection(UAV_PORT, baud=UAV_BAUDRATE)
master.wait_heartbeat()
print("Conectado al dron vía MAVLink. Corazón detectado.")

last_coord_time = 0
x_ned_sp, y_ned_sp = None, None
last_send_time = 0
timeout_printed = False  # Bandera para evitar repetir logs innecesarios

# Variables globales para almacenar la telemetría del ASV
x_actual = 0.0
y_actual = 0.0
yaw_deg = 0.0
x0 = 0.0
y0 = 0.0

# Banderas para indicar recepción de nuevos datos
new_telemetry_available = False

def read_mavlink_telemetry():
    """Hilo secundario para procesar de forma continua los mensajes MAVLink de la Pixhawk."""
    global x_actual, y_actual, yaw_deg, x0, y0, new_telemetry_available
    while True:
        try:
            # 1. Leer origen de coordenadas (HOME_POSITION)
            att      = master.recv_match(type='ATTITUDE', blocking=False)
            localpos = master.recv_match(type='LOCAL_POSITION_NED', blocking=False)
            homepos  = master.recv_match(type='HOME_POSITION', blocking=False)            
            if homepos:
                x0 = homepos.x
                y0 = homepos.y
                print("Homepos actualizado")

            # 2. Leer posición local (LOCAL_POSITION_NED)
            
            if localpos:
                x_actual = localpos.x
                y_actual = localpos.y
                print("Localpos actualizado")
                new_telemetry_available = True

            # 3. Leer orientación/actitud (ATTITUDE) para extraer el Yaw
            
            if att:
                yaw_deg = att.yaw * (180.0 / math.pi)
                new_telemetry_available = True
                print("Att actualizado")

            time.sleep(0.01)  # Pequeño descanso para el hilo secundario
        except Exception as e:
            print(f"Error en hilo MAVLink: {e}")

# Iniciar el hilo secundario de MAVLink como Daemon (se cierra al terminar el programa)
mavlink_thread = threading.Thread(target=read_mavlink_telemetry, daemon=True)
mavlink_thread.start()

try:
    while True:
        # 1. Lectura de coordenadas deseadas recibidas por la radio desde la estación base
        while ser.in_waiting > 0:
            try:
                raw_data = ser.readline().decode('utf-8', errors='ignore').strip()
                if ',' in raw_data:
                    x_str, y_str = raw_data.split(',')
                    x_ned_sp, y_ned_sp = float(x_str), float(y_str)
                    last_coord_time = time.time()
                    timeout_printed = False
                    print(f"Coordenada relativa recibida de GCS: X_rel={x_ned_sp:.2f}, Y_rel={y_ned_sp:.2f}")
            except (ValueError, IndexError) as e:
                print(f"Error procesando datos serie: ({e})")

        # 2. Transmitir estado actual relativo (Posición [X-X0, Y-Y0] + Yaw) hacia la base
        if new_telemetry_available:
            x_rel = x_actual - x0
            y_rel = y_actual - y0
            actual_message = f"ACTUAL_NED:{x_rel:.2f},{y_rel:.2f},{yaw_deg:.2f}\n"
            ser.write(actual_message.encode("utf-8"))
            new_telemetry_available = False

        # 3. Transmitir setpoints corregidos con X0 e Y0 a la Pixhawk
        if x_ned_sp is not None and y_ned_sp is not None:
            if (time.time() - last_coord_time) <= COORD_TIMEOUT:
                if (time.time() - last_send_time) >= SEND_INTERVAL:
                    # Sumar origen de coordenadas X0 e Y0
                    x_target = x_ned_sp + x0
                    y_target = y_ned_sp + y0

                    # Máscara para posición X,Y (0x0DFB = ignora Z, VX, VY, VZ, AX, AY, AZ, YAW, YAW_RATE)
                    type_mask = 0b110111111011

                    master.mav.set_position_target_local_ned_send(
                        0,                                    # time_boot_ms
                        master.target_system,                 # target_system
                        master.target_component,              # target_component
                        mavutil.mavlink.MAV_FRAME_LOCAL_NED,  # frame
                        type_mask,                            # type_mask
                        x_target, y_target, 0.0,              # X_target, Y_target corregidos
                        0, 0, 0,                              # VX, VY, VZ
                        0, 0, 0,                              # AX, AY, AZ
                        0, 0                                  # YAW, YAW_RATE
                    )
                    print(f"Enviado a Pixhawk (Relativo + Origen): X={x_target:.2f} (X0={x0:.2f}), Y={y_target:.2f} (Y0={y0:.2f})")
                    last_send_time = time.time()
            else:
                if not timeout_printed:
                    print("Tiempo de espera agotado: Se detuvo el envío de consignas al autopiloto.")
                    timeout_printed = True

        time.sleep(0.01)  # Descanso breve para prevenir sobrecarga de CPU

except KeyboardInterrupt:
    print("\nPrograma interrumpido por el usuario.")
except Exception as e:
    print(f"\nError de ejecución: {e}")
finally:
    if ser and ser.is_open:
        ser.close()
    print("Puerto serial cerrado correctamente.")