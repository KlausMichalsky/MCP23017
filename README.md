# MCP23017 Tests with Raspberry Pi Pico

Pruebas del expansor de E/S **MCP23017** utilizando un **Raspberry Pi Pico** y **MicroPython**.

Este repositorio se utiliza para desarrollar y probar el funcionamiento del MCP23017 antes de integrarlo en el proyecto principal **Onyx-Pro**, donde una Raspberry Pi 3A+ se encargará de leer los sensores del tablero.

## Hardware

- Raspberry Pi Pico
- MCP23017
- 2 × LED
- 2 × resistencias de 10 kΩ
- Fuente externa de 5 V para el Pico
- Cables

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
A0 → GND
A1 → GND
A2 → GND
