# MCP23017 Tests with Raspberry Pi Pico

Pruebas del expansor de E/S **MCP23017** utilizando un **Raspberry Pi Pico** y **MicroPython**.

Este repositorio se utiliza para desarrollar y probar el funcionamiento del MCP23017 antes de integrarlo en el proyecto principal **Onyx-Pro**, donde una Raspberry Pi 3A+ se encargará de leer los sensores del tablero.

## Hardware

- Raspberry Pi Pico
- MCP23017
- 2 × LED
- 2 × resistencias de 10 kΩ


## Comunicación

El MCP23017 se comunica con el Raspberry Pi Pico mediante **I²C**.

### Conexiones I²C

| Raspberry Pi Pico | MCP23017 |
|---|---|
| GP16 (pin físico 21) | SDA |
| GP17 (pin físico 22) | SCL |
| 3V3 OUT | VDD |
| GND | VSS |

### Dirección I²C

Los pines de dirección están conectados:

```text
RESET → 3.3V    → MCP23017 siempre habilitado
A0    → GND     → ┐
A1    → GND     → ├── dirección I²C = 0x20
A2    → GND     → ┘


### I²C Address Selection

The MCP23017 I²C address is selected using the A2, A1 and A0 pins.

| A2 | A1 | A0 | I²C Address |
|:--:|:--:|:--:|:-----------:|
| 0 | 0 | 0 | `0x20` |
| 0 | 0 | 1 | `0x21` |
| 0 | 1 | 0 | `0x22` |
| 0 | 1 | 1 | `0x23` |
| 1 | 0 | 0 | `0x24` |
| 1 | 0 | 1 | `0x25` |
| 1 | 1 | 0 | `0x26` |
| 1 | 1 | 1 | `0x27` |
