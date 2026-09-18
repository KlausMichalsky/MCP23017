
# ========================================================================
# 🔸 M C P 2 3 0 1 7  -  1 6   D R V 5 0 3 2 F A - 6   S E N S O R S 🔸
# ========================================================================
#
#  Archivo    : MCP23017-16xDRV5032FA.py
#  Autor      : Klaus Michalsky
#  Fecha      : Aug-2026
#
#  DESCRIPCION
#  -----------------------------------------------------------------------
#  - Lee 16 sensores Hall DRV5032FA-6 mediante un MCP23017.
#  - Los 16 GPIO del MCP23017 están configurados como ENTRADAS.
#  - Cada GPIO corresponde a un sensor DRV5032FA-6.
#
#  MAPEO
#  -----------------------------------------------------------------------
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
#  LOGICA DRV5032FA
#  -----------------------------------------------------------------------
#  HIGH = sin imán
#  LOW  = imán detectado
#
#  Los LEDs están conectados directamente a la salida de cada DRV5032FA
#  mediante una resistencia hacia 3.3 V.
#
#  Por lo tanto:
#
#  Sin imán  → DRV HIGH → LED OFF
#  Con imán  → DRV LOW  → LED ON
#
#  HARDWARE
#  -----------------------------------------------------------------------
#  MCU       : Raspberry Pi Pico
#  I/O       : MCP23017
#  I2C       : I2C0
#  SDA       : GP16 (Pin 21)
#  SCL       : GP17 (Pin 22)
#
#  MCP23017 : 0x20
#
#  ESTADO
#  -----------------------------------------------------------------------
#  ✅ 16 sensores configurados
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
# DIRECCION I2C DEL MCP23017
# ========================================================================

MCP23017 = 0x20


# ========================================================================
# COMPROBAR DISPOSITIVOS I2C
# ========================================================================

devices = i2c.scan()

print("Dispositivos I2C:", [hex(d) for d in devices])

if MCP23017 not in devices:

    print("ERROR: MCP23017 no encontrado")

    while True:
        time.sleep(1)


print("MCP23017 encontrado en 0x20")


# ========================================================================
# REGISTROS MCP23017
# ========================================================================

IODIRA = 0x00
IODIRB = 0x01

GPIOA = 0x12
GPIOB = 0x13


# ========================================================================
# CONFIGURAR LOS 16 GPIO COMO ENTRADAS
# ========================================================================

# ------------------------------------------------------------------------
# PORT A
#
# GPA7 GPA6 GPA5 GPA4 GPA3 GPA2 GPA1 GPA0
#   1    1    1    1    1    1    1    1
#
# GPA0 → DRV0
# GPA1 → DRV1
# ...
# GPA7 → DRV7
# ------------------------------------------------------------------------

i2c.writeto_mem(
    MCP23017,
    IODIRA,
    bytes([0b11111111])
)


# ------------------------------------------------------------------------
# PORT B
#
# GPB7 GPB6 GPB5 GPB4 GPB3 GPB2 GPB1 GPB0
#   1    1    1    1    1    1    1    1
#
# GPB0 → DRV8
# GPB1 → DRV9
# ...
# GPB7 → DRV15
# ------------------------------------------------------------------------

i2c.writeto_mem(
    MCP23017,
    IODIRB,
    bytes([0b11111111])
)


print("")
print("========================================")
print(" MCP23017 - 16 DRV5032FA-6")
print("========================================")
print("")
print("GPA0 → DRV0")
print("GPA1 → DRV1")
print("GPA2 → DRV2")
print("GPA3 → DRV3")
print("GPA4 → DRV4")
print("GPA5 → DRV5")
print("GPA6 → DRV6")
print("GPA7 → DRV7")
print("")
print("GPB0 → DRV8")
print("GPB1 → DRV9")
print("GPB2 → DRV10")
print("GPB3 → DRV11")
print("GPB4 → DRV12")
print("GPB5 → DRV13")
print("GPB6 → DRV14")
print("GPB7 → DRV15")
print("")
print("HIGH = sin iman")
print("LOW  = iman detectado")
print("========================================")
print("")


# ========================================================================
# ESTADO ANTERIOR
# ========================================================================
#
# Guardamos el estado anterior para imprimir solamente cuando un sensor
# cambia de estado. Esto evita llenar el terminal con mensajes repetidos.
# ========================================================================

previous_a = 0xFF
previous_b = 0xFF


# ========================================================================
# BUCLE PRINCIPAL
# ========================================================================

while True:

    # --------------------------------------------------------------------
    # LEER LOS 16 SENSORES
    # --------------------------------------------------------------------

    value_a = i2c.readfrom_mem(
        MCP23017,
        GPIOA,
        1
    )[0]

    value_b = i2c.readfrom_mem(
        MCP23017,
        GPIOB,
        1
    )[0]

    # ====================================================================
    # PORT A → DRV0 ... DRV7
    # ====================================================================

    for sensor in range(8):

        mask = 1 << sensor

        current = value_a & mask
        previous = previous_a & mask

        # ---------------------------------------------------------------
        # SENSOR CAMBIO DE ESTADO
        # ---------------------------------------------------------------

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
    # PORT B → DRV8 ... DRV15
    # ====================================================================

    for sensor in range(8):

        mask = 1 << sensor

        current = value_b & mask
        previous = previous_b & mask

        # ---------------------------------------------------------------
        # SENSOR CAMBIO DE ESTADO
        # ---------------------------------------------------------------

        if current != previous:

            sensor_number = sensor + 8

            if current:
                print(
                    "DRV{} → HIGH | SIN IMAN | LED OFF".format(sensor_number)
                )

            else:
                print(
                    "DRV{} → LOW  | IMAN DETECTADO | LED ON".format(
                        sensor_number)
                )

    # --------------------------------------------------------------------
    # GUARDAR ESTADO ACTUAL
    # --------------------------------------------------------------------

    previous_a = value_a
    previous_b = value_b

    # --------------------------------------------------------------------
    # PEQUEÑA PAUSA
    # --------------------------------------------------------------------

    time.sleep(0.05)
