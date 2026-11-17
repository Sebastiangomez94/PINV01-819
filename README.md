# Guia de Configuracion y Uso de ASV (Autonomous Surface Vehicles)

Este documento contiene las instrucciones y la guia explicativa para los diferentes archivos, parametros y scripts presentes en este repositorio de GitHub.

---

## 📋 Estructura del Repositorio y Archivos Relevantes

- **`Informe_1.pdf`**: Documento de lectura previa recomendada donde se detallan todos los cambios de hardware realizados en los botes autonomos (ASV).
- **`Disenos 3D.rar`**: Contiene los archivos de modelado 3D de las piezas disenadas para el proyecto.
  - **Archivos editables (`.sdlprt`, `.sdlasm`)**: Requieren el software **SolidWorks 2019** o posterior.
  - **Archivos de lectura/impresion (`.stl`)**: Para impresion directa en caso de no disponer de SolidWorks.
  - **Especificaciones de impresion**: Realizadas en plastico PLA (blanco o negro) con altura de capa de `0.2 mm`. El soporte del modulo GPS fue impreso en PETG blanco con la misma altura de capa.
- **`Firmware PX4.rar`**: Incluye el archivo `px4_fmu-v5_rover.px4`, que corresponde al firmware compilado listo para cargar.
- **`backup_parametros.params`**: Archivo de respaldo para la carga automatica de la configuracion de parametros.
- **`px4_custom_logging_routine`**: Carpeta que debe copiarse a la raiz de la memoria SD del autopiloto para garantizar la correcta transmision de datos en el modo *Offboard*.
- **`Logs 10_11_26/`**: Carpeta que almacena las trayectorias realizadas por los botes en archivos `.kml`, visualizables en Google Earth.
- **`asv_code.py`**: Codigo principal que se debe copiar y ejecutar en cada ASV.
- **`base_code.py`**: Codigo principal de control para ejecutar en la computadora de la base.

---

## ⚙ Configuracion del Autopiloto Pixhawk y Hardware

Tras realizar el montaje fisico del hardware, se debe cargar y configurar el firmware en el autopiloto **Pixhawk** mediante el software **QGroundControl (QGC)** (disponible para Windows y Linux).

### 1. Carga de Firmware
1. Abrir **QGroundControl (QGC)**.
2. Cargar el firmware `px4_fmu-v5_rover.px4` desde la carpeta `Firmware PX4.rar`.
3. *(Opcional)* Cargar el archivo `backup_parametros.params` para omision de la configuracion manual de parametros.

### 2. Airframe y Calibracion de Sensores
- **Airframe**: Seleccionar el tipo **`Generic Rover Differential`**.
- **Sensors**: Calibrar los siguientes sensores siguiendo los pasos indicados en pantalla por QGC:
  - *Compass* (Brujula)
  - *Gyroscope* (Giroscopio)
  - *Accelerometer* (Acelarometro)
  - *Level Horizon* (Nivel del horizonte)

### 3. Configuracion del Control Remoto (Radio)
- Utilizar la opcion **`Calibrate`** en QGC para identificar las senales del transmisor.
- *Nota*: Si el transmisor no esta vinculado al receptor, seguir el procedimiento **`LINK PROCEDURE (T6K/R3006SB)`** en la pagina 37 del documento `Futaba T6K User Manual.pdf`.

### 4. Modos de Vuelo (Flight Modes)
Configurar los asignamientos de canales y modos en QGC segun la siguiente tabla:

| Configuracion / Modo | Valor Asignado |
| :--- | :--- |
| **Mode Channel** | `6` |
| **Mode 1** | `Manual` |
| **Mode 2** | `Unnasigned` |
| **Mode 3** | `Unnasigned` |
| **Mode 4** | `Position` |
| **Mode 5** | `Unnasigned` |
| **Mode 6** | `Offboard` |
| **Arm switch channel** | `5` |
| **Emergency Switch Channel** | `Unnasigned` |
| **Offboard Switch Channel** | `Unnasigned` |
| **Landing Gear Switch Channel** | `Unnasigned` |
| **Return Switch Channel** | `Unnasigned` |

