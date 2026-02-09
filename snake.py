"""
Classic Snake Game Implementation
A simple and interactive Snake game built with Pygame
"""

import pygame
import sys
from enum import Enum
from collections import deque
import random

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)

# Game states
class GameState(Enum):
    RUNNING = 1
    PAUSED = 2
    OVER = 3

# Direction enumeration
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class Snake:
    """Represents the Snake entity"""
    
    def __init__(self, start_x, start_y):
        self.body = deque([(start_x, start_y)])
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.growing = False
    
    def update(self):
        """Update snake position"""
        self.direction = self.next_direction
        
        # Calculate new head position
        head_x, head_y = self.body[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)
        
        # Add new head
        self.body.appendleft(new_head)
        
        # Remove tail if not growing
        if not self.growing:
            self.body.pop()
        else:
            self.growing = False
    
    def grow(self):
        """Make the snake grow on next update"""
        self.growing = True
    
    def set_direction(self, direction):
        """Set the next direction safely (prevent reversing)"""
        # Prevent reverse movement
        if (self.direction == Direction.UP and direction == Direction.DOWN) or \
           (self.direction == Direction.DOWN and direction == Direction.UP) or \
           (self.direction == Direction.LEFT and direction == Direction.RIGHT) or \
           (self.direction == Direction.RIGHT and direction == Direction.LEFT):
            return
        self.next_direction = direction
    
    def get_head(self):
        """Return head position"""
        return self.body[0]
    
    def check_collision(self):
        """Check if snake collides with itself or walls"""
        head_x, head_y = self.get_head()
        
        # Wall collision
        if head_x < 0 or head_x >= GRID_WIDTH or head_y < 0 or head_y >= GRID_HEIGHT:
            return True
        
        # Self collision
        if self.get_head() in list(self.body)[1:]:
            return True
        
        return False


class Food:
    """Represents the food entity"""
    
    def __init__(self):
        self.position = self.spawn()
    
    def spawn(self):
        """Spawn food at a random position"""
        return (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
    
    def respawn(self, snake_body):
        """Respawn food at a new position not occupied by snake"""
        while True:
            self.position = self.spawn()
            if self.position not in snake_body:
                break


class Game:
    """Main game class"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game variables
        self.snake = Snake(GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.food = Food()
        self.score = 0
        self.state = GameState.RUNNING
        self.speed = 8  # Game ticks per second
    
    def handle_input(self):
        """Handle user input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                if event.key == pygame.K_SPACE:
                    if self.state == GameState.RUNNING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.RUNNING
                    elif self.state == GameState.OVER:
                        self.restart()
                
                if event.key == pygame.K_UP:
                    self.snake.set_direction(Direction.UP)
                elif event.key == pygame.K_DOWN:
                    self.snake.set_direction(Direction.DOWN)
                elif event.key == pygame.K_LEFT:
                    self.snake.set_direction(Direction.LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.snake.set_direction(Direction.RIGHT)
        
        return True
    
    def update(self):
        """Update game state"""
        if self.state != GameState.RUNNING:
            return
        
        # Update snake
        self.snake.update()
        
        # Check collision
        if self.snake.check_collision():
            self.state = GameState.OVER
            return
        
        # Check food collision
        if self.snake.get_head() == self.food.position:
            self.snake.grow()
            self.score += 10
            self.food.respawn(self.snake.body)
            # Increase difficulty slightly
            if self.speed < 15:
                self.speed += 0.1
    
    def draw(self):
        """Draw game elements"""
        self.screen.fill(BLACK)
        
        # Draw grid (optional)
        for x in range(0, WINDOW_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, (40, 40, 40), (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, (40, 40, 40), (0, y), (WINDOW_WIDTH, y))
        
        # Draw snake
        for i, (x, y) in enumerate(self.snake.body):
            color = DARK_GREEN if i == 0 else GREEN  # Head darker than body
            pygame.draw.rect(self.screen, color, 
                           (x * GRID_SIZE + 2, y * GRID_SIZE + 2, 
                            GRID_SIZE - 4, GRID_SIZE - 4))
        
        # Draw food
        food_x, food_y = self.food.position
        pygame.draw.rect(self.screen, RED, 
                        (food_x * GRID_SIZE + 2, food_y * GRID_SIZE + 2, 
                         GRID_SIZE - 4, GRID_SIZE - 4))
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Draw pause text
        if self.state == GameState.PAUSED:
            pause_text = self.font.render("PAUSED", True, YELLOW)
            text_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(pause_text, text_rect)
            continue_text = self.small_font.render("Press SPACE to continue", True, WHITE)
            continue_rect = continue_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40))
            self.screen.blit(continue_text, continue_rect)
        
        # Draw game over text
        if self.state == GameState.OVER:
            game_over_text = self.font.render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40))
            self.screen.blit(game_over_text, text_rect)
            
            final_score = self.small_font.render(f"Final Score: {self.score}", True, WHITE)
            score_rect = final_score.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10))
            self.screen.blit(final_score, score_rect)
            
            restart_text = self.small_font.render("Press SPACE to restart or ESC to exit", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
            self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
    
    def restart(self):
        """Restart the game"""
        self.snake = Snake(GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.food = Food()
        self.score = 0
        self.state = GameState.RUNNING
        self.speed = 8
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(self.speed)
        
        pygame.quit()
        sys.exit()


def main():
    """Entry point"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
