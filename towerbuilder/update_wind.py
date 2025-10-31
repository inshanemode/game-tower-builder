# -*- coding: utf-8 -*-
import json
import pygame
import os
import time
import random
from math import sin, cos, radians

# Import Firebase (comment dòng này nếu chưa setup Firebase)
try:
    from firebase_config import firebase_auth
    from login_screen import show_login_screen
    FIREBASE_ENABLED = True
except ImportError:
    FIREBASE_ENABLED = False
    print("Firebase chưa được cấu hình. Chỉ dùng leaderboard local.")

# === CẤU HÌNH MỚI: 600x800 ===
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
GROUND_Y = int(0.7 * SCREEN_HEIGHT)        # ~560
SCROLL_THRESHOLD = int(0.625 * SCREEN_HEIGHT)  # ~500

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tower Building Game")

# Tải hình nền
BASE_DIR = os.path.dirname(__file__)
background1_path = os.path.join(BASE_DIR, "assets", "background1.png")
background2_path = os.path.join(BASE_DIR, "assets", "background2.png")

# Load background1 (dưới đất)
if os.path.exists(background1_path):
    background1 = pygame.image.load(background1_path)
    background1 = pygame.transform.scale(background1, (SCREEN_WIDTH, SCREEN_HEIGHT))
else:
    print("⚠ Không tìm thấy background1.png, tạo background mặc định")
    background1 = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    for y in range(SCREEN_HEIGHT):
        color_value = int(135 + (y / SCREEN_HEIGHT) * 50)
        pygame.draw.line(background1, (135, 206, color_value), (0, y), (SCREEN_WIDTH, y))

# Load background2 (trên cao)
if os.path.exists(background2_path):
    background2 = pygame.image.load(background2_path)
    background2 = pygame.transform.scale(background2, (SCREEN_WIDTH, SCREEN_HEIGHT))
    print("✓ Đã tải background2.png")
else:
    print("⚠ Không tìm thấy background2.png, dùng background1")
    background2 = background1.copy()

pygame.mixer.init()
try:
    music_path = os.path.join(BASE_DIR, "assets", "basicsong.mp3")
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(-1)
    print("✓ Đã bật nhạc nền")
except Exception as e:
    print(f"⚠ Không tải được nhạc: {e}")

# Load âm thanh perfect
perfect_sound = None
try:
    perfect_sound_path = os.path.join(BASE_DIR, "assets", "land.mp3")
    perfect_sound = pygame.mixer.Sound(perfect_sound_path)
    perfect_sound.set_volume(0.1)
    print("✓ Đã tải âm thanh perfect")
except Exception as e:
    print(f"⚠ Không tải được âm thanh perfect: {e}")

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

# Cấu hình độ khó
DIFFICULTY_LEVELS = {
    1: {"force_multiplier": 2.0, "rope_length": 250, "grav": 0.7},
    2: {"force_multiplier": 2.3, "rope_length": 250, "grav": 0.75},
    3: {"force_multiplier": 2.6, "rope_length": 220, "grav": 0.8},
    4: {"force_multiplier": 2.9, "rope_length": 220, "grav": 0.85},
    5: {"force_multiplier": 3.1, "rope_length": 200, "grav": 0.9},
    6: {"force_multiplier": 3.4, "rope_length": 200, "grav": 0.95},
    7: {"force_multiplier": 4, "rope_length": 200, "grav": 1.0},
    8: {"force_multiplier": 5, "rope_length": 180, "grav": 1.1},
    9: {"force_multiplier": 6, "rope_length": 180, "grav": 1.2},
    10: {"force_multiplier": 8, "rope_length": 180, "grav": 1.3},
}

