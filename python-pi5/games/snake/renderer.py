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

from config import LED_CLK, LED_DIN, LED_CS, INPUT_POLL_INTERVAL, DEFAULT_ANIMATION_INTERVAL
from luma.core.interface.serial import bitbang
from luma.core.render import canvas
from luma.led_matrix.device import max7219
from sprites import Sprite, SPRITES
import time

class Renderer:
    def __init__(self):
        serial = bitbang(SCLK=LED_CLK, SDA=LED_DIN, CE=LED_CS)
        device = max7219(serial, rotate=2)
        self.matrix = device

    def draw_game_frame(self, game_state):
        with canvas(self.matrix) as draw:
            # Draw snake
            for pos in game_state.snake_positions:
                x, y = pos
                draw.point((x, y), fill="white")
            # Draw food
            food_x, food_y = game_state.food_position
            draw.point((food_x, food_y), fill="white")
    
    def _draw_pattern(self, pattern):
        """Draw an 8x8 pattern to the matrix."""
        with canvas(self.matrix) as draw:
            for y, row in enumerate(pattern):
                for x, pixel in enumerate(row):
                    if pixel:
                        draw.point((x, y), fill="white")
    
    def play_intro_animation_loop(self, should_stop) -> None:
        """Play intro animation loop until should_stop() returns True."""
        while True:
            should_start_game = self._play_face_animation(should_stop)
            if should_start_game:
                break
        self._play_heart_animation()
        self.clear()
        time.sleep(0.2)
    
    def play_game_over_animation(self, score: int, should_stop):
        self._play_cross_animation()
        self._show_score(score)
        while True:
            if self._wait_or_stop(DEFAULT_ANIMATION_INTERVAL, should_stop):
                break
        self.clear()
        time.sleep(0.2)
    
    def _play_face_animation(self, should_stop):
        face_animations = [
            SPRITES[Sprite.FACE_RIGHT],
            SPRITES[Sprite.FACE_LEFT],
            SPRITES[Sprite.FACE_RIGHT],
            SPRITES[Sprite.FACE_WINK],
            SPRITES[Sprite.FACE_RIGHT],
        ]
        for face_animation in face_animations:
            self._draw_pattern(face_animation)
            if self._wait_or_stop(DEFAULT_ANIMATION_INTERVAL, should_stop):
                return True
        return False
    
    def _play_heart_animation(self):
        # Show expanding heart animation
        hearts = [
            SPRITES[Sprite.HEART_DOT],
            SPRITES[Sprite.HEART_QUARTER],
            SPRITES[Sprite.HEART_HALF],
            SPRITES[Sprite.HEART_FULL],
        ]
        for heart in hearts:
            self._draw_pattern(heart)
            time.sleep(DEFAULT_ANIMATION_INTERVAL)
        # Show contracting heart animation
        for heart in reversed(hearts):
            self._draw_pattern(heart)
            time.sleep(DEFAULT_ANIMATION_INTERVAL)
    
    def _play_cross_animation(self):
        crosses = [
            SPRITES[Sprite.CROSS_DOT],
            SPRITES[Sprite.CROSS_QUARTER],
            SPRITES[Sprite.CROSS_HALF],
            SPRITES[Sprite.CROSS_FULL],
        ]
        for cross in crosses:
            self._draw_pattern(cross)
            time.sleep(DEFAULT_ANIMATION_INTERVAL)
        for i in range(3):
            self._draw_pattern(SPRITES[Sprite.EMPTY])
            time.sleep(DEFAULT_ANIMATION_INTERVAL)
            self._draw_pattern(SPRITES[Sprite.FULL])
            time.sleep(DEFAULT_ANIMATION_INTERVAL)
    
    def _show_scrolling_score(self, score: int):
        # Show infinite scrolling score until should_stop() returns True.
        # For smooth scrolling we will use virtual viewport.
        # Draw the score message twice for seamless looping.
        # [   Score: 100    Score: 100  ]
        #    ↑________↑
        #    cycle_width (one full message)
        virtual = viewport(self.matrix, width=200, height=400)
        with canvas(virtual) as draw:
            text(draw, (0, 0), f"Score: {score}", fill="white", font=proportional(CP437_FONT))
            text(draw, (score_width, 0), f"Score: {score}", fill="white", font=proportional(CP437_FONT))
        offset = 0
        while True:
            virtual.set_position((offset, 0))
            if self._wait_or_stop(DEFAULT_ANIMATION_INTERVAL, should_stop):
                break
            offset += 1
            if offset >= score_width:
                offset = 0
    
    def _wait_or_stop(self, duration: float, should_stop) -> bool:
        """
        Wait for duration while checking should_stop callback.
        Returns True if should_stop() returned True (stop requested).
        """
        elapsed = 0.0
        poll_interval = INPUT_POLL_INTERVAL  # Check every 50ms
        while elapsed < duration:
            if should_stop():
                return True
            time.sleep(poll_interval)
            elapsed += poll_interval
        return False
    
    def clear(self):
        self.matrix.clear()