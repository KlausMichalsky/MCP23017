# ========================================================================
# 🔸 M C P 2 3 0 1 7  -  3 2   D R V 5 0 3 2 F A - 6   S E N S O R S 🔸
# ========================================================================
#
#  Archivo    : MCP23017-32xDRV5032FA.py
#  Autor      : Klaus Michalsky
#  Fecha      : Sep-2026
#
#  DESCRIPCIONa
#  -----------------------------------------------------------------------
#  - Lee 32 sensores Hall DRV5032FA-6 mediante 2 MCP23017.
#  - Cada placa contiene:
#
#       1x MCP23017
#       16x DRV5032FA-6
#
#  - Las dos placas comparten el mismo bus I2C.
#  - Cada MCP23017 tiene una dirección diferente mediante A0/A1/A2.
#
#  PLACA 1
#  -----------------------------------------------------------------------
#  MCP23017 = 0x20
#
#  GPA0 → DRV0
#  GPA1 → DRV1
#  GPA2 → DRV2
#  GPA3 → DRV3
#  GPA4 → DRV4
#  GPA5 → DRV5
#  GPA6 → DRV6
#  GPA7 → DRV7
#
#  GPB0 → DRV8
#  GPB1 → DRV9
#  GPB2 → DRV10
#  GPB3 → DRV11
#  GPB4 → DRV12
#  GPB5 → DRV13
#  GPB6 → DRV14
#  GPB7 → DRV15
#
#
#  PLACA 2
#  -----------------------------------------------------------------------
#  MCP23017 = 0x21
#
#  GPA0 → DRV16
#  GPA1 → DRV17
#  GPA2 → DRV18
#  GPA3 → DRV19
#  GPA4 → DRV20
#  GPA5 → DRV21
#  GPA6 → DRV22
#  GPA7 → DRV23
#
#  GPB0 → DRV24
#  GPB1 → DRV25
#  GPB2 → DRV26
#  GPB3 → DRV27
#  GPB4 → DRV28
#  GPB5 → DRV29
#  GPB6 → DRV30
#  GPB7 → DRV31
#
#
#  LOGICA DRV5032FA
#  -----------------------------------------------------------------------
#  HIGH = sin imán
#  LOW  = imán detectado
#
#  LED conectado desde la salida del DRV hacia 3.3 V:
#
#  Sin imán  → HIGH → LED OFF
#  Con imán  → LOW  → LED ON
#
#
#  CONEXION ENTRE PLACAS
#  -----------------------------------------------------------------------
#  VCC
#  GND
#  SDA
#  SCL
#  INT1
#  INT2
#  INT3
#  INT4
#
#  En esta versión los INT todavía NO se utilizan.
#
#
#  HARDWARE
#  -----------------------------------------------------------------------
#  MCU       : Raspberry Pi Pico
#  I2C       : I2C0
#  SDA       : GP16 (Pin 21)
#  SCL       : GP17 (Pin 22)
#
#  PLACA 1   : MCP23017 0x20
#  PLACA 2   : MCP23017 0x21
#
# ========================================================================


from machine import Pin, I2C
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
# DIRECCIONES DE LOS DOS MCP23017
# ========================================================================

MCP_BOARD_1 = 0x20
MCP_BOARD_2 = 0x21


# ========================================================================
# REGISTROS MCP23017
# ========================================================================

IODIRA = 0x00
IODIRB = 0x01

GPIOA = 0x12
GPIOB = 0x13


# ========================================================================
# COMPROBAR DISPOSITIVOS I2C
# ========================================================================

devices = i2c.scan()

print("")
print("========================================")
print(" DISPOSITIVOS I2C")
print("========================================")

print(
    "Encontrados:",
    [hex(d) for d in devices]
)

print("")


# ------------------------------------------------------------------------
# COMPROBAR PLACA 1
# ------------------------------------------------------------------------

if MCP_BOARD_1 not in devices:

    print("ERROR: MCP23017 PLACA 1 (0x20) no encontrado")

    while True:
        time.sleep(1)


print("OK: PLACA 1 encontrada en 0x20")


# ------------------------------------------------------------------------
# COMPROBAR PLACA 2
# ------------------------------------------------------------------------

if MCP_BOARD_2 not in devices:

    print("ERROR: MCP23017 PLACA 2 (0x21) no encontrado")

    while True:
        time.sleep(1)


print("OK: PLACA 2 encontrada en 0x21")


# ========================================================================
# CONFIGURAR LOS DOS MCP23017
# ========================================================================
#
# Los 16 GPIO de cada MCP son ENTRADAS.
#
# IODIR = 1 → INPUT
#
# ========================================================================


# ------------------------------------------------------------------------
# PLACA 1
# ------------------------------------------------------------------------

i2c.writeto_mem(
    MCP_BOARD_1,
    IODIRA,
    bytes([0b11111111])
)

i2c.writeto_mem(
    MCP_BOARD_1,
    IODIRB,
    bytes([0b11111111])
)


# ------------------------------------------------------------------------
# PLACA 2
# ------------------------------------------------------------------------

i2c.writeto_mem(
    MCP_BOARD_2,
    IODIRA,
    bytes([0b11111111])
)

i2c.writeto_mem(
    MCP_BOARD_2,
    IODIRB,
    bytes([0b11111111])
)


