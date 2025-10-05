# -*- coding: utf-8 -*-
import pygame
import os
from math import sin, cos

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Simple Tower Game")

# Tải hình nền (dùng đường dẫn dựa trên vị trí file)
BASE_DIR = os.path.dirname(__file__)
background_path = os.path.join(BASE_DIR, "assets", "background.png")
background = pygame.image.load(background_path)
background = pygame.transform.scale(background, (800, 600))

# Thiết lập trọng lực
grav = 0.5
rope_length = 120
force = -0.001
origin = (400, 50)

# Điều khiển tốc độ khung hình (FPS)
clock = pygame.time.Clock()

class Block(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
    # Kích thước cố định cho khối
        self.width = 60
        self.height = 40
    # Tải và thay đổi kích thước hình ảnh cho phù hợp với kích thước cố định
        block_path = os.path.join(BASE_DIR, "assets", "block.png")
        original_image = pygame.image.load(block_path)
        self.image = pygame.transform.scale(original_image, (self.width, self.height))
        self.x = 370
        self.y = 150
        self.speed = 0
        self.acceleration = 0
    # Trạng thái: "đang đu", "đang rơi", "đã đáp"
        self.state = "swinging"
        self.angle = 45

    def swing(self):
    # Chuyển động con lắc
        self.x = 370 + rope_length * sin(self.angle)
        self.y = 50 + rope_length * cos(self.angle)
        self.angle += self.speed
        self.acceleration = sin(self.angle) * force
        self.speed += self.acceleration

    def drop(self, tower):
        if self.state == "swinging":
            self.state = "falling"
            
    # Kiểm tra va chạm với mặt đất hoặc tháp
        if self.y >= 550:  # Ground level
            self.state = "landed"
            self.y = 550
        elif tower.blocks and self.y >= tower.get_top_y() - self.height:
            # Kiểm tra nếu khối nằm trên tháp
            tower_left = tower.blocks[-1]['x']
            tower_right = tower_left + self.width
            if self.x < tower_right + 20 and self.x + self.width > tower_left - 20:
                self.state = "landed"
                self.y = tower.get_top_y() - self.height

    # Áp dụng trọng lực khi đang rơi
        if self.state == "falling":
            self.speed += grav
            self.y += self.speed

    def draw(self):
    # Vẽ hình ảnh khối
        screen.blit(self.image, (self.x, self.y))
        
    # Vẽ dây khi đang đu
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
    # Thêm vị trí khối hiện tại vào tháp
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
    # Vẽ tất cả các khối trong tháp
        for block in self.blocks:
            screen.blit(block['image'], (block['x'], block['y']))

def main():
    running = True
    block = Block()
    tower = Tower()
    
    # Khởi tạo font một lần (hỗ trợ tiếng Việt)
    # Thử các font Windows phổ biến hỗ trợ Unicode
    font = None
    font_names = ["Segoe UI", "Arial Unicode MS", "Microsoft Sans Serif", "Tahoma", "Verdana"]
    
    for font_name in font_names:
        try:
            # Sử dụng kích thước nhỏ hơn để phù hợp với yêu cầu
            font = pygame.font.SysFont(font_name, 24)
            # Test render một ký tự tiếng Việt để kiểm tra
            test_surface = font.render("ắ", True, (255, 255, 255))
            break
        except:
            continue
    
    # Nếu tất cả đều thất bại, dùng font mặc định
    if font is None:
        font = pygame.font.Font(None, 36)
    
    while running:
        clock.tick(60)
        
    # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if block.state == "swinging":
                        block.drop(tower)

    # Cập nhật trạng thái trò chơi
        if block.state == "swinging":
            block.swing()
        elif block.state == "falling":
            block.drop(tower)
        elif block.state == "landed":
            # Add block to tower and create a new one
            tower.add_block(block)
            block = Block()  # Create new block

        # Vẽ tất cả mọi thứ
        screen.fill((135, 206, 235))  # Màu xanh da trời để debug
        screen.blit(background, (0, 0))  # Draw background image
        
        # Vẽ tháp và khối hiện tại
        tower.draw()
        block.draw()
        
        # Hướng dẫn (vị trí cũ, nhỏ hơn)
        # Thay font mặc định hiển thị (nếu Tahoma có thể không tồn tại, sẽ fallback trong danh sách font)
        text = font.render("Nhấn SPACE để thả khối", True, (0, 0, 0))
        screen.blit(text, (10, 10))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()