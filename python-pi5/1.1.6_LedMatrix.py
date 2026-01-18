#!/usr/bin/env python3
"""
MAX7219 LED Matrix for Raspberry Pi 5 (Pironman 5 compatible)

Uses SOFTWARE SPI (bit-banging) to avoid conflicts with Pironman's hardware SPI.

Wiring (using regular GPIO pins, NOT hardware SPI):
    MAX7219     Raspberry Pi
    -------     ----------------
    VCC     ->  Pin 2 (5V)
    GND     ->  Pin 6 (Ground)
    DIN     ->  Pin 38 (GPIO 20)  ← Data
    CS      ->  Pin 40 (GPIO 21)  ← Chip Select
    CLK     ->  Pin 36 (GPIO 16)  ← Clock

These pins are at the BOTTOM of the GPIO header, away from Pironman's usual pins.
"""

from luma.core.interface.serial import bitbang
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.led_matrix.device import max7219
from luma.core.legacy import text
from luma.core.legacy.font import proportional, CP437_FONT
import time

# Software SPI using bit-banging on these GPIO pins:
# These are near the bottom of the header, less likely to conflict with Pironman
DIN_PIN = 20   # Pin 38 - Data
CS_PIN = 21    # Pin 40 - Chip Select  
CLK_PIN = 16   # Pin 36 - Clock

print("=" * 50)
print("MAX7219 LED Matrix - Software SPI Mode")
print("=" * 50)
print(f"\nWiring required:")
print(f"  VCC  -> Pin 2  (5V Power)")
print(f"  GND  -> Pin 6  (Ground)")
print(f"  DIN  -> Pin 38 (GPIO {DIN_PIN})")
print(f"  CS   -> Pin 40 (GPIO {CS_PIN})")
print(f"  CLK  -> Pin 36 (GPIO {CLK_PIN})")
print()

try:
    # Use software SPI (bitbang) instead of hardware SPI
    serial = bitbang(SCLK=CLK_PIN, SDA=DIN_PIN, CE=CS_PIN)
    device = max7219(serial, rotate=1)
    print("✓ MAX7219 initialized successfully!\n")
except Exception as e:
    print(f"✗ Error initializing MAX7219: {e}")
    print("\nMake sure you've rewired to the new pins:")
    print("  DIN -> Pin 38, CS -> Pin 40, CLK -> Pin 36")
    raise

virtual = viewport(device, width=200, height=400)

def displayRectangle():
    print("→ Displaying rectangle outline...")
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")

def displayLetter():
    print("→ Displaying letter 'A'...")
    with canvas(device) as draw:
        text(draw, (0, 0), "A", fill="white", font=proportional(CP437_FONT))

def scrollToDisplayText():
    print("→ Scrolling text 'Hello, Nice to meet you!'...")
    with canvas(virtual) as draw:
        text(draw, (0, 0), "Hello, Nice to meet you!", fill="white", font=proportional(CP437_FONT))

    for offset in range(150):
        virtual.set_position((offset, 0))
        time.sleep(0.1)

def main():
    print("Starting LED Matrix demo...")
    print("Press Ctrl+C to exit\n")
    while True:
        displayRectangle()
        time.sleep(2)
        displayLetter()
        time.sleep(2)
        scrollToDisplayText()

def destroy():
    print("\n\nCleaning up...")
    device.clear()
    print("Done!")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        destroy()
