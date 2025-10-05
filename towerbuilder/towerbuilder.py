# -*- coding: utf-8 -*-
import pygame
import os
from math import sin, cos, radians

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Simple Tower Game")

# Tải hình nền
BASE_DIR = os.path.dirname(__file__)
background_path = os.path.join(BASE_DIR, "assets", "background.png")
background = pygame.image.load(background_path)
background = pygame.transform.scale(background, (800, 600))

# Thiết lập game
grav = 0.5
rope_length = 120
force = -0.001
clock = pygame.time.Clock()

# Hiệu ứng gió
wind_force = 0
wind_direction = 1  # 1 = phải, -1 = trái
wind_timer = 0
wind_change_interval = 180  # Đổi hướng gió mỗi 3 giây (180 frames)

# Cấu hình độ khó (tăng tốc độ swing mạnh hơn)
DIFFICULTY_LEVELS = {
    1: {"force_multiplier": 2.0, "rope_length": 120, "grav": 0.7},
    2: {"force_multiplier": 2.3, "rope_length": 130, "grav": 0.8},
    3: {"force_multiplier": 2.5, "rope_length": 140, "grav": 0.9},
    4: {"force_multiplier": 2.8, "rope_length": 150, "grav": 1.0},
    5: {"force_multiplier": 3.1, "rope_length": 160, "grav": 1.2},
}

