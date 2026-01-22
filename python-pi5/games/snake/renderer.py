"""
Handles rendering of the Snake game using 8x8 LED matrix.
Initializes the 8x8 LED matrix display using software SPI on custom GPIO pins.
Wiring required:
    LED Matrix:
        VCC       -> Pin 2  (3.3V)
        GND       -> Pin 6 (Ground)
        DIN       -> Pin 38 (GPIO 20)
        CLK       -> Pin 36 (GPIO 16)
        CS        -> Pin 40 (GPIO 21)
All wirings are different from Pironman's usual pins to avoid conflicts.
All wirings are different from MCP3008's pins + Joystick button to avoid conflicts.

NOTE: This code works with the gpiozero library's bitbang SPI implementation.
It does not use hardware SPI to avoid conflicts with other peripherals.
Implementation does not use LEDMatrix class from gpiozero due to lack of software SPI support.
"""

from config import LED_CLK, LED_DIN, LED_CS
from luma.core.interface.serial import bitbang
from luma.core.render import canvas
from luma.led_matrix.device import max7219

class Renderer:
    def __init__(self):
        serial = bitbang(SCLK=LED_CLK, SDA=LED_DIN, CE=LED_CS)
        device = max7219(serial, rotate=2)
        self.matrix = device
    
    def draw_frame(self, game_state):
        with canvas(self.matrix) as draw:
            # Draw snake
            for pos in game_state.snake_positions:
                x, y = pos
                draw.point((x, y), fill="white")
            # Draw food
            food_x, food_y = game_state.food_position
            draw.point((food_x, food_y), fill="white")