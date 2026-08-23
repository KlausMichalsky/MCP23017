# ========================================================================
#             🔸 M C P 2 3 0 1 7  -  L E D   O U T P U T  🔸
# ========================================================================
#  Archivo    : MCP23017-LED-Output.py
#  Autor      : Klaus Michalsky
#  Fecha      : Aug-2026
#
#  DESCRIPCION
#  -----------------------------------------------------------------------
#  - Prueba las salidas GPIO del MCP23017 mediante I2C.
#  - Detecta el MCP23017 en la dirección I2C 0x20.
#  - GPA7 controla el LED 1.
#  - GPB0 controla el LED 2.
#  - Los LEDs se encienden y apagan de forma alternada.
#
#  HARDWARE
#  -----------------------------------------------------------------------
#  MCU     : Raspberry Pi Pico
#  I/O     : MCP23017
#  LED 1   : GPA7
#  LED 2   : GPB0
#  I2C     : I2C0
#  SDA     : GP16 (Pin fisico 21)
#  SCL     : GP17 (Pin fisico 22)
#
#  ESTADO
#  -----------------------------------------------------------------------
#  ✅ Funcional
# ========================================================================

from machine import Pin, I2C
import time

# Crea una conexión I²C y la guarda en la variable (Objeto) i2c)
i2c = I2C(
    0,
    sda=Pin(16),
    scl=Pin(17),
    freq=100000  # 100 kHz standard speed
)

# Crea una variable con el valor de la dirección I2C del MCP23017 en hexadecimal
MCP23017 = 0x20

# Escanea el bus I²C que creamos y dime qué dispositivos responden.
devices = i2c.scan()

print("Dispositivos I2C:", [hex(d) for d in devices])

if MCP23017 not in devices:
    print("ERROR: MCP23017 no encontrado")
    while True:  # entra a bucle infinito si no encuentra el MCP23017
        time.sleep(1)

print("MCP23017 encontrado en 0x20")

# NO configuran nada.
# Son simplemente nombres que nosotros
# le damos a números de registros del MCP23017.
IODIRA = 0x00  # registro que determina la dirección de los GPIO del puerto A.
IODIRB = 0x01  # registro que determina la dirección de los GPIO del puerto B.
GPIOA = 0x12  # General Purpose Input/Output, puerto A.
GPIOB = 0x13  # General Purpose Input/Output, puerto B.

# A7 y B0 como salidas
# 0 = salida, 1 = entrada
#
# A7 -> 0
# A6..A0 -> 1
# 0b01111111
#
# B0 -> 0
# B7..B1 -> 1
# 0b11111110

# MCP23017
#    ↓
# dirección I²C = 0x20
#    ↓
# registro = 0x00 (IODIRA)
#    ↓
# escribir = 01111111

# aqui solo GPA7 es salida, el resto son entradas
i2c.writeto_mem(MCP23017, IODIRA, bytes([0b01111111]))

# aqui solo GPB0 es salida, el resto son entradas
i2c.writeto_mem(MCP23017, IODIRB, bytes([0b11111110]))

print("MPA7 y MPB0 configurados como salidas")

while True:

    # A7 ON, B0 OFF
    i2c.writeto_mem(MCP23017, GPIOA, bytes([0b10000000]))
    i2c.writeto_mem(MCP23017, GPIOB, bytes([0b00000000]))

    print("A7 ON | B0 OFF")
    time.sleep(1)

    # A7 OFF, B0 ON
    i2c.writeto_mem(MCP23017, GPIOA, bytes([0b00000000]))
    i2c.writeto_mem(MCP23017, GPIOB, bytes([0b00000001]))

    print("A7 OFF | B0 ON")
    time.sleep(1)
