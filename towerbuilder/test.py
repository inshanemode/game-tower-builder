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



pygame.init()

screen = pygame.display.set_mode((768, 1024))

pygame.display.set_caption("Tower Building Game")





# Tải hình nền

BASE_DIR = os.path.dirname(__file__)

background1_path = os.path.join(BASE_DIR, "assets", "background1.png")

background2_path = os.path.join(BASE_DIR, "assets", "background2.png")



# Load background1 (dưới đất)

if os.path.exists(background1_path):

    background1 = pygame.image.load(background1_path)

    background1 = pygame.transform.scale(background1, (768, 1024))

else:

    print("⚠ Không tìm thấy background1.png, tạo background mặc định")

    background1 = pygame.Surface((768, 1024))

    for y in range(1024):

        color_value = int(135 + (y / 1024) * 50)

        pygame.draw.line(background1, (135, 206, color_value), (0, y), (768, y))



# Load background2 (trên cao)

if os.path.exists(background2_path):

    background2 = pygame.image.load(background2_path)

    background2 = pygame.transform.scale(background2, (768, 1024))

    print("✓ Đã tải background2.png")

else:

    print("⚠ Không tìm thấy background2.png, dùng background1")

    background2 = background1.copy()



pygame.mixer.init()

try:

    music_path = os.path.join(BASE_DIR, "assets", "basicsong.mp3")

    pygame.mixer.music.load(music_path)

    pygame.mixer.music.set_volume(0.1)  # Âm lượng 30%

    pygame.mixer.music.play(-1)  # Loop vô hạn (-1 = lặp mãi)

    print("✓ Đã bật nhạc nền")

except Exception as e:

    print(f"⚠ Không tải được nhạc: {e}")



# Load âm thanh perfect

perfect_sound = None

try:

    perfect_sound_path = os.path.join(BASE_DIR, "assets", "land.mp3")

    perfect_sound = pygame.mixer.Sound(perfect_sound_path)

    perfect_sound.set_volume(0.1)  # Âm lượng 40%

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



