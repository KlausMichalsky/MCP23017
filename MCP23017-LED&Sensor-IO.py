# ========================================================================
# 🔸 M C P 2 3 0 1 7  -  L E D & S E N S O R   I N P U T  O U T P U T 🔸
# ========================================================================
#  Archivo    : MCP23017-LED&Sensor-IO.py
#  Autor      : Klaus Michalsky
#  Fecha      : Aug-2026
#
#  DESCRIPCION
#  -----------------------------------------------------------------------
#  - Prueba dos sensores digitales y dos LEDs mediante el MCP23017.
#  - GPA6 controla el LED conectado a GPA7.
#  - GPB1 controla el LED conectado a GPB0.
#  - Los sensores utilizan lógica invertida:
#      HIGH = sin imán
#      LOW  = imán detectado
#
#  HARDWARE
#  -----------------------------------------------------------------------
#  MCU      : Raspberry Pi Pico
#  I/O      : MCP23017
#  SENSOR 1: GPA6
#  LED 1   : GPA7
#  SENSOR 2: GPB1
#  LED 2   : GPB0
#  I2C      : I2C0
#  SDA      : GP16 (Pin 21)
#  SCL      : GP17 (Pin 22)
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


# ------------------------------------------------------------------------
# CONFIGURACIÓN DE ENTRADAS Y SALIDAS
# ------------------------------------------------------------------------

# PORT A
#
# GPA7 = salida → LED 1
# GPA6 = entrada → Sensor 1
#
# GPA7 GPA6 GPA5 GPA4 GPA3 GPA2 GPA1 GPA0
#   0    1    0    0    0    0    0    0

i2c.writeto_mem(
    MCP23017,
    IODIRA,
    bytes([0b01000000])
)


# PORT B
#
# GPB1 = entrada → Sensor 2
# GPB0 = salida  → LED 2
#
# GPB7 GPB6 GPB5 GPB4 GPB3 GPB2 GPB1 GPB0
#   0    0    0    0    0    0    1    0

i2c.writeto_mem(
    MCP23017,
    IODIRB,
    bytes([0b00000010])
)


print("GPA6 = SENSOR 1")
print("GPA7 = LED 1")

print("GPB1 = SENSOR 2")
print("GPB0 = LED 2")


# ------------------------------------------------------------------------
# BUCLE PRINCIPAL
# ------------------------------------------------------------------------

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

    # --------------------------------------------------------------------
    # SENSOR 1 → GPA6 → LED 1 → GPA7
    # --------------------------------------------------------------------

    if value_a & 0b01000000:
        # GPA6 = HIGH → sin imán (DRV5032 es High en reposo)
        # 🔴 Para APAGAR GPA7 → usamos AND
        # Queremos forzar GPA7 a 0.
        # AND + 0 → fuerza a 0
        # x AND 0 = 0
        # Para APAGAR GPA7 la mascara es 0b01111111
        # 01111111
        # ↑
        # AND

        value_a = value_a & 0b01111111

        print("GPA6 = HIGH | LED GPA7 = OFF")

    else:
        # GPA6 = LOW → imán detectado
        # 🟢 Para ENCENDER GPA7 → usamos OR
        # Queremos forzar GPA7 a 1
        # OR + 1 → fuerza a 1
        # x OR 1 = 1
        # Para ENCENDER GPA7 la mascara es 0b10000000
        # 10000000
        # ↑
        # OR

        value_a = value_a | 0b10000000

        print("GPA6 = LOW  | LED GPA7 = ON")

    # Escribir nuevo estado de PORT A
    i2c.writeto_mem(
        MCP23017,
        GPIOA,
        bytes([value_a])
    )

    # --------------------------------------------------------------------
    # SENSOR 2 → GPB1 → LED 2 → GPB0
    # --------------------------------------------------------------------

    if value_b & 0b00000010:
        # GPB1 = HIGH → sin imán
        # Apagar LED GPB0

        value_b = value_b & 0b11111110

        print("GPB1 = HIGH | LED GPB0 = OFF")

    else:
        # GPB1 = LOW → imán detectado
        # Encender LED GPB0

        value_b = value_b | 0b00000001

        print("GPB1 = LOW  | LED GPB0 = ON")

    # Escribir nuevo estado de PORT B
    i2c.writeto_mem(
        MCP23017,
        GPIOB,
        bytes([value_b])
    )

    print("--------------------")

    time.sleep(0.1)
