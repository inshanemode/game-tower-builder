# -*- coding: utf-8 -*-
import pygame

def draw_input_box(screen, font, x, y, width, height, text, active, password=False):
    """Vẽ ô input"""
    color = (100, 150, 255) if active else (70, 120, 200)
    pygame.draw.rect(screen, (30, 30, 50), (x, y, width, height))
    pygame.draw.rect(screen, color, (x, y, width, height), 3)
    
    display_text = text
    if password and text:
        display_text = "*" * len(text)
    
    text_surface = font.render(display_text, True, (255, 255, 255))
    screen.blit(text_surface, (x + 10, y + 10))
    
    # Cursor nháy
    if active:
        cursor_x = x + 10 + text_surface.get_width() + 2
        pygame.draw.line(screen, (255, 255, 255), (cursor_x, y + 8), (cursor_x, y + height - 8), 2)

def draw_text_with_outline(surface, text, font, x, y, color, outline_color=(0, 0, 0), outline_width=2):
    """Vẽ chữ có viền"""
    for dx in [-outline_width, 0, outline_width]:
        for dy in [-outline_width, 0, outline_width]:
            if dx != 0 or dy != 0:
                outline_surface = font.render(text, True, outline_color)
                surface.blit(outline_surface, (x + dx, y + dy))
    
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))

