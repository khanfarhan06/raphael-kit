#!/usr/bin/env python3
"""
Joystick input using MCP3008 with SOFTWARE SPI (Pironman 5 compatible)

Uses software SPI (bit-banging) to avoid conflicts with Pironman's hardware SPI.

Wiring (using regular GPIO pins, NOT hardware SPI):
    MCP3008         Raspberry Pi
    -------         ----------------
    VDD         ->  Pin 1  (3.3V)
    VREF        ->  Pin 1  (3.3V)
    AGND        ->  Pin 6  (Ground)
    DGND        ->  Pin 6  (Ground)
    CLK         ->  Pin 29 (GPIO 5)
    DOUT (MISO) ->  Pin 31 (GPIO 6)
    DIN (MOSI)  ->  Pin 33 (GPIO 13)
    CS          ->  Pin 35 (GPIO 19)

    Joystick        Connections
    --------        ----------------
    VCC         ->  Pin 1  (3.3V)
    GND         ->  Pin 6  (Ground)
    VRX         ->  MCP3008 CH0
    VRY         ->  MCP3008 CH1
    SW          ->  Pin 37 (GPIO 26) + Ground

These pins are near the bottom of the GPIO header, away from Pironman's usual pins.
"""

from gpiozero import MCP3008, Button
import time

# Software SPI pins for MCP3008
MCP_CLK = 5    # Pin 29 - Clock
MCP_MOSI = 13  # Pin 33 - Data to MCP3008 (DIN)
MCP_MISO = 6   # Pin 31 - Data from MCP3008 (DOUT)
MCP_CS = 19    # Pin 35 - Chip Select

# Joystick button pin
BTN_PIN = 26   # Pin 37

print("=" * 50)
print("Joystick - Software SPI Mode (MCP3008)")
print("=" * 50)
print(f"\nWiring required:")
print(f"  MCP3008:")
print(f"    VDD/VREF -> Pin 1  (3.3V)")
print(f"    AGND/DGND -> Pin 6 (Ground)")
print(f"    CLK      -> Pin 29 (GPIO {MCP_CLK})")
print(f"    DOUT     -> Pin 31 (GPIO {MCP_MISO})")
print(f"    DIN      -> Pin 33 (GPIO {MCP_MOSI})")
print(f"    CS       -> Pin 35 (GPIO {MCP_CS})")
print(f"  Joystick:")
print(f"    VRX      -> MCP3008 CH0")
print(f"    VRY      -> MCP3008 CH1")
print(f"    SW       -> Pin 37 (GPIO {BTN_PIN})")
print()

try:
    # Initialize MCP3008 with software SPI on custom pins
    x_axis = MCP3008(channel=0, clock_pin=MCP_CLK, mosi_pin=MCP_MOSI,
                     miso_pin=MCP_MISO, select_pin=MCP_CS)
    y_axis = MCP3008(channel=1, clock_pin=MCP_CLK, mosi_pin=MCP_MOSI,
                     miso_pin=MCP_MISO, select_pin=MCP_CS)
    
    # Initialize joystick button (with pull-up, pressed = connected to ground)
    joy_button = Button(BTN_PIN)
    
    print("✓ MCP3008 and joystick initialized successfully!\n")
except Exception as e:
    print(f"✗ Error initializing: {e}")
    print("\nMake sure you've wired correctly to the specified pins.")
    raise

try:
    print("Reading joystick values (Ctrl+C to exit):\n")
    
    while True:
        # Read X and Y values (gpiozero returns 0.0 to 1.0)
        x_val = x_axis.value
        y_val = y_axis.value
        
        # Convert to 0-1023 range for familiarity (like raw MCP3008)
        x_raw = int(x_val * 1023)
        y_raw = int(y_val * 1023)
        
        # Read button state
        btn_pressed = joy_button.is_pressed
        
        # Determine direction for convenience
        direction = "CENTER"
        if x_val < 0.3:
            direction = "LEFT"
        elif x_val > 0.7:
            direction = "RIGHT"
        elif y_val < 0.3:
            direction = "UP"
        elif y_val > 0.7:
            direction = "DOWN"
        
        # Print values
        print(f"X: {x_raw:4d}  Y: {y_raw:4d}  Btn: {1 if btn_pressed else 0}  [{direction:^6}]", end='\r')
        
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n\nExiting...")
