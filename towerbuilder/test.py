# -*- coding: utf-8 -*-
import pygame
import os
from math import sin, cos, radians

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Tower Building Game")

# Tải hình nền
BASE_DIR = os.path.dirname(__file__)
background_path = os.path.join(BASE_DIR, "assets", "background.png")
background = pygame.image.load(background_path)
background = pygame.transform.scale(background, (800, 600))

# Thiết lập game
grav = 0.5
rope_length = 280  # Tăng lên 280 để sát biên hơn
force = -0.001
clock = pygame.time.Clock()

# Hiệu ứng gió
wind_force = 0
wind_direction = 1
wind_timer = 0
wind_change_interval = 180

# Cấu hình độ khó (dây ngắn dần khi level tăng)
DIFFICULTY_LEVELS = {
    1: {"force_multiplier": 2.0, "rope_length": 280, "grav": 0.7},   # Level 1: dây dài nhất - dễ
    2: {"force_multiplier": 2.3, "rope_length": 240, "grav": 0.8},   # Level 2: ngắn hơn
    3: {"force_multiplier": 2.5, "rope_length": 200, "grav": 0.9},   # Level 3: ngắn hơn + có gió
    4: {"force_multiplier": 2.8, "rope_length": 160, "grav": 1.0},   # Level 4: ngắn + phải dùng gió
    5: {"force_multiplier": 3.1, "rope_length": 130, "grav": 1.2},   # Level 5: ngắn nhất - khó nhất
}

def draw_text_with_outline(surface, text, font, x, y, color, outline_color=(0, 0, 0), outline_width=2):
    """Vẽ chữ có viền đen"""
    # Vẽ viền (vẽ text ở 8 vị trí xung quanh)
    for dx in [-outline_width, 0, outline_width]:
        for dy in [-outline_width, 0, outline_width]:
            if dx != 0 or dy != 0:
                outline_surface = font.render(text, True, outline_color)
                surface.blit(outline_surface, (x + dx, y + dy))
    
    # Vẽ chữ chính
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))

