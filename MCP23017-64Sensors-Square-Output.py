# ========================================================================
#
# 🔸 M C P 2 3 0 1 7  -  6 4  D R V 5 0 3 2 F A - 6  S E N S O R S 🔸
#
# ========================================================================
#
# Archivo    : MCP23017-64xDRV5032FA.py
# Autor      : Klaus Michalsky
# Fecha      : Sep-2026
#
# DESCRIPCION
# ------------------------------------------------------------------------
# - Lee 64 sensores Hall DRV5032FA-6 mediante 4 MCP23017.
# - Detecta cambios de estado en las 64 casillas.
# - Muestra el estado del tablero.
# - Detecta movimientos ORIGEN -> DESTINO.
# - Envía el movimiento al RP2040 mediante UART.
#
# Ejemplo:
#
#       E2 -> E4
#
# UART:
#
#       E2E4\n
#
# ========================================================================


from machine import Pin, I2C, UART
import time


# ========================================================================
# CONFIGURACION I2C
# ========================================================================

i2c = I2C(
    0,
    sda=Pin(16),
    scl=Pin(17),
    freq=100000
)


# ========================================================================
# CONFIGURACION UART
# ========================================================================
#
# IMPORTANTE:
# UART1 y los pines TX/RX deben coincidir con tu cableado hacia el RP2040.
#
# Si en tu montaje utilizas otros pines, cambia solamente TX_PIN y RX_PIN.
#
# ========================================================================

UART_ID = 1
UART_BAUD = 115200

TX_PIN = 4
RX_PIN = 5

uart = UART(
    UART_ID,
    baudrate=UART_BAUD,
    tx=Pin(TX_PIN),
    rx=Pin(RX_PIN)
)


# ========================================================================
# DIRECCIONES MCP23017
# ========================================================================

MCP_BOARD_1 = 0x20
MCP_BOARD_2 = 0x21
MCP_BOARD_3 = 0x22
MCP_BOARD_4 = 0x23

MCP_BOARDS = [
    MCP_BOARD_1,
    MCP_BOARD_2,
    MCP_BOARD_3,
    MCP_BOARD_4
]


# ========================================================================
# REGISTROS MCP23017
# ========================================================================

IODIRA = 0x00
IODIRB = 0x01

GPIOA = 0x12
GPIOB = 0x13


# ========================================================================
# MAPEO DE SENSORES -> CASILLAS
# ========================================================================
#
# ATENCION:
#
# El código original solamente define:
#
# PLACA 1 -> DRV0  - DRV15
# PLACA 2 -> DRV16 - DRV31
# PLACA 3 -> DRV32 - DRV47
# PLACA 4 -> DRV48 - DRV63
#
# Pero no define todavía qué DRV corresponde físicamente a cada casilla.
#
# Por eso aquí dejamos el mapa separado del resto del programa.
#
# Esta versión asume temporalmente:
#
# PLACA 1 = A1-D4
# PLACA 2 = E1-H4
# PLACA 3 = A5-D8
# PLACA 4 = E5-H8
#
# Y dentro de cada placa:
#
# DRV0  -> primera casilla
# DRV1  -> segunda
# ...
# DRV15 -> última
#
# Si tus PCB están orientadas de otra manera, SOLO cambia esta sección.
#
# ========================================================================


BOARD_SQUARES = [

    # PLACA 1 -> 0x20
    [
        "A1", "B1", "C1", "D1",
        "A2", "B2", "C2", "D2",
        "A3", "B3", "C3", "D3",
        "A4", "B4", "C4", "D4"
    ],

    # PLACA 2 -> 0x21
    [
        "E1", "F1", "G1", "H1",
        "E2", "F2", "G2", "H2",
        "E3", "F3", "G3", "H3",
        "E4", "F4", "G4", "H4"
    ],

    # PLACA 3 -> 0x22
    [
        "H8", "G8", "F8", "E8",
        "H7", "G7", "F7", "E7",
        "H6", "G6", "F6", "E6",
        "H5", "G5", "F5", "E5"
    ],

    # PLACA 4 -> 0x23
    [
        "D8", "C8", "B8", "A8",
        "D7", "C7", "B7", "A7",
        "D6", "C6", "B6", "A6",
        "D5", "C5", "B5", "A5"
    ]
]


# ========================================================================
# CONSTRUIR MAPA SENSOR -> CASILLA
# ========================================================================

SENSOR_TO_SQUARE = {}

for board_index in range(4):

    for sensor in range(16):

        sensor_number = board_index * 16 + sensor

        SENSOR_TO_SQUARE[sensor_number] = \
            BOARD_SQUARES[board_index][sensor]


