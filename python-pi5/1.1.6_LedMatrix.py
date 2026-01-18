from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.led_matrix.device import max7219
from luma.core.legacy import text
from luma.core.legacy.font import proportional, CP437_FONT, LCD_FONT
import time

# Configuration for MAX7219 LED Matrix
# Try different configurations if one doesn't work:
# 
# Option 1: SPI0, CE0 (GPIO 8) - Default
# serial = spi(port=0, device=0, gpio=noop())
#
# Option 2: SPI0, CE1 (GPIO 7)
# serial = spi(port=0, device=1, gpio=noop())
#
# Option 3: SPI1, CE0 (GPIO 18) - Alternative SPI bus
# serial = spi(port=1, device=0, gpio=noop())
#
# Note: Pironman 5 case may use SPI0 for its internal display.
# If you're getting conflicts, try SPI1 or use different CS pin.

# Wiring for MAX7219 with SPI0:
#   VCC  -> 5V (Pin 2 or 4)
#   GND  -> GND (Pin 6, 9, 14, 20, 25, 30, 34, or 39)
#   DIN  -> GPIO 10 / MOSI (Pin 19)
#   CS   -> GPIO 8 / CE0 (Pin 24) or GPIO 7 / CE1 (Pin 26)
#   CLK  -> GPIO 11 / SCLK (Pin 23)

print("Initializing MAX7219 LED Matrix...")
print("Using SPI0, device=0 (CE0 on GPIO 8)")

try:
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, rotate=1)
    print("MAX7219 initialized successfully!")
except Exception as e:
    print(f"Error initializing MAX7219: {e}")
    print("\nTroubleshooting tips:")
    print("1. Make sure SPI is enabled: sudo raspi-config -> Interface Options -> SPI")
    print("2. Check wiring: DIN->GPIO10, CLK->GPIO11, CS->GPIO8")
    print("3. If Pironman conflicts, try device=1 (CE1 on GPIO 7)")
    raise

virtual = viewport(device, width=200, height=400)

def displayRectangle():
    print("Displaying rectangle...")
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")

def displayLetter():
    print("Displaying letter 'A'...")
    with canvas(device) as draw:
        text(draw, (0, 0), "A", fill="white", font=proportional(CP437_FONT))

def scrollToDisplayText():
    print("Scrolling text...")
    with canvas(virtual) as draw:
        text(draw, (0, 0), "Hello, Nice to meet you!", fill="white", font=proportional(CP437_FONT))

    for offset in range(150):
        virtual.set_position((offset, 0))
        time.sleep(0.1)

def main():
    print("\nStarting LED Matrix demo...")
    print("Press Ctrl+C to exit\n")
    while True:
        displayRectangle()
        time.sleep(2)
        displayLetter()
        time.sleep(2)
        scrollToDisplayText()

def destroy():
    print("\nCleaning up...")
    device.clear()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        destroy()