class Block(pygame.sprite.Sprite):
    def __init__(self, camera_offset=0, tower_size=0, width=250):
        pygame.sprite.Sprite.__init__(self)
        self.width = width
        self.height = 70
        block_path = os.path.join(BASE_DIR, "assets", "block.png")
        original_image = pygame.image.load(block_path)
        self.image = pygame.transform.scale(original_image, (self.width, self.height))
        
        if tower_size % 2 == 0:
            self.angle = radians(-45)
        else:
            self.angle = radians(45)
        
        origin_y = 50 - camera_offset
        # Tính vị trí x của block để tâm block swing quanh điểm neo
        self.x = (800 // 2) + rope_length * sin(self.angle) - (self.width // 2)
        self.y = origin_y + rope_length * cos(self.angle)
        
        self.speed = 0
        self.acceleration = 0
        self.state = "swinging"

    def swing(self, camera_offset=0):
        origin_y = 50 - camera_offset
        # Tính vị trí x sao cho tâm block swing quanh điểm neo
        self.x = (800 // 2) + rope_length * sin(self.angle) - (self.width // 2)
        self.y = origin_y + rope_length * cos(self.angle)
        self.angle += self.speed
        self.acceleration = sin(self.angle) * force
        self.speed += self.acceleration

    def drop(self, tower, current_level=1, wind_force=0):
        if self.state == "swinging":
            self.state = "falling"
            self.xlast = self.x
            self.wind_drift = 0
            
        if not tower.blocks:
            if self.y >= 540:
                self.state = "landed"
                self.y = 540
                self.xlast = self.x
                return {"points": 50, "new_width": self.width}
        else:
            if self.y >= tower.get_top_y() - self.height:
                tower_left = tower.blocks[-1]['x']
                tower_right = tower_left + tower.blocks[-1]['width']
                tower_width = tower.blocks[-1]['width']
                block_left = self.xlast
                block_right = self.xlast + self.width
                
                if block_right > tower_left and block_left < tower_right:
                    self.state = "landed"
                    self.y = tower.get_top_y() - self.height
                    
                    # Tính offset từ cạnh trái tháp
                    offset = abs(self.xlast - tower_left)
                    
                    # Tính phần chồng lên
                    overlap_left = max(block_left, tower_left)
                    overlap_right = min(block_right, tower_right)
                    overlap_width = overlap_right - overlap_left
                    
                    new_width = self.width
                    
                    # Perfect alignment (offset <= 15px cho width lớn)
                    if offset <= 15:
                        new_width = min(tower_width + 10, 300)
                        # Căn giữa block mới
                        self.xlast = tower_left - (new_width - tower_width) / 2
                        self.width = new_width
                        
                        block_path = os.path.join(BASE_DIR, "assets", "block.png")
                        original_image = pygame.image.load(block_path)
                        self.image = pygame.transform.scale(original_image, (self.width, self.height))
                        
                        points = 100
                    elif offset <= 25:
                        # Good - giữ nguyên width
                        points = 50
                        new_width = self.width
                    else:
                        # Bad - cắt block nếu level >= 5
                        if current_level >= 5:
                            new_width = int(overlap_width)
                            self.xlast = overlap_left
                            
                            self.width = new_width
                            block_path = os.path.join(BASE_DIR, "assets", "block.png")
                            original_image = pygame.image.load(block_path)
                            self.image = pygame.transform.scale(original_image, (self.width, self.height))
                        
                        points = 25
                    
                    return {"points": points, "new_width": new_width}
                else:
                    self.state = "failed"
                    return {"points": -1, "new_width": self.width}

        if self.state == "falling":
            self.speed += grav
            self.y += self.speed
            
            if hasattr(self, 'wind_drift'):
                self.wind_drift += wind_force * 0.3
                self.xlast += self.wind_drift
                self.wind_drift *= 0.95
        return None

        if self.state == "falling":
            self.speed += grav
            self.y += self.speed
            
            if hasattr(self, 'wind_drift'):
                self.wind_drift += wind_force * 0.3
                self.xlast += self.wind_drift
                self.wind_drift *= 0.95
        return None

    def draw(self, camera_offset=0):
        draw_y = self.y + camera_offset
        
        if hasattr(self, 'xlast') and self.state in ["falling", "failed"]:
            screen.blit(self.image, (self.xlast, draw_y))
        else:
            screen.blit(self.image, (self.x, draw_y))
        
        if self.state == "swinging":
            # Điểm neo ở giữa màn hình
            origin_on_screen = (400, 50)
            # Vẽ dây từ điểm neo đến tâm block
            block_center_x = self.x + self.width // 2
            pygame.draw.line(screen, (80, 80, 80), origin_on_screen, (block_center_x, draw_y), 3)
            pygame.draw.circle(screen, (255, 200, 0), origin_on_screen, 8)
            pygame.draw.circle(screen, (200, 150, 0), origin_on_screen, 6)

class Tower:
    def __init__(self):
        self.blocks = []
        self.camera_y = 0
        self.target_camera_y = 0
        self.scrolling = False
        self.height = 0
        self.scroll_threshold = 450
        self.shake_offset = 0
        self.shake_speed = 0

    def add_block(self, block):
        self.blocks.append({
            'x': block.xlast if hasattr(block, 'xlast') else block.x,
            'y': block.y,
            'width': block.width,
            'height': block.height,
            'image': block.image
        })
        
        if len(self.blocks) > 0:
            self.height = 550 - self.get_top_y()
            
        top_y = self.get_top_y()
        if top_y < self.scroll_threshold:
            self.target_camera_y += block.height

    def get_top_y(self):
        if not self.blocks:
            return 540
        return min(block['y'] for block in self.blocks)
    
    def update_camera(self):
        if abs(self.target_camera_y - self.camera_y) > 0.5:
            self.scrolling = True
            self.camera_y += (self.target_camera_y - self.camera_y) * 0.15
        else:
            self.camera_y = self.target_camera_y
            self.scrolling = False
    
    def update_wind(self, wind_force):
        self.shake_speed += wind_force * 0.02
        self.shake_speed -= self.shake_offset * 0.05
        self.shake_speed *= 0.95
        self.shake_offset += self.shake_speed
        
        max_shake = 15
        if abs(self.shake_offset) > max_shake:
            self.shake_offset = max_shake if self.shake_offset > 0 else -max_shake
            self.shake_speed *= -0.5

    def draw(self):
        for block in self.blocks:
            screen.blit(block['image'], (block['x'] + self.shake_offset, block['y'] + self.camera_y))

def draw_scoreboard(screen, font_large, font_small, score, level, combo):
    # Panel vuông không bo góc
    board_surface = pygame.Surface((250, 160))
    board_surface.fill((40, 40, 70))
    
    # Viền vàng
    pygame.draw.rect(board_surface, (255, 215, 0), (0, 0, 250, 160), 4)
    pygame.draw.rect(board_surface, (200, 170, 0), (4, 4, 242, 152), 2)
    
    screen.blit(board_surface, (540, 10))
    
    # Tiêu đề
    draw_text_with_outline(screen, "BANG DIEM", font_large, 575, 20, (255, 255, 100))
    
    y_offset = 60
    
    # Level
    draw_text_with_outline(screen, f"Level: {level}", font_small, 555, y_offset, (150, 200, 255))
    y_offset += 30
    
    # Điểm số
    draw_text_with_outline(screen, f"Diem: {score}", font_small, 555, y_offset, (255, 255, 100))
    y_offset += 30
    
    # Độ khó - hiển thị số
    difficulty_level = min(level, 5)
    draw_text_with_outline(screen, f"Do kho: {difficulty_level}/5", font_small, 555, y_offset, (255, 150, 255))
    y_offset += 30
    
    # Combo
    if combo > 1:
        draw_text_with_outline(screen, f"x{combo} COMBO!", font_small, 555, y_offset, (255, 100, 100))

def adjust_difficulty(level):
    global force, rope_length, grav
    difficulty_level = min(level, 5)
    config = DIFFICULTY_LEVELS[difficulty_level]
    force = -0.001 * config["force_multiplier"]
    rope_length = config["rope_length"]
    grav = config["grav"]

def game_over_screen(screen, font_large, font_small, background, tower, block, score, level):
    waiting = True
    
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                elif event.key == pygame.K_ESCAPE:
                    return False
        
        screen.fill((135, 206, 235))
        screen.blit(background, (0, 0))
        tower.draw()
        block.draw(tower.camera_y)
        
        # Panel game over vuông
        game_over_surface = pygame.Surface((420, 280))
        game_over_surface.fill((30, 30, 50))
        
        # Viền đỏ
        pygame.draw.rect(game_over_surface, (255, 80, 80), (0, 0, 420, 280), 6)
        pygame.draw.rect(game_over_surface, (200, 50, 50), (6, 6, 408, 268), 3)
        
        screen.blit(game_over_surface, (190, 160))
        
        # Text
        draw_text_with_outline(screen, "GAME OVER!", font_large, 295, 180, (255, 100, 100))
        
        y = 240
        draw_text_with_outline(screen, f"Diem cuoi: {score}", font_small, 310, y, (255, 255, 100))
        y += 40
        
        draw_text_with_outline(screen, f"Level dat: {level}", font_small, 310, y, (150, 200, 255))
        y += 60
        
        draw_text_with_outline(screen, "Nhan R de choi lai", font_small, 285, y, (255, 255, 150))
        y += 35
        
        draw_text_with_outline(screen, "Nhan ESC de thoat", font_small, 285, y, (255, 200, 200))
        
        pygame.display.flip()
        clock.tick(60)

def draw_instruction_panel(screen, font_small, level):
    """Vẽ panel hướng dẫn vuông"""
    panel_surface = pygame.Surface((250, 90))
    panel_surface.fill((50, 50, 90))
    pygame.draw.rect(panel_surface, (100, 200, 255), (0, 0, 250, 90), 3)
    screen.blit(panel_surface, (10, 10))
    
    # Hướng dẫn
    draw_text_with_outline(screen, "SPACE - Tha khoi", font_small, 25, 25, (255, 255, 255))
    draw_text_with_outline(screen, "Dat chinh xac = bonus!", font_small, 25, 50, (255, 255, 100))
    
    # Hiển thị chỉ báo gió
    if level >= 3:
        draw_text_with_outline(screen, "Can than voi gio!", font_small, 25, 75, (150, 200, 255))

def draw_wind_indicator(screen, font_small, level, wind_force, wind_direction):
    """Vẽ chỉ báo gió vuông"""
    if level < 3:
        return
    
    panel_surface = pygame.Surface((180, 50))
    panel_surface.fill((60, 100, 180))
    pygame.draw.rect(panel_surface, (100, 150, 255), (0, 0, 180, 50), 3)
    screen.blit(panel_surface, (280, 10))
    
    # Text gió
    wind_text = "Gio: "
    if abs(wind_force) > 0.5:
        wind_text += "MANH "
        color = (255, 100, 100)
    else:
        wind_text += "Nhe "
        color = (255, 255, 150)
    
    if wind_direction > 0:
        wind_text += ">>>"
    else:
        wind_text += "<<<"
    
    draw_text_with_outline(screen, wind_text, font_small, 295, 20, color)

def main():
    global force, rope_length, grav, wind_force, wind_direction, wind_timer
    running = True
    tower = Tower()
    current_block_width = 250  # Thay đổi width ban đầu thành 250
    block = Block(tower.camera_y, tower_size=len(tower.blocks), width=current_block_width)
    
    score = 0
    level = 1
    combo = 0
    force = -0.002
    
    wind_force = 0
    wind_direction = 1
    wind_timer = 0
    
    # Khởi tạo font
    font_small = None
    font_large = None
    font_names = ["Segoe UI", "Arial Unicode MS", "Microsoft Sans Serif", "Tahoma", "Verdana"]
    
    for font_name in font_names:
        try:
            font_small = pygame.font.SysFont(font_name, 20)
            font_large = pygame.font.SysFont(font_name, 28, bold=True)
            font_small.render("ắ", True, (255, 255, 255))
            break
        except:
            continue
    
    if font_small is None:
        font_small = pygame.font.Font(None, 28)
        font_large = pygame.font.Font(None, 36)
    
    while running:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if block.state == "swinging":
                        block.drop(tower, current_level=level, wind_force=wind_force)

        # Cập nhật gió
        if level >= 3:
            wind_timer += 1
            if wind_timer >= wind_change_interval:
                wind_timer = 0
                wind_direction *= -1
            
            wind_intensity = min(level - 2, 5) * 0.3
            wind_force = wind_direction * wind_intensity
        else:
            wind_force = 0
        
        tower.update_wind(wind_force)

        # Cập nhật
        if block.state == "swinging":
            block.swing(tower.camera_y)
        elif block.state == "falling":
            result = block.drop(tower, current_level=level, wind_force=wind_force)
            if result is not None:
                points = result["points"]
                new_width = result["new_width"]
                
                if points == -1:
                    block.state = "failed"
                    restart = game_over_screen(screen, font_large, font_small, background, tower, block, score, level)
                    if restart:
                        tower = Tower()
                        current_block_width = 250  # Reset về 250
                        block = Block(tower.camera_y, tower_size=len(tower.blocks), width=current_block_width)
                        score = 0
                        level = 1
                        combo = 0
                        force = -0.002
                        rope_length = 200  # Reset về 200
                        grav = 0.7
                        wind_force = 0
                        wind_direction = 1
                        wind_timer = 0
                    else:
                        running = False
                        continue
                else:
                    if points >= 50:
                        combo += 1
                    else:
                        combo = 0
                    score += points * max(1, combo)
                    current_block_width = new_width
        elif block.state == "landed":
            tower.add_block(block)
            
            if len(tower.blocks) % 3 == 0:
                level += 1
                adjust_difficulty(level)
            
            block = Block(tower.camera_y, tower_size=len(tower.blocks), width=current_block_width)
            
        tower.update_camera()

        # Vẽ
        screen.fill((135, 206, 235))
        screen.blit(background, (0, 0))
        tower.draw()
        block.draw(tower.camera_y)
        
        # Vẽ các panel UI
        draw_instruction_panel(screen, font_small, level)
        draw_wind_indicator(screen, font_small, level, wind_force, wind_direction)
        draw_scoreboard(screen, font_large, font_small, score, level, combo)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()