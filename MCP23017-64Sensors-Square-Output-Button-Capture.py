from machine import Pin, I2C, UART
import time


# ============================================================
#                    O N Y X - P R O
#              CHESSBOARD CONTROLLER
# ============================================================


# ============================================================
# CONFIGURACION I2C
# ============================================================

I2C_ID = 0
SDA_PIN = 16
SCL_PIN = 17
I2C_FREQ = 100000

i2c = I2C(
    I2C_ID,
    scl=Pin(SCL_PIN),
    sda=Pin(SDA_PIN),
    freq=I2C_FREQ
)


# ============================================================
# CONFIGURACION UART
# ============================================================

UART_ID = 1
UART_BAUD = 115200
UART_TX = 4
UART_RX = 5

uart = UART(
    UART_ID,
    baudrate=UART_BAUD,
    tx=Pin(UART_TX),
    rx=Pin(UART_RX)
)


# ============================================================
# BOTON DE CONFIRMACION
# ============================================================

BUTTON_PIN = 18

button = Pin(
    BUTTON_PIN,
    Pin.IN,
    Pin.PULL_UP
)


# ============================================================
# MCP23017
# ============================================================

MCP_ADDRESSES = [
    0x20,
    0x21,
    0x22,
    0x23
]

IODIRA = 0x00
IODIRB = 0x01

GPIOA = 0x12
GPIOB = 0x13


# ============================================================
# MAPEO FISICO DEL TABLERO
# ============================================================

BOARD_SQUARES = [

    # --------------------------------------------------------
    # PLACA 1 -> 0x20
    # --------------------------------------------------------

    [
        "A1", "B1", "C1", "D1",
        "A2", "B2", "C2", "D2",
        "A3", "B3", "C3", "D3",
        "A4", "B4", "C4", "D4"
    ],


    # --------------------------------------------------------
    # PLACA 2 -> 0x21
    # --------------------------------------------------------

    [
        "E1", "F1", "G1", "H1",
        "E2", "F2", "G2", "H2",
        "E3", "F3", "G3", "H3",
        "E4", "F4", "G4", "H4"
    ],


    # --------------------------------------------------------
    # PLACA 3 -> 0x22
    # --------------------------------------------------------

    [
        "H8", "G8", "F8", "E8",
        "H7", "G7", "F7", "E7",
        "H6", "G6", "F6", "E6",
        "H5", "G5", "F5", "E5"
    ],


    # --------------------------------------------------------
    # PLACA 4 -> 0x23
    # --------------------------------------------------------

    [
        "D8", "C8", "B8", "A8",
        "D7", "C7", "B7", "A7",
        "D6", "C6", "B6", "A6",
        "D5", "C5", "B5", "A5"
    ]
]


# ============================================================
# CLASE MCP23017
# ============================================================

class MCP23017:

    def __init__(self, i2c, address):

        self.i2c = i2c
        self.address = address

    def write_register(self, register, value):

        self.i2c.writeto_mem(
            self.address,
            register,
            bytes([value])
        )

    def read_register(self, register):

        return self.i2c.readfrom_mem(
            self.address,
            register,
            1
        )[0]

    def setup_inputs(self):

        self.write_register(
            IODIRA,
            0xFF
        )

        self.write_register(
            IODIRB,
            0xFF
        )

    def read_gpio(self):

        value_a = self.read_register(
            GPIOA
        )

        value_b = self.read_register(
            GPIOB
        )

        return value_a, value_b


# ============================================================
# INICIALIZAR MCP23017
# ============================================================

mcps = []

for address in MCP_ADDRESSES:

    mcp = MCP23017(
        i2c,
        address
    )

    mcp.setup_inputs()

    mcps.append(mcp)


# ============================================================
# ESTADO DEL TABLERO
# ============================================================

board_state = {}

for board in BOARD_SQUARES:

    for square in board:

        board_state[square] = False


# ============================================================
# LEER LOS 64 SENSORES
# ============================================================

def read_all_sensors():

    for board_index in range(4):

        value_a, value_b = mcps[board_index].read_gpio()

        squares = BOARD_SQUARES[board_index]

        # ----------------------------------------------------
        # GPIOA -> sensores 0-7
        # ----------------------------------------------------

        for bit in range(8):

            square = squares[bit]

            occupied = not bool(
                value_a & (1 << bit)
            )

            board_state[square] = occupied

        # ----------------------------------------------------
        # GPIOB -> sensores 8-15
        # ----------------------------------------------------

        for bit in range(8):

            square = squares[bit + 8]

            occupied = not bool(
                value_b & (1 << bit)
            )

            board_state[square] = occupied


