
# ========================================================================
# 🔸 M C P 2 3 0 1 7  -  6 4   D R V 5 0 3 2 F A - 6   S E N S O R S 🔸
# ========================================================================
#
#  Archivo    : MCP23017-64xDRV5032FA.py
#  Autor      : Klaus Michalsky
#  Fecha      : Sep-2026
#
#  DESCRIPCION
#  -----------------------------------------------------------------------
#  - Lee 64 sensores Hall DRV5032FA-6 mediante 4 MCP23017.
#  - Cada placa contiene:
#
#       1x MCP23017
#       16x DRV5032FA-6
#
#  - Las 4 placas comparten el mismo bus I2C.
#  - Cada MCP23017 tiene una dirección diferente mediante A0/A1/A2.
#
#
#  DIRECCIONES
#  -----------------------------------------------------------------------
#
#  PLACA 1 → 0x20 → DRV0  - DRV15
#  PLACA 2 → 0x21 → DRV16 - DRV31
#  PLACA 3 → 0x22 → DRV32 - DRV47
#  PLACA 4 → 0x23 → DRV48 - DRV63
#
#
#  LOGICA DRV5032FA
#  -----------------------------------------------------------------------
#  HIGH = sin imán
#  LOW  = imán detectado
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
#  MCP1      : 0x20
#  MCP2      : 0x21
#  MCP3      : 0x22
#  MCP4      : 0x23
#
# ========================================================================


# ========================================================================
# CONFIGURACION I2C
# ========================================================================

from machine import Pin, I2C
import time


i2c = I2C(
    0,
    sda=Pin(16),
    scl=Pin(17),
    freq=100000
)

# ============================================================
# DIRECCIONES MCP23017
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
# REGISTROS MCP23017
# ============================================================

IODIRA = 0x00
IODIRB = 0x01

GPIOA = 0x12
GPIOB = 0x13

# ============================================================
# ESCANEO I2C
# ============================================================

devices = i2c.scan()

print("")
print("========================================")
print("        DISPOSITIVOS I2C")
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

# ============================================================
# CONFIGURAR LOS 16 GPIO DE CADA MCP COMO ENTRADAS
# ============================================================

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

# ============================================================
# INFORMACION
# ============================================================

print("")
print("========================================")
print("      MCP23017 - 64 DRV5032FA")
print("========================================")
print("")

print("PLACA 1 -> MCP 0x20 -> DRV0  - DRV15")
print("PLACA 2 -> MCP 0x21 -> DRV16 - DRV31")
print("PLACA 3 -> MCP 0x22 -> DRV32 - DRV47")
print("PLACA 4 -> MCP 0x23 -> DRV48 - DRV63")

print("")
print("HIGH = SIN IMAN")
print("LOW  = IMAN DETECTADO")
print("")

print("========================================")
print("       MONITOREO DE 64 SENSORES")
print("========================================")
print("")

# ============================================================
# ESTADO ANTERIOR
# ============================================================

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

# ============================================================
# CONTADOR DE ERRORES I2C
# ============================================================

i2c_errors = [
    0,
    0,
    0,
    0
]

# ============================================================
# LOOP PRINCIPAL
# ============================================================

while True:

    for board_index, address in enumerate(MCP_BOARDS):

        # ====================================================
        # LECTURA I2C PROTEGIDA
        # ====================================================

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

            # Pequeña pausa antes de continuar
            time.sleep(0.01)

            continue

        # ====================================================
        # NUMERO BASE DE SENSORES
        # ====================================================

        sensor_base = board_index * 16

        # ====================================================
        # GPIOA -> DRV0-DRV7
        # ====================================================

        for sensor in range(8):

            mask = 1 << sensor

            current = value_a & mask

            previous = previous_a[board_index] & mask

            # Solo imprimir si cambio
            if current != previous:

                sensor_number = sensor_base + sensor

                if current:

                    print(
                        "DRV{} -> HIGH | SIN IMAN | LED OFF".format(
                            sensor_number
                        )
                    )

                else:

                    print(
                        "DRV{} -> LOW  | IMAN DETECTADO | LED ON".format(
                            sensor_number
                        )
                    )

        # ====================================================
        # GPIOB -> DRV8-DRV15
        # ====================================================

        for sensor in range(8):

            mask = 1 << sensor

            current = value_b & mask

            previous = previous_b[board_index] & mask

            # Solo imprimir si cambio
            if current != previous:

                sensor_number = sensor_base + 8 + sensor

                if current:

                    print(
                        "DRV{} -> HIGH | SIN IMAN | LED OFF".format(
                            sensor_number
                        )
                    )

                else:

                    print(
                        "DRV{} -> LOW  | IMAN DETECTADO | LED ON".format(
                            sensor_number
                        )
                    )

        # ====================================================
        # GUARDAR ESTADO ACTUAL
        # ====================================================

        previous_a[board_index] = value_a

        previous_b[board_index] = value_b

    # ========================================================
    # PEQUEÑA PAUSA
    # ========================================================

    time.sleep(0.05)