# ========================================================================
# INFORMACION
# ========================================================================

print("")
print("========================================")
print(" MCP23017 - 32 DRV5032FA-6")
print("========================================")
print("")

print("PLACA 1 → MCP 0x20 → DRV0  - DRV15")
print("PLACA 2 → MCP 0x21 → DRV16 - DRV31")

print("")

print("PLACA 1")
print("GPA0 → DRV0")
print("GPA1 → DRV1")
print("GPA2 → DRV2")
print("GPA3 → DRV3")
print("GPA4 → DRV4")
print("GPA5 → DRV5")
print("GPA6 → DRV6")
print("GPA7 → DRV7")

print("GPB0 → DRV8")
print("GPB1 → DRV9")
print("GPB2 → DRV10")
print("GPB3 → DRV11")
print("GPB4 → DRV12")
print("GPB5 → DRV13")
print("GPB6 → DRV14")
print("GPB7 → DRV15")

print("")

print("PLACA 2")
print("GPA0 → DRV16")
print("GPA1 → DRV17")
print("GPA2 → DRV18")
print("GPA3 → DRV19")
print("GPA4 → DRV20")
print("GPA5 → DRV21")
print("GPA6 → DRV22")
print("GPA7 → DRV23")

print("GPB0 → DRV24")
print("GPB1 → DRV25")
print("GPB2 → DRV26")
print("GPB3 → DRV27")
print("GPB4 → DRV28")
print("GPB5 → DRV29")
print("GPB6 → DRV30")
print("GPB7 → DRV31")

print("")

print("HIGH = SIN IMAN")
print("LOW  = IMAN DETECTADO")

print("")
print("========================================")
print("")


# ========================================================================
# ESTADOS ANTERIORES
# ========================================================================
#
# 0xFF = todos HIGH inicialmente.
#
# Esto evita imprimir los 32 sensores continuamente.
# Solo se imprime cuando cambia un sensor.
# ========================================================================

previous_board_1_a = 0xFF
previous_board_1_b = 0xFF

previous_board_2_a = 0xFF
previous_board_2_b = 0xFF


# ========================================================================
# BUCLE PRINCIPAL
# ========================================================================

while True:

    # ====================================================================
    # LEER PLACA 1
    # ====================================================================

    board_1_a = i2c.readfrom_mem(
        MCP_BOARD_1,
        GPIOA,
        1
    )[0]

    board_1_b = i2c.readfrom_mem(
        MCP_BOARD_1,
        GPIOB,
        1
    )[0]

    # ====================================================================
    # LEER PLACA 2
    # ====================================================================

    board_2_a = i2c.readfrom_mem(
        MCP_BOARD_2,
        GPIOA,
        1
    )[0]

    board_2_b = i2c.readfrom_mem(
        MCP_BOARD_2,
        GPIOB,
        1
    )[0]

    # ====================================================================
    # PLACA 1 → DRV0 ... DRV7
    # ====================================================================

    for sensor in range(8):

        mask = 1 << sensor

        current = board_1_a & mask
        previous = previous_board_1_a & mask

        if current != previous:

            if current:

                print(
                    "DRV{} → HIGH | SIN IMAN | LED OFF".format(sensor)
                )

            else:

                print(
                    "DRV{} → LOW  | IMAN DETECTADO | LED ON".format(sensor)
                )

    # ====================================================================
    # PLACA 1 → DRV8 ... DRV15
    # ====================================================================

    for sensor in range(8):

        mask = 1 << sensor

        current = board_1_b & mask
        previous = previous_board_1_b & mask

        if current != previous:

            sensor_number = sensor + 8

            if current:

                print(
                    "DRV{} → HIGH | SIN IMAN | LED OFF".format(
                        sensor_number
                    )
                )

            else:

                print(
                    "DRV{} → LOW  | IMAN DETECTADO | LED ON".format(
                        sensor_number
                    )
                )

    # ====================================================================
    # PLACA 2 → DRV16 ... DRV23
    # ====================================================================

    for sensor in range(8):

        mask = 1 << sensor

        current = board_2_a & mask
        previous = previous_board_2_a & mask

        if current != previous:

            sensor_number = sensor + 16

            if current:

                print(
                    "DRV{} → HIGH | SIN IMAN | LED OFF".format(
                        sensor_number
                    )
                )

            else:

                print(
                    "DRV{} → LOW  | IMAN DETECTADO | LED ON".format(
                        sensor_number
                    )
                )

    # ====================================================================
    # PLACA 2 → DRV24 ... DRV31
    # ====================================================================

    for sensor in range(8):

        mask = 1 << sensor

        current = board_2_b & mask
        previous = previous_board_2_b & mask

        if current != previous:

            sensor_number = sensor + 24

            if current:

                print(
                    "DRV{} → HIGH | SIN IMAN | LED OFF".format(
                        sensor_number
                    )
                )

            else:

                print(
                    "DRV{} → LOW  | IMAN DETECTADO | LED ON".format(
                        sensor_number
                    )
                )

    # ====================================================================
    # GUARDAR ESTADOS
    # ====================================================================

    previous_board_1_a = board_1_a
    previous_board_1_b = board_1_b

    previous_board_2_a = board_2_a
    previous_board_2_b = board_2_b

    # ====================================================================
    # PEQUEÑA PAUSA
    # ====================================================================

    time.sleep(0.05)