# ============================================================
# MOSTRAR TABLERO
# ============================================================

def print_board():

    print()

    print(
        "--------------- BOARD ----------------"
    )

    for rank in range(8, 0, -1):

        line = str(rank) + " | "

        for file_index in range(8):

            file_letter = chr(
                ord("A") + file_index
            )

            square = (
                file_letter +
                str(rank)
            )

            if board_state[square]:

                line += "X "

            else:

                line += ". "

        print(line)

    print(
        "    A B C D E F G H"
    )

    print(
        "---------------------------------------"
    )

    print()


# ============================================================
# DEBUG BINARIO
# ============================================================

def byte_to_binary(value):

    result = ""

    for bit in range(7, -1, -1):

        if value & (1 << bit):

            result += "1"

        else:

            result += "0"

    return result


# ============================================================
# DEBUG DE LOS 64 SENSORES
# ============================================================

def debug_all_sensors():

    print()

    print(
        "================================================"
    )

    print(
        "             DEBUG 64 SENSORES"
    )

    print(
        "================================================"
    )

    for board_index in range(4):

        address = MCP_ADDRESSES[
            board_index
        ]

        value_a, value_b = mcps[
            board_index
        ].read_gpio()

        print()

        print(
            "PLACA",
            board_index + 1,
            "->",
            hex(address)
        )

        print(
            "GPIOA =",
            byte_to_binary(value_a),
            " HEX =",
            hex(value_a)
        )

        print(
            "GPIOB =",
            byte_to_binary(value_b),
            " HEX =",
            hex(value_b)
        )

        print()

        squares = BOARD_SQUARES[
            board_index
        ]

        for i in range(16):

            if i < 8:

                occupied = not bool(
                    value_a & (1 << i)
                )

            else:

                occupied = not bool(
                    value_b & (
                        1 << (i - 8)
                    )
                )

            sensor_number = (
                board_index * 16 + i
            )

            print(
                "DRV",
                sensor_number,
                "->",
                squares[i],
                "->",
                "X" if occupied else "."
            )

    print()

    print(
        "================================================"
    )

    print()


# ============================================================
# ESTADO INICIAL
# ============================================================

previous_state = {}

read_all_sensors()

for square in board_state:

    previous_state[square] = (
        board_state[square]
    )


# ============================================================
# VARIABLES DEL MOVIMIENTO
# ============================================================

move_from = None
move_to = None

move_active = False

pending_empty = None

capture_square = None


# ============================================================
# BLOQUEAR ORIGEN
# ============================================================

def lock_origin(square):

    global move_from
    global move_active

    move_from = square

    move_active = True

    print()

    print(
        "🔒 ORIGIN LOCKED ->",
        move_from
    )


# ============================================================
# PROCESAR CAMBIO DE SENSOR
# ============================================================

def update_square(square, occupied):

    global move_from
    global move_to
    global move_active
    global pending_empty
    global capture_square

    board_state[square] = occupied

    # ========================================================
    # PIEZA RETIRADA
    # ========================================================

    if not occupied:

        # ----------------------------------------------------
        # TODAVIA NO HAY MOVIMIENTO ACTIVO
        # ----------------------------------------------------

        if not move_active:

            if pending_empty is None:

                pending_empty = square

                print()

                print(
                    "⏳ EMPTY PENDING ->",
                    square
                )

            else:

                first_empty = pending_empty

                lock_origin(square)

                capture_square = first_empty

                print(
                    "⚔️ CAPTURE SEQUENCE DETECTED"
                )

                print(
                    "⚔️ CAPTURE SQUARE ->",
                    capture_square
                )

                pending_empty = None

        # ----------------------------------------------------
        # YA HAY MOVIMIENTO ACTIVO
        # ----------------------------------------------------

        else:

            # No modificar el origen
            if square == move_from:

                return

            # Se retira la pieza del destino
            if square == move_to:

                move_to = None

                print(
                    "↩️ DESTINATION CLEARED ->",
                    square
                )

                return

            # Detectar casilla de captura
            if capture_square is None:

                capture_square = square

                print(
                    "⚔️ CAPTURE CANDIDATE ->",
                    square
                )

    # ========================================================
    # PIEZA COLOCADA
    # ========================================================

    else:

        # ----------------------------------------------------
        # TODAVIA NO HAY MOVIMIENTO ACTIVO
        # ----------------------------------------------------

        if not move_active:

            if pending_empty is not None:

                origin = pending_empty

                pending_empty = None

                lock_origin(origin)

                move_to = square

                print(
                    "🎯 DESTINATION CANDIDATE ->",
                    move_to
                )

        # ----------------------------------------------------
        # YA HAY MOVIMIENTO ACTIVO
        # ----------------------------------------------------

        else:

            # No modificar el origen
            if square == move_from:

                return

            # Colocar pieza en casilla de captura
            if square == capture_square:

                move_to = square

                print()

                print(
                    "⚔️ CAPTURE DESTINATION ->",
                    move_to
                )

            else:

                move_to = square

                print()

                print(
                    "🎯 DESTINATION CANDIDATE ->",
                    move_to
                )