# ========================================================================
# ESCANEO I2C
# ========================================================================

devices = i2c.scan()

print("")
print("========================================")
print("           DISPOSITIVOS I2C")
print("========================================")
print("Encontrados:", [hex(d) for d in devices])
print("")


for board_number, address in enumerate(MCP_BOARDS, start=1):

    if address not in devices:

        print(
            "ERROR: MCP23017 PLACA {} ({}) no encontrado".format(
                board_number,
                hex(address)
            )
        )

        while True:
            time.sleep(1)

    print(
        "OK: PLACA {} encontrada en {}".format(
            board_number,
            hex(address)
        )
    )


# ========================================================================
# CONFIGURAR LOS 16 GPIO DE CADA MCP COMO ENTRADAS
# ========================================================================

for address in MCP_BOARDS:

    i2c.writeto_mem(
        address,
        IODIRA,
        bytes([0b11111111])
    )

    i2c.writeto_mem(
        address,
        IODIRB,
        bytes([0b11111111])
    )


# ========================================================================
# INFORMACION
# ========================================================================

print("")
print("========================================")
print("       ONYX-PRO CHESSBOARD")
print("========================================")
print("")

print("PLACA 1 -> 0x20 -> DRV0  - DRV15")
print("PLACA 2 -> 0x21 -> DRV16 - DRV31")
print("PLACA 3 -> 0x22 -> DRV32 - DRV47")
print("PLACA 4 -> 0x23 -> DRV48 - DRV63")

print("")

print("HIGH = SIN IMAN")
print("LOW  = IMAN DETECTADO")

print("")

print("UART -> RP2040")
print("BAUD -> {}".format(UART_BAUD))

print("")
print("========================================")


# ========================================================================
# ESTADO DEL TABLERO
# ========================================================================
#
# True  = hay pieza
# False = casilla vacia
#
# DRV:
#
# HIGH = sin iman
# LOW  = iman
#
# Por tanto:
#
# HIGH -> casilla VACIA
# LOW  -> casilla OCUPADA
#
# ========================================================================

board_state = [False] * 64


# ========================================================================
# ESTADO ANTERIOR DE LOS MCP
# ========================================================================

previous_a = [
    0xFF,
    0xFF,
    0xFF,
    0xFF
]

previous_b = [
    0xFF,
    0xFF,
    0xFF,
    0xFF
]


# ========================================================================
# CONTADOR DE ERRORES I2C
# ========================================================================

i2c_errors = [
    0,
    0,
    0,
    0
]


# ========================================================================
# MOVIMIENTO
# ========================================================================
#
# Cuando una pieza se mueve:
#
# 1. La casilla ORIGEN pasa de OCUPADA -> VACIA
#
#       E2
#
# 2. La casilla DESTINO pasa de VACIA -> OCUPADA
#
#       E4
#
# Entonces:
#
#       E2 -> E4
#
# Se envía:
#
#       E2E4\n
#
# ========================================================================

move_from = None
move_to = None


# ========================================================================
# TIEMPO MINIMO ENTRE MOVIMIENTOS
# ========================================================================

last_move_time = 0

MOVE_DELAY_MS = 150


# ========================================================================
# FUNCION: MOSTRAR TABLERO
# ========================================================================

def print_board():

    print("")
    print("========================================")
    print("              ESTADO TABLERO")
    print("========================================")

    for rank in range(7, -1, -1):

        line = "{}  ".format(rank + 1)

        for file in range(8):

            index = rank * 8 + file

            if board_state[index]:

                line += "● "

            else:

                line += ". "

        print(line)

    print("")
    print("   A B C D E F G H")
    print("")


# ========================================================================
# FUNCION: OBTENER INDICE DE CASILLA
# ========================================================================

def square_to_index(square):

    file = ord(square[0]) - ord("A")

    rank = int(square[1]) - 1

    return rank * 8 + file


# ========================================================================
# FUNCION: ACTUALIZAR CASILLA
# ========================================================================

