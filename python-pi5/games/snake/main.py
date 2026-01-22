"""
Handles the main game loop for the Snake game.
Sets up the game state, input handler, and renderer.
"""
from input_handler import InputHandler
from renderer import Renderer
from game_state import GameState
from direction import Direction

def game_loop():
    print("Starting the Snake game...")
    input_handler = InputHandler()
    renderer = Renderer()
    game_state = GameState()

    while not game_state.game_over:
        direction = input_handler.get_direction()
        if direction != game_state.direction and direction != Direction.NONE:
            game_state.direction = direction
        
        game_state.move_snake()
        game_state.check_collision()
        
        if game_state.check_food_collision():
            game_state.eat_food()
        
        renderer.draw_frame(game_state)


if __name__ == "__main__":
    game_loop()