def show_login_screen(screen, background, font_small, font_large, firebase_auth):
    """Màn hình đăng nhập/đăng ký"""
    mode = "login"  # "login" hoặc "register"
    
    email = ""
    password = ""
    username = ""
    
    active_field = "email"
    message = ""
    message_color = (255, 255, 255)
    message_timer = 0
    
    clock = pygame.time.Clock()
    
    while True:
        clock.tick(60)
        
        if message_timer > 0:
            message_timer -= 1
            if message_timer == 0:
                message = ""
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "back"
                
                elif event.key == pygame.K_TAB:
                    # Chuyển field
                    if mode == "login":
                        active_field = "password" if active_field == "email" else "email"
                    else:
                        fields = ["email", "username", "password"]
                        idx = fields.index(active_field)
                        active_field = fields[(idx + 1) % len(fields)]
                
                elif event.key == pygame.K_RETURN:
                    # Submit
                    if mode == "login":
                        if email and password:
                            success, msg = firebase_auth.login(email, password)
                            message = msg
                            message_color = (100, 255, 100) if success else (255, 100, 100)
                            message_timer = 180
                            if success:
                                return "logged_in"
                        else:
                            message = "Vui lòng điền đầy đủ thông tin!"
                            message_color = (255, 200, 100)
                            message_timer = 120
                    else:
                        if email and password and username:
                            success, msg = firebase_auth.register(email, password, username)
                            message = msg
                            message_color = (100, 255, 100) if success else (255, 100, 100)
                            message_timer = 180
                            if success:
                                return "logged_in"
                        else:
                            message = "Vui lòng điền đầy đủ thông tin!"
                            message_color = (255, 200, 100)
                            message_timer = 120
                
                elif event.key == pygame.K_BACKSPACE:
                    if active_field == "email":
                        email = email[:-1]
                    elif active_field == "password":
                        password = password[:-1]
                    elif active_field == "username":
                        username = username[:-1]
                
                else:
                    # Nhập ký tự
                    if event.unicode.isprintable():
                        if active_field == "email" and len(email) < 40:
                            email += event.unicode
                        elif active_field == "password" and len(password) < 30:
                            password += event.unicode
                        elif active_field == "username" and len(username) < 20:
                            username += event.unicode
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Check click vào input boxes
                if mode == "login":
                    if 200 <= mouse_pos[0] <= 600 and 220 <= mouse_pos[1] <= 260:
                        active_field = "email"
                    elif 200 <= mouse_pos[0] <= 600 and 290 <= mouse_pos[1] <= 330:
                        active_field = "password"
                    # Button login
                    elif 300 <= mouse_pos[0] <= 500 and 370 <= mouse_pos[1] <= 420:
                        if email and password:
                            success, msg = firebase_auth.login(email, password)
                            message = msg
                            message_color = (100, 255, 100) if success else (255, 100, 100)
                            message_timer = 180
                            if success:
                                return "logged_in"
                    # Switch to register
                    elif 250 <= mouse_pos[0] <= 550 and 480 <= mouse_pos[1] <= 510:
                        mode = "register"
                        active_field = "email"
                        message = ""
                else:
                    if 200 <= mouse_pos[0] <= 600 and 200 <= mouse_pos[1] <= 240:
                        active_field = "email"
                    elif 200 <= mouse_pos[0] <= 600 and 260 <= mouse_pos[1] <= 300:
                        active_field = "username"
                    elif 200 <= mouse_pos[0] <= 600 and 320 <= mouse_pos[1] <= 360:
                        active_field = "password"
                    # Button register
                    elif 300 <= mouse_pos[0] <= 500 and 400 <= mouse_pos[1] <= 450:
                        if email and password and username:
                            success, msg = firebase_auth.register(email, password, username)
                            message = msg
                            message_color = (100, 255, 100) if success else (255, 100, 100)
                            message_timer = 180
                            if success:
                                return "logged_in"
                    # Switch to login
                    elif 250 <= mouse_pos[0] <= 550 and 500 <= mouse_pos[1] <= 530:
                        mode = "login"
                        active_field = "email"
                        message = ""
        
        # Vẽ
        screen.fill((135, 206, 235))
        screen.blit(background, (0, 0))
        
        # Panel chính
        panel = pygame.Surface((450, 400 if mode == "login" else 450))
        panel.fill((30, 30, 50))
        pygame.draw.rect(panel, (100, 150, 255), (0, 0, 450, panel.get_height()), 6)
        screen.blit(panel, (175, 100))
        
        # Title
        title = "DANG NHAP" if mode == "login" else "DANG KY"
        draw_text_with_outline(screen, title, font_large, 330, 120, (255, 255, 150))
        
        if mode == "login":
            # Email
            draw_text_with_outline(screen, "Email:", font_small, 210, 190, (200, 200, 255))
            draw_input_box(screen, font_small, 200, 220, 400, 40, email, active_field == "email")
            
            # Password
            draw_text_with_outline(screen, "Mat khau:", font_small, 210, 260, (200, 200, 255))
            draw_input_box(screen, font_small, 200, 290, 400, 40, password, active_field == "password", password=True)
            
            # Login button
            login_btn = pygame.Surface((200, 50))
            login_btn.fill((50, 150, 50))
            pygame.draw.rect(login_btn, (100, 255, 100), (0, 0, 200, 50), 3)
            screen.blit(login_btn, (300, 370))
            draw_text_with_outline(screen, "Dang nhap", font_small, 335, 382, (255, 255, 255))
            
            # Switch to register
            draw_text_with_outline(screen, "Chua co tai khoan? Dang ky tai day", font_small, 250, 485, (200, 200, 255))
            
        else:
            # Email
            draw_text_with_outline(screen, "Email:", font_small, 210, 170, (200, 200, 255))
            draw_input_box(screen, font_small, 200, 200, 400, 40, email, active_field == "email")
            
            # Username
            draw_text_with_outline(screen, "Ten hien thi:", font_small, 210, 240, (200, 200, 255))
            draw_input_box(screen, font_small, 200, 260, 400, 40, username, active_field == "username")
            
            # Password
            draw_text_with_outline(screen, "Mat khau:", font_small, 210, 300, (200, 200, 255))
            draw_input_box(screen, font_small, 200, 320, 400, 40, password, active_field == "password", password=True)
            
            # Register button
            register_btn = pygame.Surface((200, 50))
            register_btn.fill((50, 100, 150))
            pygame.draw.rect(register_btn, (100, 150, 255), (0, 0, 200, 50), 3)
            screen.blit(register_btn, (300, 400))
            draw_text_with_outline(screen, "Dang ky", font_small, 350, 412, (255, 255, 255))
            
            # Switch to login
            draw_text_with_outline(screen, "Da co tai khoan? Dang nhap tai day", font_small, 250, 505, (200, 200, 255))
        
        # Message
        if message:
            draw_text_with_outline(screen, message, font_small, 250, 550, message_color)
        
        # Instructions
        draw_text_with_outline(screen, "ESC - Quay lai", font_small, 310, 570, (180, 180, 180))
        
        pygame.display.flip()
