"""
Handles the main game loop for the Snake game.
Sets up the game state, input handler, and renderer.
"""
from input_handler import InputHandler
from renderer import Renderer
from game_state import GameState
from direction import Direction
from config import GAME_SPEED
import time

def game_loop():
    print("Starting the Snake game...")
    input_handler = InputHandler()
    renderer = Renderer()
    game_state = GameState()
    speed = GAME_SPEED

    renderer.draw_frame(game_state)
    print(f"Score: {game_state.score}")

    while not game_state.game_over:
        direction = input_handler.poll_for_direction_input(timeout=speed)
        
        game_state.move_snake(direction)
        game_state.check_collision()
        
        if game_state.check_food_collision():
            game_state.eat_food()
        
        renderer.draw_frame(game_state)
        print(f"Score: {game_state.score}")


if __name__ == "__main__":
    game_loop()
