import pygame
from math import sin, cos

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Simple Tower Game")

# Load background image
background = pygame.image.load("assets/background.png")
background = pygame.transform.scale(background, (800, 600))

# Gravity settings
grav = 0.5
rope_length = 120
force = -0.001
origin = (400, 50)

# FPS control
clock = pygame.time.Clock()

class Block(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # Fixed size for blocks
        self.width = 60
        self.height = 40
        # Load and scale image to fit the fixed size
        original_image = pygame.image.load("assets/block.png")
        self.image = pygame.transform.scale(original_image, (self.width, self.height))
        self.x = 370
        self.y = 150
        self.speed = 0
        self.acceleration = 0
        # States: "swinging", "falling", "landed"
        self.state = "swinging"
        self.angle = 45

    def swing(self):
        # Pendulum motion
        self.x = 370 + rope_length * sin(self.angle)
        self.y = 50 + rope_length * cos(self.angle)
        self.angle += self.speed
        self.acceleration = sin(self.angle) * force
        self.speed += self.acceleration

    def drop(self, tower):
        if self.state == "swinging":
            self.state = "falling"
            
        # Check collision with ground or tower
        if self.y >= 550:  # Ground level
            self.state = "landed"
            self.y = 550
        elif tower.blocks and self.y >= tower.get_top_y() - self.height:
            # Check if block is above the tower
            tower_left = tower.blocks[-1]['x']
            tower_right = tower_left + self.width
            if self.x < tower_right + 20 and self.x + self.width > tower_left - 20:
                self.state = "landed"
                self.y = tower.get_top_y() - self.height

        # Apply gravity when falling
        if self.state == "falling":
            self.speed += grav
            self.y += self.speed

    def draw(self):
        # Draw the block image
        screen.blit(self.image, (self.x, self.y))
        
        # Draw rope when swinging
        if self.state == "swinging":
            pygame.draw.line(screen, (0, 0, 0), origin, (self.x + self.width//2, self.y), 2)
            pygame.draw.circle(screen, (200, 0, 0), origin, 5)

    def reset(self):
        self.x = 370
        self.y = 150
        self.speed = 0
        self.state = "swinging"
        self.angle = 45

class Tower:
    def __init__(self):
        self.blocks = []  # List to store landed blocks

    def add_block(self, block):
        # Add the current block position to the tower
        self.blocks.append({
            'x': block.x,
            'y': block.y,
            'width': block.width,
            'height': block.height,
            'image': block.image
        })

    def get_top_y(self):
        if not self.blocks:
            return 550  # Ground level
        return min(block['y'] for block in self.blocks)

    def draw(self):
        # Draw all blocks in the tower
        for block in self.blocks:
            screen.blit(block['image'], (block['x'], block['y']))

def main():
    running = True
    block = Block()
    tower = Tower()
    
    while running:
        clock.tick(60)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if block.state == "swinging":
                        block.drop(tower)

        # Update game state
        if block.state == "swinging":
            block.swing()
        elif block.state == "falling":
            block.drop(tower)
        elif block.state == "landed":
            # Add block to tower and create a new one
            tower.add_block(block)
            block = Block()  # Create new block

        # Draw everything
        screen.blit(background, (0, 0))  # Draw background image
        
        # Draw tower and current block
        tower.draw()
        block.draw()
        
        # Instructions
        font = pygame.font.Font(None, 36)
        text = font.render("Press SPACE to drop block", True, (255, 255, 255))
        screen.blit(text, (10, 10))
        
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()