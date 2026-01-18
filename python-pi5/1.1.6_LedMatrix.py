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
from luma.core.legacy import text, textsize
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, LCD_FONT
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
    device = max7219(serial, rotate=2)
    print("✓ MAX7219 initialized successfully!\n")
except Exception as e:
    print(f"✗ Error initializing MAX7219: {e}")
    print("\nMake sure you've rewired to the new pins:")
    print("  DIN -> Pin 38, CS -> Pin 40, CLK -> Pin 36")
    raise

virtual = viewport(device, width=200, height=400)

def displayHeart():
    """Display a heart shape on the 8x8 LED matrix"""
    print("→ Displaying heart ❤️...")
    
    # Heart pattern for 8x8 matrix (1 = LED on, 0 = LED off)
    heart = [
        [0, 1, 1, 0, 0, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]
    
    with canvas(device) as draw:
        for y, row in enumerate(heart):
            for x, pixel in enumerate(row):
                if pixel:
                    draw.point((x, y), fill="white")

def displayRectangle():
    print("→ Displaying rectangle outline...")
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")

def displayLetter(letter="A"):
    """Display a single letter centered on the 8x8 matrix"""
    print(f"→ Displaying letter '{letter}' (centered)...")
    
    # For an 8x8 matrix:
    # - CP437_FONT characters are 8 pixels tall, variable width (5-8 px)
    # - TINY_FONT characters are 4 pixels tall, ~4 px wide
    # - LCD_FONT characters are 8 pixels tall, 5 px wide
    
    # Use LCD_FONT for better centering (fixed 5px width)
    font = LCD_FONT
    char_width = 5   # LCD_FONT is 5 pixels wide
    char_height = 8  # LCD_FONT is 8 pixels tall
    
    # Calculate centered position
    x = (8 - char_width) // 2    # (8 - 5) // 2 = 1
    y = (8 - char_height) // 2   # (8 - 8) // 2 = 0
    
    with canvas(device) as draw:
        text(draw, (x, y), letter, fill="white", font=font)

def displayLetterProportional(letter="A"):
    """Display a letter using proportional font, properly centered based on actual width"""
    font = proportional(CP437_FONT)
    
    # Get the actual pixel dimensions of this character
    width, height = textsize(letter, font)
    
    # Center on the 8x8 display
    x = (8 - width) // 2
    y = (8 - height) // 2
    
    print(f"→ Displaying '{letter}' (width={width}px, centered at x={x})")
    with canvas(device) as draw:
        text(draw, (x, y), letter, fill="white", font=font)

def scrollToDisplayText():
    print("→ Scrolling text 'Hello, Nice to meet you!'...")
    with canvas(virtual) as draw:
        text(draw, (0, 0), "Hello, Nice to meet you!", fill="white", font=proportional(CP437_FONT))

    for offset in range(150):
        virtual.set_position((offset, 0))
        time.sleep(0.1)

def scrollLoveMessage(name="World", speed=0.08):
    """
    Scroll 'I ♥ U, {name}' across the LED matrix
    
    Args:
        name: The name to display after "I ♥ U, "
        speed: Scroll speed in seconds (lower = faster)
    """
    # CP437 font has a heart character at position 3
    heart_char = chr(3)  # ♥ in CP437
    
    message = f"I {heart_char} U, {name}"
    print(f"→ Scrolling: 'I ♥ U, {name}'")
    
    # Calculate scroll distance based on message length
    # Each character is roughly 6-8 pixels wide in proportional font
    # Add extra space before and after for smooth scrolling
    # Add 8 pixels for the display width so message scrolls completely off
    scroll_distance = 8 + len(message) * 7 - 12
    
    with canvas(virtual) as draw:
        text(draw, (8, 0), message, fill="white", font=proportional(CP437_FONT))
    
    for offset in range(scroll_distance):
        virtual.set_position((offset, 0))
        time.sleep(speed)

def boom_boom_i_heart_u():
    # Start with square in the middle that expands outward frame by frame
    # Then full square shrinks to the center frame by frame
    # Then print I in the center, then heart, then U
    print("→ Displaying 'Boom Boom I ♥ U' animation...")
    
    # Use EVEN sizes (2, 4, 6, 8) for proper centering on 8x8 grid
    # Center of 8x8 grid is between pixels 3 and 4
    
    # Expanding square: 2x2 → 4x4 → 6x6 → 8x8
    for size in range(2, 10, 2):  # size = 2, 4, 6, 8
        half = size // 2
        with canvas(device) as draw:
            draw.rectangle(
                [(4 - half, 4 - half), (4 + half - 1, 4 + half - 1)],
                outline="white",
                fill="black"
            )
        time.sleep(0.2)
    
    # Shrinking square: 8x8 → 6x6 → 4x4 → 2x2
    for size in range(8, 0, -2):  # size = 8, 6, 4, 2
        half = size // 2
        with canvas(device) as draw:
            draw.rectangle(
                [(4 - half, 4 - half), (4 + half - 1, 4 + half - 1)],
                outline="white",
                fill="black"
            )
        time.sleep(0.2)
    
    # Display I, heart, U
    for char in ["I", chr(3), "U"]:
        displayLetterProportional(char)
        time.sleep(0.5) 

def main():
    print("Starting LED Matrix demo...")
    print("Press Ctrl+C to exit\n")
    
    # Change this to your name!
    YOUR_NAME = "Mala"
    
    while True:
        boom_boom_i_heart_u()

def destroy():
    print("\n\nCleaning up...")
    device.clear()
    print("Done!")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        destroy()