def draw_backgrounds(camera_offset):
    bg_height = SCREEN_HEIGHT
    screen.blit(background1, (0, camera_offset))
    if camera_offset > 0:
        start_y = camera_offset - bg_height
        num_bg2 = int(camera_offset // bg_height) + 2
        for i in range(num_bg2):
            bg2_y = start_y - (i * bg_height)
            screen.blit(background2, (0, bg2_y))

def draw_text_with_outline(surface, text, font, x, y, color, outline_color=(0, 0, 0), outline_width=2):
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
        self.height = width
        block_number = random.randint(1, 4)
        block_path = os.path.join(BASE_DIR, "assets", f"normal{block_number}.png")
        original_image = pygame.image.load(block_path)
        self.image = pygame.transform.scale(original_image, (self.width, self.height))
        if tower_size % 2 == 0:
            self.angle = radians(-45)
        else:
            self.angle = radians(45)
        origin_y = 100 - camera_offset
        self.x = (SCREEN_WIDTH // 2) + rope_length * sin(self.angle) - (self.width // 2)
        self.y = origin_y + rope_length * cos(self.angle)
        self.speed = 0
        self.acceleration = 0
        self.state = "swinging"

    def swing(self, camera_offset=0):
        origin_y = 100 - camera_offset
        self.x = (SCREEN_WIDTH // 2) + rope_length * sin(self.angle) - (self.width // 2)
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
            if self.y >= GROUND_Y:
                self.state = "landed"
                self.y = GROUND_Y
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
                    MIN_WIDTH = 40
                    new_width = self.width
                    if offset <= 15:
                        new_width = min(tower_width + 10, 150)
                        self.xlast = tower_left - (new_width - tower_width) / 2
                        self.width = new_width
                        self.height = new_width
                        block_number = random.randint(1, 4)
                        block_path = os.path.join(BASE_DIR, "assets", f"perfect{block_number}.png")
                        original_image = pygame.image.load(block_path)
                        self.image = pygame.transform.scale(original_image, (self.width, self.height))
                        if perfect_sound:
                            perfect_sound.play()
                        points = 100
                    elif offset <= 25:
                        points = 50
                        block_number = random.randint(1, 4)
                        block_path = os.path.join(BASE_DIR, "assets", f"normal{block_number}.png")
                        original_image = pygame.image.load(block_path)
                        self.image = pygame.transform.scale(original_image, (self.width, self.height))
                    else:
                        points = 25
                        # === CẮT KHỐI CHỈ TỪ LEVEL 7 ===
                        if current_level >= 7:
                            SHRINK_AMOUNT = 20
                            new_width = max(self.width - SHRINK_AMOUNT, MIN_WIDTH)
                            self.width = new_width
                            self.height = new_width
                            self.y = tower.get_top_y() - self.height
                            block_number = random.randint(1, 4)
                            block_path = os.path.join(BASE_DIR, "assets", f"normal{block_number}.png")
                            original_image = pygame.image.load(block_path)
                            self.image = pygame.transform.scale(original_image, (self.width, self.height))
                        else:
                            new_width = self.width
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
        if hasattr(self, 'xlast') and self.state in ["falling", "failed", "landed"]:
            screen.blit(self.image, (self.xlast, draw_y))
        else:
            screen.blit(self.image, (self.x, draw_y))
        if self.state == "swinging":
            origin_on_screen = (SCREEN_WIDTH // 2, 100)
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
        self.scroll_threshold = SCROLL_THRESHOLD
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
            self.height = 970 - self.get_top_y()
        top_y = self.get_top_y()
        if top_y < self.scroll_threshold:
            self.target_camera_y += block.height

    def get_top_y(self):
        if not self.blocks:
            return GROUND_Y
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
    board_surface = pygame.Surface((200, 140))
    board_surface.fill((40, 40, 70))
    pygame.draw.rect(board_surface, (255, 215, 0), (0, 0, 200, 140), 3)
    pygame.draw.rect(board_surface, (200, 170, 0), (3, 3, 194, 134), 2)
    scoreboard_x = SCREEN_WIDTH - 210
    scoreboard_y = 10
    screen.blit(board_surface, (scoreboard_x, scoreboard_y))
    draw_text_with_outline(screen, "BANG DIEM", font_large, scoreboard_x + 35, scoreboard_y + 10, (255, 255, 100))
    y_offset = scoreboard_y + 50
    draw_text_with_outline(screen, f"Level: {level}", font_small, scoreboard_x + 15, y_offset, (150, 200, 255))
    y_offset += 25
    draw_text_with_outline(screen, f"Diem: {score}", font_small, scoreboard_x + 15, y_offset, (255, 255, 100))
    y_offset += 25
    if level <= 10:
        draw_text_with_outline(screen, f"Do kho: {level}/10", font_small, scoreboard_x + 15, y_offset, (255, 150, 255))
    else:
        draw_text_with_outline(screen, f"Do kho: MAX+{level-10}", font_small, scoreboard_x + 15, y_offset, (255, 100, 100))
    y_offset += 25
    if combo > 1:
        draw_text_with_outline(screen, f"x{combo} COMBO!", font_small, scoreboard_x + 15, y_offset, (255, 100, 100))

def adjust_difficulty(level):
    global force, rope_length, grav
    if level <= 10:
        config = DIFFICULTY_LEVELS[level]
        force = -0.001 * config["force_multiplier"]
        rope_length = config["rope_length"]
        grav = config["grav"]
    else:
        base_config = DIFFICULTY_LEVELS[10]
        extra_levels = level - 10
        force_multiplier = base_config["force_multiplier"] + extra_levels
        force = -0.001 * force_multiplier
        rope_length = base_config["rope_length"]
        grav = base_config["grav"]

def pause_screen(screen, font_large, font_small, tower, block):
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
        screen.fill((135, 206, 235))
        draw_backgrounds(tower.camera_y)
        tower.draw()
        block.draw(tower.camera_y)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        menu_width = int(500 * 0.78)
        menu_height = int(350 * 0.78)
        menu_x = (SCREEN_WIDTH - menu_width) // 2
        menu_y = 280
        pause_surface = pygame.Surface((menu_width, menu_height))
        pause_surface.fill((30, 30, 50))
        pygame.draw.rect(pause_surface, (100, 150, 255), (0, 0, menu_width, menu_height), 4)
        pygame.draw.rect(pause_surface, (70, 120, 200), (4, 4, menu_width-8, menu_height-8), 2)
        screen.blit(pause_surface, (menu_x, menu_y))
        draw_text_with_outline(screen, "TAM DUNG", font_large, menu_x + 80, menu_y + 20, (255, 255, 150))
        y = menu_y + 80
        draw_text_with_outline(screen, "P/ESC - Tiep tuc", font_small, menu_x + 60, y, (255, 255, 255))
        y += 35
        draw_text_with_outline(screen, "R - Choi lai", font_small, menu_x + 60, y, (150, 255, 150))
        y += 35
        draw_text_with_outline(screen, "Q - Thoat game", font_small, menu_x + 60, y, (255, 150, 150))
        y += 50
        draw_text_with_outline(screen, "Nhan phim de lua chon...", font_small, menu_x + 40, y, (200, 200, 200))
        pygame.display.flip()
        clock.tick(30)

def game_over_screen(screen, font_large, font_small, tower, block, score, level):
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "restart"
                elif event.key == pygame.K_l:
                    return "leaderboard"
                elif event.key == pygame.K_ESCAPE:
                    return "menu"
        screen.fill((135, 206, 235))
        draw_backgrounds(tower.camera_y)
        tower.draw()
        block.draw(tower.camera_y)
        menu_width = int(500 * 0.78)
        menu_height = int(400 * 0.78)
        menu_x = (SCREEN_WIDTH - menu_width) // 2
        menu_y = 250
        go_surface = pygame.Surface((menu_width, menu_height))
        go_surface.fill((30, 30, 50))
        pygame.draw.rect(go_surface, (255, 80, 80), (0, 0, menu_width, menu_height), 4)
        pygame.draw.rect(go_surface, (200, 50, 50), (4, 4, menu_width-8, menu_height-8), 2)
        screen.blit(go_surface, (menu_x, menu_y))
        draw_text_with_outline(screen, "GAME OVER!", font_large, menu_x + 70, menu_y + 20, (255, 100, 100))
        y = menu_y + 80
        draw_text_with_outline(screen, f"Diem cuoi: {score}", font_small, menu_x + 80, y, (255, 255, 100))
        y += 45
        draw_text_with_outline(screen, f"Level dat: {level}", font_small, menu_x + 80, y, (150, 200, 255))
        y += 55
        if FIREBASE_ENABLED and firebase_auth.is_logged_in():
            draw_text_with_outline(screen, "Diem da luu online!", font_small, menu_x + 60, y, (150, 255, 150))
        else:
            draw_text_with_outline(screen, "Diem da luu local!", font_small, menu_x + 65, y, (200, 200, 255))
        y += 55
        draw_text_with_outline(screen, "R - Choi lai", font_small, menu_x + 80, y, (255, 255, 150))
        y += 40
        draw_text_with_outline(screen, "L - Xem bang xep hang", font_small, menu_x + 30, y, (255, 200, 100))
        y += 40
        draw_text_with_outline(screen, "ESC - Ve menu", font_small, menu_x + 80, y, (255, 200, 200))
        pygame.display.flip()
        clock.tick(60)

def draw_instruction_panel(screen, font_small, level):
    panel_surface = pygame.Surface((190, 100))
    panel_surface.fill((50, 50, 90))
    pygame.draw.rect(panel_surface, (100, 200, 255), (0, 0, 190, 100), 2)
    screen.blit(panel_surface, (10, 10))
    draw_text_with_outline(screen, "SPACE - Tha khoi", font_small, 20, 25, (255, 255, 255))
    draw_text_with_outline(screen, "P/ESC - Tam dung", font_small, 20, 50, (200, 200, 255))
    if level >= 3:
        draw_text_with_outline(screen, "Can than voi gio!", font_small, 20, 75, (150, 200, 255))
    else:
        draw_text_with_outline(screen, "Dat chinh xac = bonus!", font_small, 20, 75, (255, 255, 100))

def draw_wind_indicator(screen, font_small, level, wind_force, wind_direction):
    """Hiển thị từ level 3"""
    if level < 3:
        return
    panel_surface = pygame.Surface((160, 50))
    panel_surface.fill((60, 100, 180))
    pygame.draw.rect(panel_surface, (100, 150, 255), (0, 0, 160, 50), 2)
    screen.blit(panel_surface, (10, 120))
    wind_text = "Gio: "
    if level >= 5:
        wind_text += "MANH "
        color = (255, 100, 100)
    else:
        wind_text += "Nhe "
        color = (255, 255, 150)
    if wind_direction > 0:
        wind_text += ">>>"
    else:
        wind_text += "<<<"
    draw_text_with_outline(screen, wind_text, font_small, 22, 135, color)

def load_leaderboard(max_entries=10):
    leaderboard_path = os.path.join(BASE_DIR, "leaderboard.json")
    scores = []
    if os.path.exists(leaderboard_path):
        try:
            with open(leaderboard_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    scores = data
        except Exception as e:
            print(f"Lỗi đọc leaderboard: {e}")
            try:
                txt_path = os.path.join(BASE_DIR, "leaderboard.txt")
                if os.path.exists(txt_path):
                    with open(txt_path, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line:
                                try:
                                    scores.append({"username": "Guest", "score": int(line), "level": 0})
                                except ValueError:
                                    continue
            except Exception:
                pass
    scores.sort(key=lambda x: x.get('score', 0), reverse=True)
    return scores[:max_entries]

def save_score_to_leaderboard(score, level=1, username=None, max_entries=10):
    leaderboard_path = os.path.join(BASE_DIR, "leaderboard.json")
    if username is None:
        if FIREBASE_ENABLED and firebase_auth.is_logged_in():
            username = firebase_auth.username
        else:
            username = "Guest"
    scores = load_leaderboard(max_entries=max_entries*2)
    scores.append({"username": username, "score": int(score), "level": int(level)})
    scores.sort(key=lambda x: x.get('score', 0), reverse=True)
    scores = scores[:max_entries]
    try:
        with open(leaderboard_path, "w", encoding="utf-8") as f:
            json.dump(scores, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Lỗi lưu leaderboard: {e}")

def show_leaderboard(screen, font_large, font_small, show_online=False, force_refresh=False):
    waiting = True
    current_tab = "online" if show_online and FIREBASE_ENABLED else "local"
    cached_local = None
    cached_online = None
    last_refresh = 0
    while waiting:
        current_time = time.time()
        if force_refresh or (current_time - last_refresh > 2):
            cached_local = None
            cached_online = None
            last_refresh = current_time
            force_refresh = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                    return "back"
                if FIREBASE_ENABLED:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                        current_tab = "online" if current_tab == "local" else "local"
                        cached_local = None
                        cached_online = None
                if event.key == pygame.K_r:
                    cached_local = None
                    cached_online = None
        screen.fill((135, 206, 235))
        screen.blit(background1, (0, 0))
        lb_width = 546
        lb_height = 624
        lb_x = (SCREEN_WIDTH - lb_width) // 2
        lb_y = (SCREEN_HEIGHT - lb_height) // 2 - 40
        panel = pygame.Surface((lb_width, lb_height))
        panel.fill((30, 30, 50))
        pygame.draw.rect(panel, (255, 215, 0), (0, 0, lb_width, lb_height), 6)
        pygame.draw.rect(panel, (200, 170, 0), (6, 6, lb_width-12, lb_height-12), 3)
        screen.blit(panel, (lb_x, lb_y))
        draw_text_with_outline(screen, "LEADERBOARD", font_large, lb_x + 180, lb_y + 20, (255, 255, 150))
        tab_y = lb_y + 60
        if FIREBASE_ENABLED:
            local_color = (100, 255, 100) if current_tab == "local" else (150, 150, 150)
            draw_text_with_outline(screen, "Local", font_small, lb_x + 50, tab_y, local_color)
            online_color = (100, 150, 255) if current_tab == "online" else (150, 150, 150)
            draw_text_with_outline(screen, "Online", font_small, lb_x + 440, tab_y, online_color)
            draw_text_with_outline(screen, "<- ->: Chuyen tab | R: Tai lai", font_small, lb_x + 130, tab_y, (200, 200, 200))
        else:
            draw_text_with_outline(screen, "R: Tai lai", font_small, lb_x + 220, tab_y, (200, 200, 200))
        if FIREBASE_ENABLED and current_tab == "online":
            status_text = "Online"
            if firebase_auth.is_logged_in():
                status_text += f" - {firebase_auth.username}"
            draw_text_with_outline(screen, status_text, font_small, lb_x + 30, tab_y + 40, (150, 150, 150))
        y = lb_y + 120
        if current_tab == "local":
            if cached_local is None:
                cached_local = load_leaderboard()
            scores = cached_local
            if not scores:
                draw_text_with_outline(screen, "Chua co diem nao", font_small, lb_x + 180, y, (255, 255, 255))
            else:
                for idx, entry in enumerate(scores[:10], start=1):
                    username = entry.get('username', 'Guest')
                    score = entry.get('score', 0)
                    level = entry.get('level', 0)
                    color = (255, 255, 100) if (FIREBASE_ENABLED and firebase_auth.is_logged_in() and username == firebase_auth.username) else (255, 255, 255)
                    text = f"{idx}. {username}: {score} (Lv{level})"
                    draw_text_with_outline(screen, text, font_small, lb_x + 40, y, color)
                    y += 45
        else:
            if FIREBASE_ENABLED:
                if cached_online is None:
                    draw_text_with_outline(screen, "Dang tai...", font_small, lb_x + 220, y, (200, 200, 200))
                    pygame.display.flip()
                    cached_online = firebase_auth.get_leaderboard(10) or []
                leaderboard = cached_online
                if not leaderboard:
                    draw_text_with_outline(screen, "Chua co diem online nao", font_small, lb_x + 160, y, (255, 255, 255))
                    y += 40
                    draw_text_with_outline(screen, "Choi de them diem!", font_small, lb_x + 180, y, (150, 255, 150))
                else:
                    for idx, entry in enumerate(leaderboard, start=1):
                        try:
                            username = entry.get('username', 'Unknown')
                            score = entry.get('score', 0)
                            level = entry.get('level', 0)
                            color = (255, 255, 100) if (firebase_auth.is_logged_in() and username == firebase_auth.username) else (255, 255, 255)
                            text = f"{idx}. {username}: {score} (Lv{level})"
                            draw_text_with_outline(screen, text, font_small, lb_x + 40, y, color)
                            y += 45
                        except Exception as e:
                            print(f"Loi hien thi entry: {e}")
                            continue
        draw_text_with_outline(screen, "ESC/ENTER de quay lai", font_small, lb_x + 150, lb_y + lb_height - 35, (200, 200, 200))
        pygame.display.flip()
        clock.tick(60)

def show_main_menu(screen, font_large, font_small):
    if FIREBASE_ENABLED:
        if firebase_auth.is_logged_in():
            options = ["Choi", "Bang xep hang", "Dang xuat", "Thoat"]
        else:
            options = ["Choi", "Bang xep hang", "Dang nhap", "Thoat"]
    else:
        options = ["Choi", "Bang xep hang", "Thoat"]
    selected = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if FIREBASE_ENABLED:
                        if selected == 0: return "play"
                        elif selected == 1: return "leaderboard"
                        elif selected == 2:
                            if firebase_auth.is_logged_in():
                                firebase_auth.logout()
                                return "menu_refresh"
                            else:
                                return "login"
                        else: return "quit"
                    else:
                        if selected == 0: return "play"
                        elif selected == 1: return "leaderboard"
                        else: return "quit"
        screen.fill((135, 206, 235))
        screen.blit(background1, (0, 0))
        title_panel = pygame.Surface((480, 120))
        title_panel.fill((30, 30, 50))
        pygame.draw.rect(title_panel, (100, 150, 255), (0, 0, 480, 120), 4)
        screen.blit(title_panel, (60, 150))
        draw_text_with_outline(screen, "TOWER BUILDER", font_large, 130, 180, (255, 255, 150))
        menu_panel = pygame.Surface((400, 320))
        menu_panel.fill((30, 30, 50))
        pygame.draw.rect(menu_panel, (100, 150, 255), (0, 0, 400, 320), 4)
        screen.blit(menu_panel, (100, 280))
        y = 320
        for idx, label in enumerate(options):
            color = (255, 255, 150) if idx == selected else (255, 255, 255)
            draw_text_with_outline(screen, label, font_small, 160, y, color)
            y += 50
        if FIREBASE_ENABLED and firebase_auth.is_logged_in():
            draw_text_with_outline(screen, f"Xin chao: {firebase_auth.username}", font_small, 120, 250, (150, 255, 150))
        draw_text_with_outline(screen, "Len/Xuong de chon, Enter de xac nhan", font_small, 110, 620, (200, 200, 200))
        pygame.display.flip()
        clock.tick(60)

def play_game(screen, font_small, font_large):
    global force, rope_length, grav, wind_force, wind_direction, wind_timer
    running = True
    tower = Tower()
    current_block_width = 100
    block = Block(tower.camera_y, tower_size=len(tower.blocks), width=current_block_width)
    score = 0
    level = 1
    combo = 0
    wind_force = 0
    wind_direction = 1
    wind_timer = 0
    wind_change_interval = 180
    level_up_message = ""
    level_up_timer = 0
    adjust_difficulty(level)
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if block.state == "swinging":
                        block.drop(tower, current_level=level, wind_force=wind_force)
                elif event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    pause_action = pause_screen(screen, font_large, font_small, tower, block)
                    if pause_action == "quit":
                        return "menu"
                    elif pause_action == "restart":
                        return "restart"
        # === CƠ CHẾ GIÓ THEO LEVEL ===
        if level >= 5:
            wind_timer += 1
            if wind_timer >= 120:
                wind_direction *= -1
                wind_timer = 0
            wind_force = wind_direction * min(level - 2, 6) * 0.3
        elif level >= 3:
            wind_timer += 1
            if wind_timer >= 180:
                wind_direction *= -1
                wind_timer = 0
            wind_force = wind_direction * 0.4
        else:
            wind_force = 0
            wind_timer = 0

        tower.update_wind(wind_force)

        if block.state == "swinging":
            block.swing(tower.camera_y)
        elif block.state == "falling":
            result = block.drop(tower, current_level=level, wind_force=wind_force)
            if result is not None:
                points = result["points"]
                new_width = result["new_width"]
                if points == -1:
                    block.state = "failed"
                    save_score_to_leaderboard(score, level)
                    if FIREBASE_ENABLED and firebase_auth.is_logged_in():
                        firebase_auth.save_score(score, level)
                    time.sleep(0.5)
                    action = game_over_screen(screen, font_large, font_small, tower, block, score, level)
                    if action == "restart":
                        return "restart"
                    elif action == "leaderboard":
                        return "leaderboard"
                    elif action == "menu":
                        return "menu"
                    else:
                        return "quit"
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
                old_level = level
                level += 1
                adjust_difficulty(level)
                if level == 3:
                    level_up_message = "Level 3: Gio nhe xuat hien!"
                    level_up_timer = 120
                elif level == 5:
                    level_up_message = "Level 5: Gio manh + Bat dau co gio!"
                    level_up_timer = 150
                elif level == 7:
                    level_up_message = "Level 7: Cat khoi khi dat xau!"
                    level_up_timer = 150
            block = Block(tower.camera_y, tower_size=len(tower.blocks), width=current_block_width)

        tower.update_camera()
        screen.fill((135, 206, 235))
        draw_backgrounds(tower.camera_y)
        tower.draw()
        block.draw(tower.camera_y)
        draw_instruction_panel(screen, font_small, level)
        draw_wind_indicator(screen, font_small, level, wind_force, wind_direction)
        draw_scoreboard(screen, font_large, font_small, score, level, combo)

        if level_up_timer > 0:
            msg_surface = pygame.Surface((420, 80))
            msg_surface.set_alpha(220)
            msg_surface.fill((30, 30, 60))
            pygame.draw.rect(msg_surface, (100, 200, 255), (0, 0, 420, 80), 3)
            screen.blit(msg_surface, (SCREEN_WIDTH // 2 - 210, SCREEN_HEIGHT // 2 - 40))
            draw_text_with_outline(
                screen, level_up_message,
                pygame.font.SysFont("Segoe UI", 22, bold=True),
                SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 25,
                (255, 255, 150)
            )
            level_up_timer -= 1

        pygame.display.flip()
    return "menu"

def main():
    global force, rope_length, grav, wind_force, wind_direction, wind_timer
    font_small = None
    font_large = None
    font_names = ["Segoe UI", "Arial Unicode MS", "Microsoft Sans Serif", "Tahoma", "Verdana"]
    for font_name in font_names:
        try:
            font_small = pygame.font.SysFont(font_name, 20)
            font_large = pygame.font.SysFont(font_name, 32, bold=True)
            font_small.render("ắ", True, (255, 255, 255))
            break
        except:
            continue
    if font_small is None:
        font_small = pygame.font.Font(None, 24)
        font_large = pygame.font.Font(None, 36)

    app_running = True
    while app_running:
        action = show_main_menu(screen, font_large, font_small)
        if action == "quit":
            break
        elif action == "menu_refresh":
            continue
        elif action == "login":
            if FIREBASE_ENABLED:
                login_result = show_login_screen(screen, background1, font_small, font_large, firebase_auth)
                if login_result == "quit":
                    break
            continue
        elif action == "leaderboard":
            show_online = FIREBASE_ENABLED and firebase_auth.is_logged_in()
            lb_action = show_leaderboard(screen, font_large, font_small, show_online=show_online, force_refresh=True)
            if lb_action == "quit":
                break
            continue
        elif action == "play":
            while True:
                game_action = play_game(screen, font_small, font_large)
                if game_action == "quit":
                    app_running = False
                    break
                elif game_action == "restart":
                    continue
                elif game_action == "leaderboard":
                    show_online = FIREBASE_ENABLED and firebase_auth.is_logged_in()
                    lb_action = show_leaderboard(screen, font_large, font_small, show_online=show_online, force_refresh=True)
                    if lb_action == "quit":
                        app_running = False
                        break
                    break
                else:
                    break
    pygame.quit()

if __name__ == "__main__":
    main()