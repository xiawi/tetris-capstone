from settings import DAS, ARR, SDF
import pygame
import time
from gamecontroller import GameController

class InputHandler:
    def __init__(self, game_controller: GameController):
        self.game_controller = game_controller
        self.das_timer = 0  # Delayed Auto-Shift timer
        self.arr_timer = 0  # Auto-Repeat Rate timer
        self.sdf_timer = 0  # Soft Drop Factor timer

        self.das_delay = DAS * 0.001  # Example: 150 ms delay for DAS
        self.arr_speed = ARR * 0.001  # Example: 50 ms per movement after DAS
        self.sdf_speed = SDF * 0.001  # Example: 50 ms per soft drop step

        self.last_move_time = time.time()
        self.moving_left = False
        self.moving_right = False

    def handleInput(self):
        keys = pygame.key.get_pressed()
        current_time = time.time()

        if keys[pygame.K_s]:  # Soft Drop
            if current_time - self.sdf_timer >= self.sdf_speed:
                self.game_controller.softDrop()
                self.sdf_timer = current_time

        # Handle DAS for left movement
        if keys[pygame.K_a]:
            if not self.moving_left:  # On first press
                self.game_controller.moveLeft()
                self.das_timer = current_time  # Start DAS timer
                self.arr_timer = current_time  # Start ARR timer
                self.moving_left = True
            elif current_time - self.das_timer >= self.das_delay:  # DAS delay is over
                if current_time - self.arr_timer >= self.arr_speed:  # ARR active
                    self.game_controller.moveLeft()
                    self.arr_timer = current_time  # Reset ARR timer
        else:
            self.moving_left = False  # Reset when the key is released

        # Handle DAS for right movement
        if keys[pygame.K_d]:
            if not self.moving_right:  # On first press
                self.game_controller.moveRight()
                self.das_timer = current_time  # Start DAS timer
                self.arr_timer = current_time  # Start ARR timer
                self.moving_right = True
            elif current_time - self.das_timer >= self.das_delay:  # DAS delay is over
                if current_time - self.arr_timer >= self.arr_speed:  # ARR active
                    self.game_controller.moveRight()
                    self.arr_timer = current_time  # Reset ARR timer
        else:
            self.moving_right = False  # Reset when the key is released

        # Process immediate (single press) inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()  # Exit the game
            if event.type == pygame.KEYDOWN:
                self.processKeyEvent(event.key)

    def processKeyEvent(self, key):
        if key == pygame.K_w:  # Hard Drop
            self.game_controller.hardDrop()
        if key == pygame.K_j:  # Rotate Left
            self.game_controller.rotateLeft()
        if key == pygame.K_l:  # Rotate Right
            self.game_controller.rotateRight()
        if key == pygame.K_i:  # Hold Piece
            self.game_controller.holdPiece()