def draw_backgrounds(camera_offset):

    """Vẽ background: background1 ở dưới, background2 lặp lại ở trên"""

    bg_height = 1024

   

    # Background1 chỉ xuất hiện 1 lần ở vị trí ban đầu (dưới đất)

    screen.blit(background1, (0, camera_offset))

   

    # Background2 lặp lại từ vị trí trên background1 trở lên

    if camera_offset > 0:

        # Tính vị trí bắt đầu của background2 đầu tiên

        start_y = camera_offset - bg_height

       

        # Tính số lượng background2 cần vẽ (chuyển sang int)

        num_bg2 = int(camera_offset // bg_height) + 2

       

        # Vẽ background2 lặp lại

        for i in range(num_bg2):

            bg2_y = start_y - (i * bg_height)

            screen.blit(background2, (0, bg2_y))



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

        self.height = width  # Hình vuông: height = width

       

        # Chọn ngẫu nhiên 1 trong 4 ảnh normal

        block_number = random.randint(1, 4)

        block_path = os.path.join(BASE_DIR, "assets", f"normal{block_number}.png")

        original_image = pygame.image.load(block_path)

        self.image = pygame.transform.scale(original_image, (self.width, self.height))

       

        if tower_size % 2 == 0:

            self.angle = radians(-45)

        else:

            self.angle = radians(45)

       

        origin_y = 100 - camera_offset

        self.x = (768 // 2) + rope_length * sin(self.angle) - (self.width // 2)

        self.y = origin_y + rope_length * cos(self.angle)

       

        self.speed = 0

        self.acceleration = 0

        self.state = "swinging"



    def swing(self, camera_offset=0):

        origin_y = 100 - camera_offset

        self.x = (768 // 2) + rope_length * sin(self.angle) - (self.width // 2)

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

            if self.y >= 720:

                self.state = "landed"

                self.y = 720

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

                        new_width = min(tower_width + 10, 150)

                        self.xlast = tower_left - (new_width - tower_width) / 2

                        self.width = new_width

                        self.height = new_width  # Giữ hình vuông

                       

                        # Chọn ngẫu nhiên 1 trong 4 ảnh PERFECT khi đạt perfect

                        block_number = random.randint(1, 4)

                        block_path = os.path.join(BASE_DIR, "assets", f"perfect{block_number}.png")

                        original_image = pygame.image.load(block_path)

                        self.image = pygame.transform.scale(original_image, (self.width, self.height))

                       

                        # Phát âm thanh perfect

                        if perfect_sound:

                            perfect_sound.play()

                       

                        points = 100

                    elif offset <= 25:

                        points = 50

                        new_width = self.width

                        

                        # Chuyển về ảnh normal nếu không đạt perfect

                        block_number = random.randint(1, 4)

                        block_path = os.path.join(BASE_DIR, "assets", f"normal{block_number}.png")

                        original_image = pygame.image.load(block_path)

                        self.image = pygame.transform.scale(original_image, (self.width, self.height))

                    else:

                        # Đặt không chính xác nhưng vẫn chấp nhận - không cắt block

                        points = 25

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

            origin_on_screen = (384, 100)

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

        self.scroll_threshold = 640

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

            return 720

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

   

    screen.blit(board_surface, (500, 20))

   

    draw_text_with_outline(screen, "BANG DIEM", font_large, 535, 30, (255, 255, 100))

   

    y_offset = 70

   

    draw_text_with_outline(screen, f"Level: {level}", font_small, 515, y_offset, (150, 200, 255))

    y_offset += 30

   

    draw_text_with_outline(screen, f"Diem: {score}", font_small, 515, y_offset, (255, 255, 100))

    y_offset += 30

   

    difficulty_level = min(level, 10)

    draw_text_with_outline(screen, f"Do kho: {difficulty_level}/10", font_small, 515, y_offset, (255, 150, 255))

    y_offset += 30

   

    if combo > 1:

        draw_text_with_outline(screen, f"x{combo} COMBO!", font_small, 515, y_offset, (255, 100, 100))



def adjust_difficulty(level):

    global force, rope_length, grav

    difficulty_level = min(level, 10)

    config = DIFFICULTY_LEVELS[difficulty_level]

    force = -0.001 * config["force_multiplier"]

    rope_length = config["rope_length"]

    grav = config["grav"]



def pause_screen(screen, font_large, font_small, tower, block):

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

       

        # Vẽ game ở phía sau với background động

        screen.fill((135, 206, 235))

        draw_backgrounds(tower.camera_y)

        tower.draw()

        block.draw(tower.camera_y)

       

        # Overlay mờ

        overlay = pygame.Surface((768, 1024))

        overlay.set_alpha(180)

        overlay.fill((0, 0, 0))

        screen.blit(overlay, (0, 0))

       

        # Panel pause

        pause_surface = pygame.Surface((500, 350))

        pause_surface.fill((30, 30, 50))

       

        pygame.draw.rect(pause_surface, (100, 150, 255), (0, 0, 500, 350), 6)

        pygame.draw.rect(pause_surface, (70, 120, 200), (6, 6, 488, 338), 3)

       

        screen.blit(pause_surface, (134, 337))

       

        # Text

        draw_text_with_outline(screen, "TAM DUNG", font_large, 290, 365, (255, 255, 150))

       

        y = 445

        draw_text_with_outline(screen, "P/ESC - Tiep tuc", font_small, 260, y, (255, 255, 255))

        y += 40

       

        draw_text_with_outline(screen, "R - Choi lai", font_small, 260, y, (150, 255, 150))

        y += 40

       

        draw_text_with_outline(screen, "Q - Thoat game", font_small, 260, y, (255, 150, 150))

        y += 60

       

        draw_text_with_outline(screen, "Nhan phim de lua chon...", font_small, 215, y, (200, 200, 200))

       

        pygame.display.flip()

        clock.tick(30)



def game_over_screen(screen, font_large, font_small, tower, block, score, level):

    """Màn hình game over với option xem leaderboard"""

    waiting = True

    show_options = True

   

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

       

        game_over_surface = pygame.Surface((500, 400))

        game_over_surface.fill((30, 30, 50))

       

        pygame.draw.rect(game_over_surface, (255, 80, 80), (0, 0, 500, 400), 6)

        pygame.draw.rect(game_over_surface, (200, 50, 50), (6, 6, 488, 388), 3)

       

        screen.blit(game_over_surface, (134, 312))

       

        draw_text_with_outline(screen, "GAME OVER!", font_large, 265, 345, (255, 100, 100))

       

        y = 420

        draw_text_with_outline(screen, f"Diem cuoi: {score}", font_small, 280, y, (255, 255, 100))

        y += 50

       

        draw_text_with_outline(screen, f"Level dat: {level}", font_small, 280, y, (150, 200, 255))

        y += 60

       

        # Hiển thị thông báo lưu điểm

        if FIREBASE_ENABLED and firebase_auth.is_logged_in():

            draw_text_with_outline(screen, "Diem da luu online!", font_small, 245, y, (150, 255, 150))

        else:

            draw_text_with_outline(screen, "Diem da luu local!", font_small, 250, y, (200, 200, 255))

        y += 60

       

        draw_text_with_outline(screen, "R - Choi lai", font_small, 265, y, (255, 255, 150))

        y += 45

       

        draw_text_with_outline(screen, "L - Xem bang xep hang", font_small, 215, y, (255, 200, 100))

        y += 45

       

        draw_text_with_outline(screen, "ESC - Ve menu", font_small, 265, y, (255, 200, 200))

       

        pygame.display.flip()

        clock.tick(60)



def draw_instruction_panel(screen, font_small, level):

    """Vẽ panel hướng dẫn vuông"""

    panel_surface = pygame.Surface((250, 110))

    panel_surface.fill((50, 50, 90))

    pygame.draw.rect(panel_surface, (100, 200, 255), (0, 0, 250, 110), 3)

    screen.blit(panel_surface, (20, 20))

   

    draw_text_with_outline(screen, "SPACE - Tha khoi", font_small, 35, 35, (255, 255, 255))

    draw_text_with_outline(screen, "P/ESC - Tam dung", font_small, 35, 60, (200, 200, 255))

   

    if level >= 4:

        draw_text_with_outline(screen, "Can than voi gio!", font_small, 35, 85, (150, 200, 255))

    else:

        draw_text_with_outline(screen, "Dat chinh xac = bonus!", font_small, 35, 85, (255, 255, 100))



def draw_wind_indicator(screen, font_small, level, wind_force, wind_direction):

    """Vẽ chỉ báo gió vuông"""

    if level < 4:

        return

   

    panel_surface = pygame.Surface((180, 50))

    panel_surface.fill((60, 100, 180))

    pygame.draw.rect(panel_surface, (100, 150, 255), (0, 0, 180, 50), 3)

    screen.blit(panel_surface, (294, 20))

   

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

   

    draw_text_with_outline(screen, wind_text, font_small, 309, 30, color)



def load_leaderboard(max_entries=10):

    """Load leaderboard scores from file, return list of dicts with username and score."""

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

            # Fallback: thử đọc file txt cũ

            try:

                txt_path = os.path.join(BASE_DIR, "leaderboard.txt")

                if os.path.exists(txt_path):

                    with open(txt_path, "r", encoding="utf-8") as f:

                        for line in f:

                            line = line.strip()

                            if line:

                                try:

                                    scores.append({

                                        "username": "Guest",

                                        "score": int(line),

                                        "level": 0

                                    })

                                except ValueError:

                                    continue

            except Exception:

                pass

   

    # Sắp xếp theo điểm giảm dần

    scores.sort(key=lambda x: x.get('score', 0), reverse=True)

    return scores[:max_entries]



def save_score_to_leaderboard(score, level=1, username=None, max_entries=10):

    """Save score with username to leaderboard."""

    leaderboard_path = os.path.join(BASE_DIR, "leaderboard.json")

   

    # Lấy username

    if username is None:

        if FIREBASE_ENABLED and firebase_auth.is_logged_in():

            username = firebase_auth.username

        else:

            username = "Guest"

   

    # Load existing scores

    scores = load_leaderboard(max_entries=max_entries*2)

   

    # Thêm score mới

    scores.append({

        "username": username,

        "score": int(score),

        "level": int(level)

    })

   

    # Sắp xếp và giữ top N

    scores.sort(key=lambda x: x.get('score', 0), reverse=True)

    scores = scores[:max_entries]

   

    # Lưu file

    try:

        with open(leaderboard_path, "w", encoding="utf-8") as f:

            json.dump(scores, f, ensure_ascii=False, indent=2)

    except Exception as e:

        print(f"Lỗi lưu leaderboard: {e}")



def show_leaderboard(screen, font_large, font_small, show_online=False, force_refresh=False):

    """Display leaderboard and wait for user to go back."""

    waiting = True

   

    # Chọn tab (local hoặc online)

    current_tab = "online" if show_online and FIREBASE_ENABLED else "local"

   

    # Cache để tránh load liên tục

    cached_local = None

    cached_online = None

    last_refresh = 0

   

    while waiting:

        # Auto refresh mỗi 2 giây hoặc khi force_refresh

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

                # Tab switching

                if FIREBASE_ENABLED:

                    if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:

                        current_tab = "online" if current_tab == "local" else "local"

                        # Force refresh khi đổi tab

                        cached_local = None

                        cached_online = None

                # Refresh thủ công

                if event.key == pygame.K_r:

                    cached_local = None

                    cached_online = None



        screen.fill((135, 206, 235))

        screen.blit(background1, (0, 0))  # Menu dùng background1



        panel = pygame.Surface((700, 800))

        panel.fill((30, 30, 50))

        pygame.draw.rect(panel, (255, 215, 0), (0, 0, 700, 800), 6)

        pygame.draw.rect(panel, (200, 170, 0), (6, 6, 688, 788), 3)

        screen.blit(panel, (34, 112))



        draw_text_with_outline(screen, "LEADERBOARD", font_large, 280, 140, (255, 255, 150))



        # Tabs

        if FIREBASE_ENABLED:

            # Local tab

            local_color = (100, 255, 100) if current_tab == "local" else (150, 150, 150)

            draw_text_with_outline(screen, "Local", font_small, 100, 200, local_color)

           

            # Online tab

            online_color = (100, 150, 255) if current_tab == "online" else (150, 150, 150)

            draw_text_with_outline(screen, "Online", font_small, 600, 200, online_color)

           

            draw_text_with_outline(screen, "<- ->: Chuyen tab | R: Tai lai", font_small, 215, 200, (200, 200, 200))

        else:

            draw_text_with_outline(screen, "R: Tai lai", font_small, 310, 200, (200, 200, 200))

       

        # Debug info (chỉ hiển thị khi có Firebase)

        if FIREBASE_ENABLED and current_tab == "online":

            status_text = "Online"

            if firebase_auth.is_logged_in():

                status_text += f" - {firebase_auth.username}"

            draw_text_with_outline(screen, status_text, font_small, 80, 240, (150, 150, 150))

       

        # Hiển thị scores

        y = 280

        if current_tab == "local":

            # Load local scores với cache

            if cached_local is None:

                cached_local = load_leaderboard()

           

            scores = cached_local

            if not scores:

                draw_text_with_outline(screen, "Chua co diem nao", font_small, 265, y, (255, 255, 255))

            else:

                for idx, entry in enumerate(scores[:10], start=1):

                    username = entry.get('username', 'Guest')

                    score = entry.get('score', 0)

                    level = entry.get('level', 0)

                   

                    # Highlight nếu là user hiện tại

                    color = (255, 255, 100) if (FIREBASE_ENABLED and

                                               firebase_auth.is_logged_in() and

                                               username == firebase_auth.username) else (255, 255, 255)

                   

                    text = f"{idx}. {username}: {score} (Lv{level})"

                    draw_text_with_outline(screen, text, font_small, 80, y, color)

                    y += 50

        else:

            # Online leaderboard

            if FIREBASE_ENABLED:

                # Load online scores với cache

                if cached_online is None:

                    try:

                        # Hiển thị loading

                        draw_text_with_outline(screen, "Dang tai...", font_small, 310, y, (200, 200, 200))

                        pygame.display.flip()

                       

                        cached_online = firebase_auth.get_leaderboard(10)

                        if cached_online is None:

                            cached_online = []

                    except Exception as e:

                        print(f"Loi load online leaderboard: {e}")

                        cached_online = []

               

                leaderboard = cached_online

                if not leaderboard or len(leaderboard) == 0:

                    draw_text_with_outline(screen, "Chua co diem online nao", font_small, 225, y, (255, 255, 255))

                    y += 40

                    draw_text_with_outline(screen, "Choi de them diem!", font_small, 255, y, (150, 255, 150))

                else:

                    for idx, entry in enumerate(leaderboard, start=1):

                        try:

                            username = entry.get('username', 'Unknown')

                            score = entry.get('score', 0)

                            level = entry.get('level', 0)

                           

                            # Highlight nếu là user hiện tại

                            color = (255, 255, 100) if (firebase_auth.is_logged_in() and

                                                       username == firebase_auth.username) else (255, 255, 255)

                           

                            text = f"{idx}. {username}: {score} (Lv{level})"

                            draw_text_with_outline(screen, text, font_small, 80, y, color)

                            y += 50

                        except Exception as e:

                            print(f"Loi hien thi entry: {e}")

                            continue



        draw_text_with_outline(screen, "ESC/ENTER de quay lai", font_small, 230, 870, (200, 200, 200))

        pygame.display.flip()

        clock.tick(60)



def show_main_menu(screen, font_large, font_small):

    """Main menu with Play, Leaderboard, Login, Quit. Returns action string."""

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

                        if selected == 0:

                            return "play"

                        elif selected == 1:

                            return "leaderboard"

                        elif selected == 2:

                            if firebase_auth.is_logged_in():

                                firebase_auth.logout()

                                return "menu_refresh"

                            else:

                                return "login"

                        else:

                            return "quit"

                    else:

                        if selected == 0:

                            return "play"

                        elif selected == 1:

                            return "leaderboard"

                        else:

                            return "quit"



        screen.fill((135, 206, 235))

        screen.blit(background1, (0, 0))  # Menu dùng background1



        title_panel = pygame.Surface((600, 140))

        title_panel.fill((30, 30, 50))

        pygame.draw.rect(title_panel, (100, 150, 255), (0, 0, 600, 140), 6)

        pygame.draw.rect(title_panel, (70, 120, 200), (6, 6, 588, 128), 3)

        screen.blit(title_panel, (84, 200))

        draw_text_with_outline(screen, "TOWER BUILDER", font_large, 210, 245, (255, 255, 150))



        menu_panel = pygame.Surface((500, 380))

        menu_panel.fill((30, 30, 50))

        pygame.draw.rect(menu_panel, (100, 150, 255), (0, 0, 500, 380), 6)

        pygame.draw.rect(menu_panel, (70, 120, 200), (6, 6, 488, 368), 3)

        screen.blit(menu_panel, (134, 380))



        y = 435

        for idx, label in enumerate(options):

            color = (255, 255, 255)

            if idx == selected:

                color = (255, 255, 150)

                pygame.draw.rect(screen, (70, 120, 200), (200, y - 8, 368, 50), 0)

            draw_text_with_outline(screen, label, font_small, 300, y, color)

            y += 65



        # Hiển thị trạng thái đăng nhập

        if FIREBASE_ENABLED and firebase_auth.is_logged_in():

            draw_text_with_outline(screen, f"Xin chao: {firebase_auth.username}", font_small, 210, 345, (150, 255, 150))



        draw_text_with_outline(screen, "Len/Xuong de chon, Enter de xac nhan", font_small, 145, 810, (200, 200, 200))

        pygame.display.flip()

        clock.tick(60)



def play_game(screen, font_small, font_large):

    """Run one game session. Returns action string."""

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



        if block.state == "swinging":

            block.swing(tower.camera_y)

        elif block.state == "falling":

            result = block.drop(tower, current_level=level, wind_force=wind_force)

            if result is not None:

                points = result["points"]

                new_width = result["new_width"]

                if points == -1:

                    block.state = "failed"

                   

                    # Lưu điểm ngay khi game over

                    save_score_to_leaderboard(score, level)

                    if FIREBASE_ENABLED and firebase_auth.is_logged_in():

                        firebase_auth.save_score(score, level)

                   

                    # Đợi 0.5s để đảm bảo Firebase lưu xong

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

                level += 1

                adjust_difficulty(level)

            block = Block(tower.camera_y, tower_size=len(tower.blocks), width=current_block_width)



        tower.update_camera()



        screen.fill((135, 206, 235))

       

        # Vẽ background với hàm mới

        draw_backgrounds(tower.camera_y)

       

        tower.draw()

        block.draw(tower.camera_y)



        draw_instruction_panel(screen, font_small, level)

        draw_wind_indicator(screen, font_small, level, wind_force, wind_direction)

        draw_scoreboard(screen, font_large, font_small, score, level, combo)



        pygame.display.flip()



    return "menu"



def main():

    global force, rope_length, grav, wind_force, wind_direction, wind_timer

    # Khởi tạo font... (giữ nguyên code cũ)

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

   

    # Vòng lặp menu chính

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

            lb_action = show_leaderboard(screen, font_large, font_small,

                                        show_online=show_online, force_refresh=True)

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

                    continue  # Chơi lại

                elif game_action == "leaderboard":

                    # Hiển thị leaderboard với force_refresh

                    show_online = FIREBASE_ENABLED and firebase_auth.is_logged_in()

                    lb_action = show_leaderboard(screen, font_large, font_small,

                                                show_online=show_online, force_refresh=True)

                    if lb_action == "quit":

                        app_running = False

                        break

                    # Sau khi xem xong leaderboard, quay lại menu

                    break

                else:  # menu

                    break



    pygame.quit()



if __name__ == "__main__":

    main()