class Block(pygame.sprite.Sprite):
    def __init__(self, camera_offset=0, tower_size=0, width=80):
        pygame.sprite.Sprite.__init__(self)
        self.width = width  # Cho phép width thay đổi
        self.height = 70 # lên 70
        block_path = os.path.join(BASE_DIR, "assets", "block.png")
        original_image = pygame.image.load(block_path)
        self.image = pygame.transform.scale(original_image, (self.width, self.height))
        
        # Khởi tạo góc xen kẽ trái/phải
        if tower_size % 2 == 0:
            self.angle = radians(-45)
        else:
            self.angle = radians(45)
        
        # Vị trí ban đầu
        origin_y = 50 - camera_offset
        self.x = 370 + rope_length * sin(self.angle)
        self.y = origin_y + rope_length * cos(self.angle)
        
        self.speed = 0
        self.acceleration = 0
        self.state = "swinging"

    def swing(self, camera_offset=0):
        origin_y = 50 - camera_offset
        self.x = 370 + rope_length * sin(self.angle)
        self.y = origin_y + rope_length * cos(self.angle)
        self.angle += self.speed
        self.acceleration = sin(self.angle) * force
        self.speed += self.acceleration

    def drop(self, tower, current_level=1, wind_force=0):
        if self.state == "swinging":
            self.state = "falling"
            self.xlast = self.x
            self.wind_drift = 0  # Khởi tạo drift do gió
            
        # Block đầu tiên luôn đặt trên mặt đất
        if not tower.blocks:
            if self.y >= 540:
                self.state = "landed"
                self.y = 540
                self.xlast = self.x
                return {"points": 50, "new_width": self.width}
        else:
            # Block tiếp theo - kiểm tra va chạm với tháp
            if self.y >= tower.get_top_y() - self.height:
                tower_left = tower.blocks[-1]['x']
                tower_right = tower_left + self.width
                tower_width = tower.blocks[-1]['width']
                block_left = self.xlast
                block_right = self.xlast + self.width
                
                # Kiểm tra có chồng lên không
                if block_right > tower_left and block_left < tower_right:
                    # Chồng lên được - landed thành công
                    self.state = "landed"
                    self.y = tower.get_top_y() - self.height
                    
                    # Tính offset và điểm
                    offset = abs(self.xlast - tower_left)
                    
                    # Từ level 5 trở đi: cắt khối
                    new_width = self.width
                    if current_level >= 5:
                        # Tính phần chồng lên
                        overlap_left = max(block_left, tower_left)
                        overlap_right = min(block_right, tower_right)
                        overlap_width = overlap_right - overlap_left
                        
                        # Perfect alignment (offset <= 8px) - TĂNG WIDTH! (Tăng từ 3px lên 8px)
                        if offset <= 8:
                            # Tăng width lên 5px, tối đa 120px
                            new_width = min(tower_width + 5, 120)
                            self.xlast = tower_left - 2.5  # Căn giữa để mở rộng đều 2 bên
                            self.width = new_width
                            
                            # Cập nhật image với width mới
                            block_path = os.path.join(BASE_DIR, "assets", "block.png")
                            original_image = pygame.image.load(block_path)
                            self.image = pygame.transform.scale(original_image, (self.width, self.height))
                            
                            points = 100
                        else:
                            # Cắt khối - chỉ giữ lại phần chồng
                            new_width = int(overlap_width)
                            self.xlast = overlap_left
                            
                            # Cập nhật width và image của khối hiện tại
                            self.width = new_width
                            block_path = os.path.join(BASE_DIR, "assets", "block.png")
                            original_image = pygame.image.load(block_path)
                            self.image = pygame.transform.scale(original_image, (self.width, self.height))
                            
                            # Tính điểm dựa trên độ chính xác
                            if offset <= 12:
                                points = 50
                            elif offset <= 16:
                                points = 25
                            else:
                                points = 10
                        
                        return {"points": points, "new_width": new_width}
                    else:
                        # Level < 5: Perfect tăng width nhẹ
                        if offset <= 8:  # Tăng từ 3px lên 8px
                            new_width = min(self.width + 3, 120)  # Tăng 3px, max 120px
                            points = 100
                        elif offset <= 12:
                            points = 50
                        elif offset <= 16:
                            points = 25
                        else:
                            points = 10
                        return {"points": points, "new_width": new_width}
                else:
                    # KHÔNG chồng lên = GAME OVER
                    self.state = "failed"
                    return {"points": -1, "new_width": self.width}

        # Áp dụng trọng lực và gió
        if self.state == "falling":
            self.speed += grav
            self.y += self.speed
            
            # Áp dụng hiệu ứng gió - đẩy khối sang ngang
            if hasattr(self, 'wind_drift'):
                self.wind_drift += wind_force * 0.3
                self.xlast += self.wind_drift
                self.wind_drift *= 0.95  # Giảm dần
        return None

    def draw(self, camera_offset=0):
        draw_y = self.y + camera_offset
        
        if hasattr(self, 'xlast') and self.state in ["falling", "failed"]:
            screen.blit(self.image, (self.xlast, draw_y))
        else:
            screen.blit(self.image, (self.x, draw_y))
        
        if self.state == "swinging":
            origin_on_screen = (400, 50)
            pygame.draw.line(screen, (0, 0, 0), origin_on_screen, (self.x + self.width//2, draw_y), 2)
            pygame.draw.circle(screen, (200, 0, 0), origin_on_screen, 5)

class Tower:
    def __init__(self):
        self.blocks = []
        self.camera_y = 0
        self.target_camera_y = 0
        self.scrolling = False
        self.height = 0
        self.scroll_threshold = 450
        self.shake_offset = 0  # Độ lệch do gió
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
            return 540  # Cập nhật để khớp với vị trí khối đầu tiên
        return min(block['y'] for block in self.blocks)
    
    def update_camera(self):
        if abs(self.target_camera_y - self.camera_y) > 0.5:
            self.scrolling = True
            self.camera_y += (self.target_camera_y - self.camera_y) * 0.15
        else:
            self.camera_y = self.target_camera_y
            self.scrolling = False
    
    def update_wind(self, wind_force):
        """Cập nhật hiệu ứng gió làm tháp lắc lư"""
        # Áp dụng lực gió
        self.shake_speed += wind_force * 0.02
        
        # Lực đàn hồi kéo về vị trí ban đầu
        self.shake_speed -= self.shake_offset * 0.05
        
        # Giảm tốc độ (ma sát)
        self.shake_speed *= 0.95
        
        # Cập nhật vị trí
        self.shake_offset += self.shake_speed
        
        # Giới hạn độ lệch tối đa
        max_shake = 15
        if abs(self.shake_offset) > max_shake:
            self.shake_offset = max_shake if self.shake_offset > 0 else -max_shake
            self.shake_speed *= -0.5  # Đảo chiều khi chạm giới hạn

    def draw(self):
        for block in self.blocks:
            # Vẽ với hiệu ứng lắc theo gió
            screen.blit(block['image'], (block['x'] + self.shake_offset, block['y'] + self.camera_y))

def draw_scoreboard(screen, font_large, font_small, score, level, blocks_placed, combo):
    board_surface = pygame.Surface((250, 180))
    board_surface.set_alpha(200)
    board_surface.fill((50, 50, 80))
    pygame.draw.rect(board_surface, (255, 215, 0), (0, 0, 250, 180), 3)
    screen.blit(board_surface, (540, 10))
    
    title = font_large.render("BẢNG ĐIỂM", True, (255, 255, 255))
    screen.blit(title, (555, 20))
    
    level_text = font_small.render(f"Level: {level}", True, (255, 255, 255))
    screen.blit(level_text, (555, 55))
    
    score_text = font_small.render(f"Điểm: {score}", True, (255, 215, 0))
    screen.blit(score_text, (555, 80))
    
    blocks_text = font_small.render(f"Khối: {blocks_placed}", True, (100, 255, 100))
    screen.blit(blocks_text, (555, 105))
    
    difficulty_level = min(level, 5)
    difficulty_text = font_small.render(f"Độ khó: {'★' * difficulty_level}", True, (255, 100, 255))
    screen.blit(difficulty_text, (555, 130))
    
    if combo > 1:
        combo_text = font_small.render(f"Combo x{combo}!", True, (255, 100, 100))
        screen.blit(combo_text, (555, 155))

def adjust_difficulty(level):
    global force, rope_length, grav
    difficulty_level = min(level, 5)
    config = DIFFICULTY_LEVELS[difficulty_level]
    force = -0.001 * config["force_multiplier"]
    rope_length = config["rope_length"]
    grav = config["grav"]

def game_over_screen(screen, font_large, font_small, background, tower, block, score, blocks_placed, level):
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
        
        game_over_surface = pygame.Surface((400, 300))
        game_over_surface.set_alpha(230)
        game_over_surface.fill((20, 20, 40))
        pygame.draw.rect(game_over_surface, (255, 50, 50), (0, 0, 400, 300), 5)
        screen.blit(game_over_surface, (200, 150))
        
        game_over_text = font_large.render("GAME OVER!", True, (255, 50, 50))
        screen.blit(game_over_text, (300, 180))
        
        final_score_text = font_small.render(f"Điểm cuối: {score}", True, (255, 255, 255))
        screen.blit(final_score_text, (280, 230))
        
        blocks_text = font_small.render(f"Số khối xếp: {blocks_placed}", True, (255, 255, 255))
        screen.blit(blocks_text, (260, 260))
        
        level_text = font_small.render(f"Level đạt: {level}", True, (255, 255, 255))
        screen.blit(level_text, (280, 290))
        
        restart_text = font_small.render("Nhấn R để chơi lại hoặc ESC để thoát", True, (255, 255, 100))
        screen.blit(restart_text, (220, 350))
        
        pygame.display.flip()
        clock.tick(60)

def main():
    global force, rope_length, grav, wind_force, wind_direction, wind_timer
    running = True
    tower = Tower()
    current_block_width = 100  # Tăng width từ 60 lên 80
    block = Block(tower.camera_y, tower_size=len(tower.blocks), width=current_block_width)
    
    score = 0
    level = 1
    blocks_placed = 0
    combo = 0
    force = -0.002  # Tăng force ban đầu để khối swing nhanh hơn
    
    # Khởi tạo gió
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
            font_large = pygame.font.SysFont(font_name, 26, bold=True)
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

        # Cập nhật gió (chỉ từ level 3 trở đi)
        if level >= 3:
            wind_timer += 1
            if wind_timer >= wind_change_interval:
                wind_timer = 0
                wind_direction *= -1  # Đổi hướng gió
            
            # Tính lực gió (tăng dần theo level)
            wind_intensity = min(level - 2, 5) * 0.3  # Level 3: 0.3, Level 5+: 0.9
            wind_force = wind_direction * wind_intensity
        else:
            wind_force = 0
        
        # Cập nhật hiệu ứng gió cho tháp
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
                    restart = game_over_screen(screen, font_large, font_small, background, tower, block, score, blocks_placed, level)
                    if restart:
                        tower = Tower()
                        current_block_width = 80  # Reset width về 80
                        block = Block(tower.camera_y, tower_size=len(tower.blocks), width=current_block_width)
                        score = 0
                        level = 1
                        blocks_placed = 0
                        combo = 0
                        force = -0.002  # Reset với tốc độ nhanh hơn
                        rope_length = 120
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
                    current_block_width = new_width  # Cập nhật width cho khối tiếp theo
        elif block.state == "landed":
            tower.add_block(block)
            blocks_placed += 1
            
            if blocks_placed % 3 == 0:  # Tăng độ khó nhanh hơn (mỗi 3 khối thay vì 5)
                level += 1
                adjust_difficulty(level)
            
            # Tạo khối mới với width được cập nhật
            block = Block(tower.camera_y, tower_size=len(tower.blocks), width=current_block_width)
            
        tower.update_camera()

        # Vẽ
        screen.fill((135, 206, 235))
        screen.blit(background, (0, 0))
        tower.draw()
        block.draw(tower.camera_y)
        draw_scoreboard(screen, font_large, font_small, score, level, blocks_placed, combo)
        
        text = font_small.render("Nhấn SPACE để thả khối", True, (0, 0, 0))
        screen.blit(text, (10, 10))
        
        # Hiển thị chỉ báo gió (từ level 3+)
        if level >= 3:
            wind_text = "🌬️ Gió: "
            if wind_direction > 0:
                wind_text += "→→→" if abs(wind_force) > 0.5 else "→→"
            else:
                wind_text += "←←←" if abs(wind_force) > 0.5 else "←←"
            wind_indicator = font_small.render(wind_text, True, (100, 100, 255))
            screen.blit(wind_indicator, (10, 40))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()