# ============================================================
# CONFIRMAR MOVIMIENTO
# ============================================================

def confirm_move():

    global move_from
    global move_to
    global move_active
    global pending_empty
    global capture_square
    global previous_state

    # ========================================================
    # VERIFICAR MOVIMIENTO COMPLETO
    # ========================================================

    if (
        move_active
        and move_from is not None
        and move_to is not None
    ):

        move = (
            move_from +
            move_to
        )

        print()

        print(
            "♟️ MOVE CONFIRMED"
        )

        print(
            "UART ->",
            move
        )

        # ----------------------------------------------------
        # ENVIAR MOVIMIENTO AL RP2040
        # ----------------------------------------------------

        uart.write(
            move + "\n"
        )

        # ----------------------------------------------------
        # RESET DEL ESTADO DEL MOVIMIENTO
        # ----------------------------------------------------

        move_from = None
        move_to = None

        move_active = False

        pending_empty = None

        capture_square = None

        # ====================================================
        # LEER NUEVAMENTE LOS 64 SENSORES
        # ====================================================

        read_all_sensors()

        # ====================================================
        # MOSTRAR NUEVA MATRIZ
        # ====================================================

        print()

        print(
            "------------- NEW BOARD --------------"
        )

        print_board()

        # ====================================================
        # NUEVO ESTADO FISICO =
        # NUEVO ESTADO BASE
        # ====================================================

        for square in board_state:

            previous_state[square] = (
                board_state[square]
            )

        print(
            "✅ READY FOR NEXT MOVE"
        )

    # ========================================================
    # BOTON PRESIONADO SIN MOVIMIENTO COMPLETO
    # ========================================================

    else:

        print()

        print(
            "⚠️ BUTTON PRESSED - "
            "NO COMPLETE MOVE"
        )


# ============================================================
# DETECTAR BOTON
# ============================================================

def button_pressed():

    if button.value() == 0:

        time.sleep_ms(50)

        if button.value() == 0:

            return True

    return False


# ============================================================
# ESPERAR LIBERACION DEL BOTON
# ============================================================

def wait_button_release():

    while button.value() == 0:

        time.sleep_ms(10)


# ============================================================
# STARTUP
# ============================================================

print()

print(
    "================================================"
)

print(
    "              O N Y X - P R O"
)

print(
    "          CHESSBOARD CONTROLLER"
)

print(
    "================================================"
)

print()


# ============================================================
# I2C SCAN
# ============================================================

print(
    "I2C SCAN:"
)

print(
    i2c.scan()
)

print()


# ============================================================
# COMPROBAR MCP23017
# ============================================================

for address in MCP_ADDRESSES:

    if address in i2c.scan():

        print(
            "✅ MCP23017 encontrado:",
            hex(address)
        )

    else:

        print(
            "❌ MCP23017 NO encontrado:",
            hex(address)
        )


# ============================================================
# LECTURA INICIAL
# ============================================================

read_all_sensors()


# ============================================================
# DEBUG INICIAL
# ============================================================

debug_all_sensors()


# ============================================================
# MOSTRAR TABLERO INICIAL
# ============================================================

print_board()


print(
    "🚀 SENSOR SYSTEM READY"
)

print()


# ============================================================
# LOOP PRINCIPAL
# ============================================================

while True:

    # --------------------------------------------------------
    # Leer todos los sensores
    # --------------------------------------------------------

    read_all_sensors()

    # --------------------------------------------------------
    # Detectar cambios
    # --------------------------------------------------------

    for square in board_state:

        current = board_state[square]

        previous = previous_state[square]

        if current != previous:

            print(
                "CHANGE:",
                square,
                "->",
                "X" if current else "."
            )

            update_square(
                square,
                current
            )

            previous_state[square] = current

    # --------------------------------------------------------
    # Comprobar boton de confirmacion
    # --------------------------------------------------------

    if button_pressed():

        confirm_move()

        wait_button_release()

    # --------------------------------------------------------
    # Pequeña pausa
    # --------------------------------------------------------

    time.sleep_ms(20)