### 5. Actuadores y Motores (Actuators)
En la seccion **PWM MAIN**:
- **MAIN 1-2**: Configurar en `OneShot`.
- **MAIN 1 (Left Motor / Motor Izquierdo)**:
  - `Disarmed`: `1500`
  - `Minimum`: `1100`
  - `Maximum`: `1900`
  - `Rev Range`: `True`
- **MAIN 2 (Right Motor / Motor Derecho)**:
  - Utilizar los mismos parametros que **MAIN 1**.
- **Demas salidas MAIN**: Configurar en `Disabled`.

### 6. Sistema de Alimentacion (Power)
- **Battery Source 1**: `Disabled`
- **Battery Source 2**: `Power Module`
  - `Number of cells`: `4`
  - `Empty voltage per cell`: `3.7 V`
  - `Full voltage per cell`: `4.2 V`
  - `Voltage Divider`: Ajustar siguiendo las instrucciones tras pulsar el boton **`Calculate`**.
  - ⚠ *Advertencia*: No modificar la opcion `Amps per volt` para prevenir incompatibilidades o danos en el amperimetro del modulo PM07.

### 7. Calibracion ESC PWM
1. Asegurarse de haber definido previamente todos los parametros listados.
2. Conectar el autopiloto directamente a la computadora via cable USB.
3. Presionar **`Calibrate`** y seguir las indicaciones.

---

## 📊 Parametros de Control y Registros

| Parametro | Valor Configurado | Parametro | Valor Configurado |
| :--- | :--- | :--- | :--- |
| `MAN_ARM_GESTURE` | `Disabled` | `SDLOG_MISSION` | `All mission messages` |
| `NAV_ACC_RAD` | `0.5 m` | `SDLOG_MODE` | `when armed until disarm` |
| `PP_LOOKAHD_GAIN` | `0.1` | `RO_ACCEL_LIM` | `-1` |
| `PP_LOOKAHD_MAX` | `5 m` | `RO_DECEL_LIM` | `-1` |
| `PP_LOOKAHD_MIN` | `2 m` | `RO_JERK_LIM` | `-1` |
| `RD_MAX_THR_YAW_R`| `0.9 m/s` | `RO_SPEED_I` | `0` |
| `RD_WHEEL_TRACK` | `1 m` | `RO_SPEED_LIM` | `2` |
| `SER_TEL2_BAUD` | `115200 8N1` | `RO_SPEED_P` | `0` |
| `CAL_MAG0_PRIO` | `Disabled` | `RO_SPEED_TH` | `0.1` |
| `CAL_MAG1_PRIO` | `High` | `RO_YAW_ACCEL_LIM`| `-1` |
| `RO_YAW_DECEL_LIM`| `-1` | `RO_YAW_P` | `5` |
| `RO_YAW_RATE_I` | `10` | `RO_YAW_RATE_LIM` | `73` |
| `RO_YAW_RATE_P` | `1` | `RO_YAW_RATE_TH` | `0` |
| `RO_YAW_STICK_DZ` | `0` | | |

---

## 🚀 Tutorial de Uso de Codigos Principales

1. **Conexion a Red WiFi**: Conectar las Raspberry Pi 3B (RPi3B) de los ASVs y una computadora base a una red WiFi comun.

