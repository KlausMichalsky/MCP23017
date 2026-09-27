from machine import Pin, I2C, UART
import time


# ============================================================
# 🔹 ONYX-PRO — CHESSBOARD SENSOR CONTROLLER
# ============================================================
# Raspberry Pi Pico / MicroPython
#
# I2C:
#   SDA = GPIO 16
#   SCL = GPIO 17
#
# MCP23017:
#   Board 1 = 0x20
#   Board 2 = 0x21
#   Board 3 = 0x22
#   Board 4 = 0x23
#
# UART:
#   TX = GPIO 4
#   RX = GPIO 5
#   UART1 @ 115200
#
# Confirm Button:
#   GPIO 15 -> GND
#   Internal PULL_UP
#
# Hall sensor:
#   HIGH = EMPTY
#   LOW  = PIECE PRESENT
# ============================================================


# ============================================================
# I2C
# ============================================================

i2c = I2C(
    0,
    sda=Pin(16),
    scl=Pin(17),
    freq=100000
)


# ============================================================
# UART -> RP2040
# ============================================================

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


# ============================================================
# CONFIRM BUTTON
# ============================================================

BUTTON_PIN = 15

button = Pin(
    BUTTON_PIN,
    Pin.IN,
    Pin.PULL_UP
)


# ============================================================
# MCP23017 ADDRESSES
# ============================================================

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


# ============================================================
# MCP23017 REGISTERS
# ============================================================

IODIRA = 0x00
IODIRB = 0x01

GPIOA = 0x12
GPIOB = 0x13


# ============================================================
# PHYSICAL BOARD MAPPING
# ============================================================

BOARD_SQUARES = [

    # --------------------------------------------------------
    # BOARD 1 -> 0x20
    # --------------------------------------------------------
    [
        "A1", "B1", "C1", "D1",
        "A2", "B2", "C2", "D2",
        "A3", "B3", "C3", "D3",
        "A4", "B4", "C4", "D4"
    ],

    # --------------------------------------------------------
    # BOARD 2 -> 0x21
    # --------------------------------------------------------
    [
        "E1", "F1", "G1", "H1",
        "E2", "F2", "G2", "H2",
        "E3", "F3", "G3", "H3",
        "E4", "F4", "G4", "H4"
    ],

    # --------------------------------------------------------
    # BOARD 3 -> 0x22
    # --------------------------------------------------------
    [
        "H8", "G8", "F8", "E8",
        "H7", "G7", "F7", "E7",
        "H6", "G6", "F6", "E6",
        "H5", "G5", "F5", "E5"
    ],

    # --------------------------------------------------------
    # BOARD 4 -> 0x23
    # --------------------------------------------------------
    [
        "D8", "C8", "B8", "A8",
        "D7", "C7", "B7", "A7",
        "D6", "C6", "B6", "A6",
        "D5", "C5", "B5", "A5"
    ]
]


# ============================================================
# SENSOR -> CHESS SQUARE
# ============================================================

SENSOR_TO_SQUARE = {}

sensor_number = 0

for board in BOARD_SQUARES:
    for square in board:
        SENSOR_TO_SQUARE[sensor_number] = square
        sensor_number += 1


# ============================================================
# BOARD STATE
# ============================================================

# False = empty
# True  = occupied

board_state = [False] * 64


# ============================================================
# PREVIOUS MCP VALUES
# ============================================================

previous_a = [0xFF] * 4
previous_b = [0xFF] * 4


# ============================================================
# MOVEMENT STATE MACHINE
# ============================================================

# Original square of the moving piece
move_from = None

# Current destination candidate
move_to = None

# True after the original square has been detected
move_active = False


# ============================================================
# I2C HELPERS
# ============================================================

def write_register(address, register, value):

    i2c.writeto_mem(
        address,
        register,
        bytes([value])
    )


def read_register(address, register):

    data = i2c.readfrom_mem(
        address,
        register,
        1
    )

    return data[0]


