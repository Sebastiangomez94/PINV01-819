import serial
import time
import math

# Configuración de los puertos serial de los módulos inalámbricos
DRONE1_PORT = 'COM15'   # Ajusta al puerto del primer módulo
DRONE2_PORT = 'COM12'  # Ajusta al puerto del segundo módulo
BAUDRATE = 57600

two_asv_mode = False

# Listas independientes de waypoints en NED para cada dron
waypoints_body_drone1 = [
    (0.0, 0.0),
    (5.0, 0.0),
    (5.0, 5.0),
    (0.0, 5.0),
    (0.0, 0.0)
]

waypoints_body_drone2 = [
    (0.0, 0.0),
    (2.0, 0.0),
    (2.0, 2.0),
    (0.0, 2.0),
    (0.0, 0.0)
]

yaw_body_zero = 90*(math.pi/180)


DIST_THRESHOLD = 0.5   # 50 cm
SEND_INTERVAL  = 0.5     # Cada 1 segundos
# Conexión a los puertos serial
ser1 = serial.Serial(DRONE1_PORT, BAUDRATE, timeout=1)
ser2 = serial.Serial(DRONE2_PORT, BAUDRATE, timeout=1) if two_asv_mode else None

if two_asv_mode:
    print(f"Conectado a {DRONE1_PORT} y {DRONE2_PORT}")
else:
    print(f"Conectado únicamente a {DRONE1_PORT}")

# Índices de waypoint para cada dron
wp_index1 = 0
wp_index2 = 0

last_send_time = 0

def body2ned(x_body,y_body,yaw):
    x_ned = math.cos(yaw)*x_body - math.sin(yaw)*y_body # x_ned meters to the North
    y_ned = math.sin(yaw)*x_body + math.cos(yaw)*y_body # y_ned meters to the East
    return x_ned,y_ned

def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def process_serial_data(ser, drone_name, current_wp_index, waypoints_body_list):
    """Procesa todo el buffer pendiente recibiendo X, Y y Yaw desde la telemetría del ASV."""
    global yaw_body_zero
    updated_index = current_wp_index
    while ser.in_waiting > 0:
        try:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line.startswith("ACTUAL_POS:"):
                coords = line.replace("ACTUAL_POS:", "").split(',')
                
                # Extrae X, Y y Yaw (grados)
                x = float(coords[0])
                y = float(coords[1])
                yaw = float(coords[2]) if len(coords) > 2 else 0.0
                
                print(f"{drone_name} actual: X={x:.2f}, Y={y:.2f}, Yaw={yaw:.1f}")
                
                if updated_index < len(waypoints_body_list):
                    x_sp_body, y_sp_body = waypoints_body_list[updated_index]
                    x_sp,y_sp=body2ned(x_sp_body,y_sp_body,yaw_body_zero)
                    distance_asv=distance(x, y, x_sp, y_sp)
                    if  distance_asv < DIST_THRESHOLD:
                        updated_index += 1
                        print(f"{drone_name} alcanzó waypoint. Siguiente índice: {updated_index}")
                    else:
                        print(f"{drone_name} a {distance_asv:.2f} [m] del waypoint")
        except (ValueError, IndexError):
            pass  # Descarta paquetes mal formados o incompletos
    return updated_index

try:
    while True:
        # 1. Leer y procesar telemetría de cada bote
        wp_index1 = process_serial_data(ser1, "Dron1", wp_index1, waypoints_body_drone1)
        if two_asv_mode and ser2:
            wp_index2 = process_serial_data(ser2, "Dron2", wp_index2, waypoints_body_drone2)

        # 2. Enviar setpoints periódicamente a 2 Hz
        if (time.time() - last_send_time) >= SEND_INTERVAL:
            # Enviar setpoint a Dron 1
            idx1 = min(wp_index1, len(waypoints_body_drone1) - 1)
            x_sp1_body, y_sp1_body = waypoints_body_drone1[idx1]
            x_sp1,y_sp1=body2ned(x_sp1_body,y_sp1_body,yaw_body_zero)
            ser1.write(f"{x_sp1},{y_sp1}\n".encode('utf-8'))
            print(f"Enviado a Dron1: Xsp={x_sp1}, Ysp={y_sp1}")

            # Enviar setpoint a Dron 2
            if two_asv_mode and ser2:
                idx2 = min(wp_index2, len(waypoints_body_drone2) - 1)
                x_sp2_body, y_sp2_body = waypoints_body_drone2[idx2]
                x_sp2,y_sp2=body2ned(x_sp2_body,y_sp2_body,yaw_body_zero)
                ser2.write(f"{x_sp2},{y_sp2}\n".encode('utf-8'))
                print(f"Enviado a Dron2: Xsp={x_sp2}, Ysp={y_sp2}")

            last_send_time = time.time()

        time.sleep(0.01)  # Pausa breve para prevenir sobrecarga de CPU

except KeyboardInterrupt:
    print("\nPrograma interrumpido por el usuario.")
except Exception as e:
    print(f"\nError de ejecución: {e}")
finally:
    # Cierre seguro de los puertos seriales
    if ser1 and ser1.is_open:
        ser1.close()
    if ser2 and ser2.is_open:
        ser2.close()
    print("Puertos seriales cerrados correctamente.")