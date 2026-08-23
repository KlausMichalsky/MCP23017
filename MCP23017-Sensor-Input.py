# ========================================================================
#           🔸 M C P 2 3 0 1 7  -  S E N S O R   I N P U T  🔸
# ========================================================================
#  Archivo    : MCP23017-Sensor-Input.py
#  Autor      : Klaus Michalsky
#  Fecha      : Aug-2026
#
#  DESCRIPCION
#  -----------------------------------------------------------------------
#  - Prueba dos entradas digitales del MCP23017 mediante I2C.
#  - Utiliza un Raspberry Pi Pico con MicroPython.
#  - Detecta el MCP23017 en la dirección I2C 0x20.
#  - GPA6 se utiliza como entrada digital para el sensor 1.
#  - GPB1 se utiliza como entrada digital para el sensor 2.
#  - Los estados de ambos sensores se muestran continuamente
#    en la consola.
#
#  HARDWARE
#  -----------------------------------------------------------------------
#  MCU     : Raspberry Pi Pico
#  I/O     : MCP23017
#  SENSOR 1: GPA6
#  SENSOR 2: GPB1
#  I2C     : I2C0
#  SDA     : GP16 (Pin 21)
#  SCL     : GP17 (Pin 22)
#
#  ESTADO
#  -----------------------------------------------------------------------
#  ✅ Funcional
# ========================================================================


from machine import Pin, I2C
import time


# Configuración I2C
i2c = I2C(
    0,
    sda=Pin(16),
    scl=Pin(17),
    freq=100000
)


# Dirección I2C del MCP23017
MCP23017 = 0x20


# Comprobar dispositivos I2C
devices = i2c.scan()

print("Dispositivos I2C:", [hex(d) for d in devices])


if MCP23017 not in devices:
    print("ERROR: MCP23017 no encontrado")

    while True:
        time.sleep(1)


print("MCP23017 encontrado en 0x20")


# Registros MCP23017
IODIRA = 0x00
IODIRB = 0x01
GPIOA = 0x12
GPIOB = 0x13


# Configurar GPA6 como entrada
#
# GPA7 GPA6 GPA5 GPA4 GPA3 GPA2 GPA1 GPA0
#   0    1    0    0    0    0    0    0

i2c.writeto_mem(
    MCP23017,
    IODIRA,
    bytes([0b01000000])
)


# Configurar GPB1 como entrada
#
# GPB7 GPB6 GPB5 GPB4 GPB3 GPB2 GPB1 GPB0
#   0    0    0    0    0    0    1    0

i2c.writeto_mem(
    MCP23017,
    IODIRB,
    bytes([0b00000010])
)


print("GPA6 configurado como entrada")
print("GPB1 configurado como entrada")


# Leer ambos sensores continuamente

while True:

    # Leer PORT A
    value_a = i2c.readfrom_mem(
        MCP23017,
        GPIOA,
        1
    )[0]

    # Leer PORT B
    value_b = i2c.readfrom_mem(
        MCP23017,
        GPIOB,
        1
    )[0]

    # Sensor 1 - GPA6
    if value_a & 0b01000000:
        print("GPA6 = LOW")
    else:
        print("GPA6 = HIGH")

    # Sensor 2 - GPB1
    if value_b & 0b00000010:
        print("GPB1 = LOW")
    else:
        print("GPB1 = HIGH")

    print("--------------------")

    time.sleep(0.5)