# ============================================================
# CONFIGURE MCP23017
# ============================================================

def configure_mcp(address):

    # All GPIO as inputs
    write_register(address, IODIRA, 0xFF)
    write_register(address, IODIRB, 0xFF)


# ============================================================
# INITIAL BOARD READ
# ============================================================

def initialize_board():

    print()
    print("========================================")
    print(" INITIALIZING BOARD")
    print("========================================")

    for board_index, address in enumerate(MCP_BOARDS):

        value_a = read_register(address, GPIOA)
        value_b = read_register(address, GPIOB)

        base_sensor = board_index * 16

        # GPIOA -> sensors 0-7
        for bit in range(8):

            sensor = base_sensor + bit

            # LOW = magnet detected
            occupied = not bool(value_a & (1 << bit))

            board_state[sensor] = occupied

        # GPIOB -> sensors 8-15
        for bit in range(8):

            sensor = base_sensor + 8 + bit

            # LOW = magnet detected
            occupied = not bool(value_b & (1 << bit))

            board_state[sensor] = occupied

        previous_a[board_index] = value_a
        previous_b[board_index] = value_b

    print("Board initialized.")
    print()


# ============================================================
# PRINT BOARD
# ============================================================

def print_board():

    print()
    print("--------------- BOARD ----------------")

    for rank in range(7, -1, -1):

        row = ""

        for file_index in range(8):

            sensor = rank * 8 + file_index

            if board_state[sensor]:
                row += "X "
            else:
                row += ". "

        print("{} | {}".format(rank + 1, row))

    print("    A B C D E F G H")
    print("---------------------------------------")
    print()


# ============================================================
# SENSOR CHANGE HANDLER
# ============================================================

def update_square(sensor_number, occupied):

    global move_from
    global move_to
    global move_active

    square = SENSOR_TO_SQUARE[sensor_number]

    # --------------------------------------------------------
    # Update physical board state
    # --------------------------------------------------------

    board_state[sensor_number] = occupied

    # ========================================================
    # PIECE REMOVED
    # ========================================================

    if not occupied:

        print("EMPTY  -> {}".format(square))

        # ----------------------------------------------------
        # No movement currently active.
        #
        # The FIRST square that becomes empty is the origin.
        # ----------------------------------------------------

        if not move_active:

            move_from = square
            move_to = None
            move_active = True

            print()
            print("🔒 ORIGIN LOCKED -> {}".format(move_from))
            print("   Move the piece freely...")
            print()

        # ----------------------------------------------------
        # Movement already active.
        #
        # If the current destination becomes empty, the piece
        # has moved away from that candidate.
        #
        # IMPORTANT:
        # The origin NEVER changes here.
        # ----------------------------------------------------

        else:

            if square == move_to:

                print(
                    "DESTINATION LEFT -> {}".format(square)
                )

                move_to = None

    # ========================================================
    # PIECE DETECTED
    # ========================================================

    else:

        print("OCCUPIED -> {}".format(square))

        # ----------------------------------------------------
        # If movement is active, this square becomes the
        # current destination candidate.
        # ----------------------------------------------------

        if move_active:

            # Never allow the original square to become
            # the destination.
            if square != move_from:

                move_to = square

                print(
                    "🎯 DESTINATION CANDIDATE -> {}".format(
                        move_to
                    )
                )


# ============================================================
# BUTTON
# ============================================================

def button_pressed():

    # Button pressed = LOW
    if button.value() == 0:

        # Simple debounce
        time.sleep_ms(50)

        if button.value() == 0:

            return True

    return False


# ============================================================
# WAIT FOR BUTTON RELEASE
# ============================================================

def wait_button_release():

    while button.value() == 0:
        time.sleep_ms(10)


# ============================================================
# CONFIRM MOVEMENT
# ============================================================

