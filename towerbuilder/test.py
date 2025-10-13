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
rope_length = 280
force = -0.001
clock = pygame.time.Clock()

# Hiệu ứng gió
wind_force = 0
wind_direction = 1
wind_timer = 0
wind_change_interval = 180

# Cấu hình độ khó (10 level)
DIFFICULTY_LEVELS = {
    1: {"force_multiplier": 2.0, "rope_length": 250, "grav": 0.7},
    2: {"force_multiplier": 2.3, "rope_length": 250, "grav": 0.75},
    3: {"force_multiplier": 2.6, "rope_length": 220, "grav": 0.8},
    4: {"force_multiplier": 2.9, "rope_length": 220, "grav": 0.85},
    5: {"force_multiplier": 3.1, "rope_length": 200, "grav": 0.9},
    6: {"force_multiplier": 3.4, "rope_length": 200, "grav": 0.95},
    7: {"force_multiplier": 3.8, "rope_length": 200, "grav": 1.0},
    8: {"force_multiplier": 4.3, "rope_length": 180, "grav": 1.1},
    9: {"force_multiplier": 4.6, "rope_length": 180, "grav": 1.2},
    10: {"force_multiplier": 5, "rope_length": 180, "grav": 1.3},
}

def draw_text_with_outline(surface, text, font, x, y, color, outline_color=(0, 0, 0), outline_width=2):
    """Vẽ chữ có viền đen"""
    for dx in [-outline_width, 0, outline_width]:
        for dy in [-outline_width, 0, outline_width]:
            if dx != 0 or dy != 0:
                outline_surface = font.render(text, True, outline_color)
                surface.blit(outline_surface, (x + dx, y + dy))
    
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
        self.x = (800 // 2) + rope_length * sin(self.angle) - (self.width // 2)
        self.y = origin_y + rope_length * cos(self.angle)
        
        self.speed = 0
        self.acceleration = 0
        self.state = "swinging"

    def swing(self, camera_offset=0):
        origin_y = 50 - camera_offset
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
                    
                    offset = abs(self.xlast - tower_left)
                    overlap_left = max(block_left, tower_left)
                    overlap_right = min(block_right, tower_right)
                    overlap_width = overlap_right - overlap_left
                    
                    new_width = self.width
                    
                    if offset <= 15:
                        new_width = min(tower_width + 10, 300)
                        self.xlast = tower_left - (new_width - tower_width) / 2
                        self.width = new_width
                        
                        block_path = os.path.join(BASE_DIR, "assets", "block.png")
                        original_image = pygame.image.load(block_path)
                        self.image = pygame.transform.scale(original_image, (self.width, self.height))
                        
                        points = 100
                    elif offset <= 25:
                        points = 50
                        new_width = self.width
                    else:
                        if current_level >= 7:
                            new_width = int(overlap_width)
                            # Kiểm tra width tối thiểu để tránh game over sớm
                            if new_width < 50:
                                self.state = "failed"
                                return {"points": -1, "new_width": self.width}
                            
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

    def draw(self, camera_offset=0):
        draw_y = self.y + camera_offset
        
        if hasattr(self, 'xlast') and self.state in ["falling", "failed"]:
            screen.blit(self.image, (self.xlast, draw_y))
        else:
            screen.blit(self.image, (self.x, draw_y))
        
        if self.state == "swinging":
            origin_on_screen = (400, 50)
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
    board_surface = pygame.Surface((250, 160))
    board_surface.fill((40, 40, 70))
    
    pygame.draw.rect(board_surface, (255, 215, 0), (0, 0, 250, 160), 4)
    pygame.draw.rect(board_surface, (200, 170, 0), (4, 4, 242, 152), 2)
    
    screen.blit(board_surface, (540, 10))
    
    draw_text_with_outline(screen, "BANG DIEM", font_large, 575, 20, (255, 255, 100))
    
    y_offset = 60
    
    draw_text_with_outline(screen, f"Level: {level}", font_small, 555, y_offset, (150, 200, 255))
    y_offset += 30
    
    draw_text_with_outline(screen, f"Diem: {score}", font_small, 555, y_offset, (255, 255, 100))
    y_offset += 30
    
    difficulty_level = min(level, 10)
    draw_text_with_outline(screen, f"Do kho: {difficulty_level}/10", font_small, 555, y_offset, (255, 150, 255))
    y_offset += 30
    
    if combo > 1:
        draw_text_with_outline(screen, f"x{combo} COMBO!", font_small, 555, y_offset, (255, 100, 100))

def adjust_difficulty(level):
    global force, rope_length, grav
    difficulty_level = min(level, 10)
    config = DIFFICULTY_LEVELS[difficulty_level]
    force = -0.001 * config["force_multiplier"]
    rope_length = config["rope_length"]
    grav = config["grav"]

def pause_screen(screen, font_large, font_small, background, tower, block):
    """Màn hình tạm dừng game"""
    paused = True
    
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    return "resume"
                elif event.key == pygame.K_r:
                    return "restart"
                elif event.key == pygame.K_q:
                    return "quit"
        
        # Vẽ game ở phía sau
        screen.fill((135, 206, 235))
        screen.blit(background, (0, 0))
        tower.draw()
        block.draw(tower.camera_y)
        
        # Overlay mờ
        overlay = pygame.Surface((800, 600))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Panel pause
        pause_surface = pygame.Surface((420, 320))
        pause_surface.fill((30, 30, 50))
        
        pygame.draw.rect(pause_surface, (100, 150, 255), (0, 0, 420, 320), 6)
        pygame.draw.rect(pause_surface, (70, 120, 200), (6, 6, 408, 308), 3)
        
        screen.blit(pause_surface, (190, 140))
        
        # Text
        draw_text_with_outline(screen, "TAM DUNG", font_large, 320, 160, (255, 255, 150))
        
        y = 230
        draw_text_with_outline(screen, "P/ESC - Tiep tuc", font_small, 270, y, (255, 255, 255))
        y += 40
        
        draw_text_with_outline(screen, "R - Choi lai", font_small, 270, y, (150, 255, 150))
        y += 40
        
        draw_text_with_outline(screen, "Q - Thoat game", font_small, 270, y, (255, 150, 150))
        y += 60
        
        draw_text_with_outline(screen, "Nhan phim de lua chon...", font_small, 250, y, (200, 200, 200))
        
        pygame.display.flip()
        clock.tick(30)

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
        
        game_over_surface = pygame.Surface((420, 280))
        game_over_surface.fill((30, 30, 50))
        
        pygame.draw.rect(game_over_surface, (255, 80, 80), (0, 0, 420, 280), 6)
        pygame.draw.rect(game_over_surface, (200, 50, 50), (6, 6, 408, 268), 3)
        
        screen.blit(game_over_surface, (190, 160))
        
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
    panel_surface = pygame.Surface((250, 110))
    panel_surface.fill((50, 50, 90))
    pygame.draw.rect(panel_surface, (100, 200, 255), (0, 0, 250, 110), 3)
    screen.blit(panel_surface, (10, 10))
    
    draw_text_with_outline(screen, "SPACE - Tha khoi", font_small, 25, 25, (255, 255, 255))
    draw_text_with_outline(screen, "P/ESC - Tam dung", font_small, 25, 50, (200, 200, 255))
    
    if level >= 4:
        draw_text_with_outline(screen, "Can than voi gio!", font_small, 25, 75, (150, 200, 255))
    else:
        draw_text_with_outline(screen, "Dat chinh xac = bonus!", font_small, 25, 75, (255, 255, 100))

def draw_wind_indicator(screen, font_small, level, wind_force, wind_direction):
    """Vẽ chỉ báo gió vuông"""
    if level < 4:
        return
    
    panel_surface = pygame.Surface((180, 50))
    panel_surface.fill((60, 100, 180))
    pygame.draw.rect(panel_surface, (100, 150, 255), (0, 0, 180, 50), 3)
    screen.blit(panel_surface, (280, 10))
    
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
    current_block_width = 250
    block = Block(tower.camera_y, tower_size=len(tower.blocks), width=current_block_width)
    
    score = 0
    level = 1
    combo = 0
    
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
    
    # Khởi tạo độ khó ban đầu
    adjust_difficulty(level)
    
    while running:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if block.state == "swinging":
                        block.drop(tower, current_level=level, wind_force=wind_force)
                
                elif event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    pause_action = pause_screen(screen, font_large, font_small, background, tower, block)
                    if pause_action == "quit":
                        running = False
                        continue
                    elif pause_action == "restart":
                        tower = Tower()
                        current_block_width = 250
                        block = Block(tower.camera_y, tower_size=len(tower.blocks), width=current_block_width)
                        score = 0
                        level = 1
                        combo = 0
                        wind_force = 0
                        wind_direction = 1
                        wind_timer = 0
                        adjust_difficulty(level)

        # Cập nhật gió (bắt đầu từ level 4)
        if level >= 4:
            wind_timer += 1
            if wind_timer >= wind_change_interval:
                wind_timer = 0
                wind_direction *= -1
            
            wind_intensity = min(level - 3, 7) * 0.3
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
                        current_block_width = 250
                        block = Block(tower.camera_y, tower_size=len(tower.blocks), width=current_block_width)
                        score = 0
                        level = 1
                        combo = 0
                        wind_force = 0
                        wind_direction = 1
                        wind_timer = 0
                        adjust_difficulty(level)
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