2. **Configuracion y Ejecucion en cada ASV**:
   - **2.1**: Abrir una ventana CMD en la computadora base.
   - **2.2**: Establecer una conexion SSH ejecutando el comando:
     ```bash
     ssh admin@10.74.206.10
     ```
     *(Reemplazar los numeros de la direccion IP segun corresponda a cada ASV)*.
   - **2.3**: Una vez establecida la conexion, ejecutar:
     ```bash
     cd codigos_asv
     ```
     para dirigirse a la carpeta con los archivos de prueba.
   - **2.4**: Ejecutar el siguiente comando para iniciar el entorno virtual en Python:
     ```bash
     python3 -m venv env
     ```
   - **2.5**: Ejecutar el comando para activar dicho entorno virtual:
     ```bash
     source env/bin/activate
     ```
   - **2.6**: Ejecutar el script principal para que el ASV quede listo para recibir comandos de la base:
     ```bash
     python3 asv_code.py
     ```
   - **2.7**: Una vez terminadas las pruebas, presionar `Ctrl+C` para finalizar el programa.
   - **2.8**: En caso de editar una copia del archivo `asv_code.py` desde la base para luego enviarla al ASV, ejecutar:
     ```bash
     scp C:\{UBICACION_DE_TU_ARCHIVO}\asv_code.py admin@10.74.206.10:codigos_asv
     ```
   - **2.9**: Para apagar la RPi3B de forma segura, ejecutar:
     ```bash
     sudo shutdown -h now
     ```

3. **Configuracion de Telemetria en la Base**: En la computadora base, conectar e identificar el puerto COM del modulo de telemetria para cada ASV.

4. **Configuracion y Ejecucion del Codigo Base**: Abrir el codigo `base_code.py` en dicha computadora y definir los puntos a recorrer por cada ASV en coordenadas NED. Se debe incluir el angulo de Yaw inicial de los botes, el cual corresponde a la orientacion inicial de los botes apuntando al lago.

---

## 🐍 Ejecucion de Scripts Secundarios y Pruebas en Python

### Requisito Previo
Todos los scripts estan desarrollados en Python y requieren la libreria **`pymavlink`**:
```bash
pip install pymavlink
```

### 1. Codigos Principales de Operacion

- **`asv_code.py`**: Es el codigo que se debe copiar en cada ASV. Debe ejecutarse antes de ejecutar el codigo `base_code.py` en la computadora de la base.
- **`base_code.py`**: Es el codigo a ejecutar en la computadora base. Se deben definir los diferentes puntos de "waypoints" en coordenadas NED con respecto a los ASV estando en su lugar de origen en el lago con sus frentes apuntando al lago. Antes de ejecutarlo, se deben definir bien los puertos seriales asignados a sus modulos de telemetria.

### 2. Lectura de Datos de Telemetria (`mavlink_nedread_threaded_test.py`)
Muestra en tiempo real el angulo de *yaw*, la posicion relativa ($X$, $Y$) y el voltaje de la bateria.

**Asignacion de Puerto Serial (Linea 12):**
- **Windows**:
  ```python
  UAV_PORT = 'COMX'  # Reemplazar 'X' por el numero de puerto COM asignado
  ```
- **Raspberry Pi** (conexion del puerto TELEM2 de Pvvvixhawk al puerto Serial0):
  ```python
  UAV_PORT = '/dev/serial0'
  ```

### 3. Control de Navegacion Offboard (`mavlink_offboardcontrol_test.py`)
Permite enviar comandos de movimiento al bote autonomo.
- Se definen las coordenadas $X$ e $Y$ relativas a la posicion del bote en la orilla.
- **Obtencion de referencias iniciales**: Los valores `yaw0`, `x0_ned` e `y0_ned` se determinan ejecutando primero el script `mavlink_nedread_threaded_test.py` con el bote ubicado en la bahia apuntando hacia el lago.
- **Permanencia**: Se puede modificar el parametro `UAV_DRIVE_INTERVAL` para variar el tiempo de posicion sostenida en un punto.
- Cambiar el modo del autopiloto a **`Offboard`** tras iniciar la ejecucion.

### 4. Verificacion de Comunicacion Serial (`serial_read.py` / `serial_write.py`)
Scripts disenados para validar la transmision de datos a traves de los modulos de telemetria.
- *Procedimiento*: Desconectar el modulo de telemetria del autopiloto y conectarlo directamente a la Raspberry Pi mediante un cable USB.