def confirm_move():

    global move_from
    global move_to
    global move_active

    # --------------------------------------------------------
    # No active movement
    # --------------------------------------------------------

    if not move_active:

        print()
        print("⚠️  No movement detected.")
        print()

        return

    # --------------------------------------------------------
    # Origin exists, but destination does not
    # --------------------------------------------------------

    if move_from is None:

        print()
        print("⚠️  No origin.")
        print()

        return

    if move_to is None:

        print()
        print(
            "⚠️  Origin = {}".format(move_from)
        )
        print(
            "⚠️  Waiting for destination..."
        )
        print()

        return

    # ========================================================
    # FINAL MOVE
    # ========================================================

    move = move_from + move_to

    print()
    print("========================================")
    print("♟️  MOVE CONFIRMED")
    print("========================================")
    print("FROM : {}".format(move_from))
    print("TO   : {}".format(move_to))
    print("MOVE : {}".format(move))
    print("========================================")
    print()

    # --------------------------------------------------------
    # Send to RP2040
    # --------------------------------------------------------

    uart.write(move + "\n")

    print("UART -> {}".format(move))

    # ========================================================
    # RESET MOVEMENT STATE
    # ========================================================

    move_from = None
    move_to = None
    move_active = False

    print("Movement state reset.")
    print()

    print_board()


# ============================================================
# I2C SCAN
# ============================================================

print()
print("========================================")
print(" ONYX-PRO SENSOR CONTROLLER")
print("========================================")

print()
print("I2C scan:")

devices = i2c.scan()

for address in devices:

    print(
        "  Found: 0x{:02X}".format(address)
    )

print()


# ============================================================
# CHECK MCP BOARDS
# ============================================================

for address in MCP_BOARDS:

    if address in devices:

        print(
            "MCP23017 OK -> 0x{:02X}".format(address)
        )

        configure_mcp(address)

    else:

        print(
            "WARNING: MCP23017 NOT FOUND -> 0x{:02X}".format(
                address
            )
        )


print()


# ============================================================
# INITIAL BOARD STATE
# ============================================================

initialize_board()

print_board()


# ============================================================
# MAIN LOOP
# ============================================================

print("========================================")
print(" READY")
print("========================================")
print()
print("Move a piece.")
print("The first empty square becomes the origin.")
print("The latest occupied square becomes the destination.")
print("Press GPIO 15 button to confirm.")
print()


while True:

    # ========================================================
    # READ ALL FOUR MCP23017
    # ========================================================

    for board_index, address in enumerate(MCP_BOARDS):

        try:

            value_a = read_register(
                address,
                GPIOA
            )

            value_b = read_register(
                address,
                GPIOB
            )

        except Exception as e:

            print(
                "I2C ERROR on 0x{:02X}: {}".format(
                    address,
                    e
                )
            )

            continue

        base_sensor = board_index * 16

        # ====================================================
        # GPIO A
        # ====================================================

        changed_a = value_a ^ previous_a[board_index]

        if changed_a:

            for bit in range(8):

                if changed_a & (1 << bit):

                    sensor = base_sensor + bit

                    occupied = not bool(
                        value_a & (1 << bit)
                    )

                    update_square(
                        sensor,
                        occupied
                    )

        # ====================================================
        # GPIO B
        # ====================================================

        changed_b = value_b ^ previous_b[board_index]

        if changed_b:

            for bit in range(8):

                if changed_b & (1 << bit):

                    sensor = base_sensor + 8 + bit

                    occupied = not bool(
                        value_b & (1 << bit)
                    )

                    update_square(
                        sensor,
                        occupied
                    )

        # ====================================================
        # SAVE CURRENT VALUES
        # ====================================================

        previous_a[board_index] = value_a
        previous_b[board_index] = value_b

    # ========================================================
    # CHECK CONFIRM BUTTON
    # ========================================================

    if button_pressed():

        confirm_move()

        # Wait until user releases button
        wait_button_release()

    # ========================================================
    # SMALL LOOP DELAY
    # ========================================================

    time.sleep_ms(20)