def update_square(sensor_number, occupied):

    global move_from
    global move_to
    global last_move_time

    square = SENSOR_TO_SQUARE[sensor_number]

    index = square_to_index(square)

    old_state = board_state[index]

    if old_state == occupied:

        return

    board_state[index] = occupied

    # ================================================================
    # MOSTRAR CAMBIO
    # ================================================================

    if occupied:

        print(
            "CASILLA {} -> OCUPADA | DRV{}".format(
                square,
                sensor_number
            )
        )

    else:

        print(
            "CASILLA {} -> VACIA | DRV{}".format(
                square,
                sensor_number
            )
        )

    # ================================================================
    # PIEZA RETIRADA
    # ================================================================

    if not occupied:

        move_from = square

        print(
            "ORIGEN DETECTADO -> {}".format(
                move_from
            )
        )

    # ================================================================
    # PIEZA COLOCADA
    # ================================================================

    else:

        move_to = square

        print(
            "DESTINO DETECTADO -> {}".format(
                move_to
            )
        )

    # ================================================================
    # MOVIMIENTO COMPLETO
    # ================================================================

    if move_from is not None and move_to is not None:

        now = time.ticks_ms()

        elapsed = time.ticks_diff(
            now,
            last_move_time
        )

        if elapsed >= MOVE_DELAY_MS:

            move = move_from + move_to

            print("")
            print("********************************")
            print("MOVIMIENTO: {} -> {}".format(
                move_from,
                move_to
            ))

            print("UART -> {}".format(move))

            # --------------------------------------------------------
            # ENVIAR AL RP2040
            # --------------------------------------------------------

            uart.write(
                move + "\n"
            )

            print("********************************")
            print("")

            last_move_time = now

        move_from = None
        move_to = None

        print_board()


# ========================================================================
# INICIALIZAR ESTADO DEL TABLERO
# ========================================================================
#
# Hacemos una primera lectura para saber qué casillas están ocupadas.
#
# ========================================================================

print("")
print("Inicializando estado del tablero...")
print("")


for board_index, address in enumerate(MCP_BOARDS):

    try:

        value_a = i2c.readfrom_mem(
            address,
            GPIOA,
            1
        )[0]

        value_b = i2c.readfrom_mem(
            address,
            GPIOB,
            1
        )[0]

    except OSError as e:

        print(
            "ERROR I2C durante inicializacion -> PLACA {} ({}) -> {}".format(
                board_index + 1,
                hex(address),
                e
            )
        )

        continue

    sensor_base = board_index * 16

    # ================================================================
    # GPIOA
    # ================================================================

    for sensor in range(8):

        mask = 1 << sensor

        current = value_a & mask

        sensor_number = sensor_base + sensor

        occupied = not bool(current)

        board_state[
            square_to_index(
                SENSOR_TO_SQUARE[sensor_number]
            )
        ] = occupied

    # ================================================================
    # GPIOB
    # ================================================================

    for sensor in range(8):

        mask = 1 << sensor

        current = value_b & mask

        sensor_number = sensor_base + 8 + sensor

        occupied = not bool(current)

        board_state[
            square_to_index(
                SENSOR_TO_SQUARE[sensor_number]
            )
        ] = occupied

    previous_a[board_index] = value_a
    previous_b[board_index] = value_b


# ========================================================================
# MOSTRAR TABLERO INICIAL
# ========================================================================

print_board()

print("========================================")
print("      SISTEMA LISTO")
print("========================================")
print("")


# ========================================================================
# LOOP PRINCIPAL
# ========================================================================

while True:

    for board_index, address in enumerate(MCP_BOARDS):

        # ================================================================
        # LECTURA I2C PROTEGIDA
        # ================================================================

        try:

            value_a = i2c.readfrom_mem(
                address,
                GPIOA,
                1
            )[0]

            value_b = i2c.readfrom_mem(
                address,
                GPIOB,
                1
            )[0]

        except OSError as e:

            i2c_errors[board_index] += 1

            print(
                "⚠️ ERROR I2C -> PLACA {} ({}) -> {} | ERRORES: {}".format(
                    board_index + 1,
                    hex(address),
                    e,
                    i2c_errors[board_index]
                )
            )

            time.sleep(0.01)

            continue

        # ================================================================
        # BASE DE SENSORES
        # ================================================================

        sensor_base = board_index * 16

        # ================================================================
        # GPIOA -> DRV0-DRV7
        # ================================================================

        for sensor in range(8):

            mask = 1 << sensor

            current = value_a & mask

            previous = previous_a[board_index] & mask

            if current != previous:

                sensor_number = sensor_base + sensor

                occupied = not bool(current)

                update_square(
                    sensor_number,
                    occupied
                )

        # ================================================================
        # GPIOB -> DRV8-DRV15
        # ================================================================

        for sensor in range(8):

            mask = 1 << sensor

            current = value_b & mask

            previous = previous_b[board_index] & mask

            if current != previous:

                sensor_number = sensor_base + 8 + sensor

                occupied = not bool(current)

                update_square(
                    sensor_number,
                    occupied
                )

        # ================================================================
        # GUARDAR ESTADO MCP
        # ================================================================

        previous_a[board_index] = value_a
        previous_b[board_index] = value_b

    # ====================================================================
    # PEQUEÑA PAUSA
    # ====================================================================

    time.sleep(0.02)
