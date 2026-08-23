from machine import Pin, I2C
import time

# I2C0
# Pin físico 21 = GP16 = SDA
# Pin físico 22 = GP17 = SCL
i2c = I2C(
    0,
    sda=Pin(16),
    scl=Pin(17),
    freq=100000
)

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

i2c.writeto_mem(MCP23017, IODIRA, bytes([0b01111111]))
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
