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

def show_login_screen(screen, background, font_small, font_large, firebase_auth, lang_data, current_lang):
    """Màn hình đăng nhập/đăng ký - hỗ trợ đa ngôn ngữ"""
    # Hàm dịch nội bộ
    def _(key):
        return lang_data.get(current_lang, {}).get(key, key)

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
                    if mode == "login":
                        active_field = "password" if active_field == "email" else "email"
                    else:
                        fields = ["email", "username", "password"]
                        idx = fields.index(active_field)
                        active_field = fields[(idx + 1) % len(fields)]
                
                elif event.key == pygame.K_RETURN:
                    if mode == "login":
                        if email and password:
                            success, msg = firebase_auth.login(email, password)
                            message = msg
                            message_color = (100, 255, 100) if success else (255, 100, 100)
                            message_timer = 180
                            if success:
                                return "logged_in"
                        else:
                            message = _("login_missing_info")
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
                            message = _("register_missing_info")
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
                    if event.unicode.isprintable():
                        if active_field == "email" and len(email) < 40:
                            email += event.unicode
                        elif active_field == "password" and len(password) < 30:
                            password += event.unicode
                        elif active_field == "username" and len(username) < 20:
                            username += event.unicode
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                panel_width = 420
                panel_height = 350 if mode == "login" else 400
                panel_x = (600 - panel_width) // 2
                panel_y = 150
                input_width = 360
                input_x = panel_x + 30
                
                if mode == "login":
                    email_y = panel_y + 70
                    if input_x <= mouse_pos[0] <= input_x + input_width and email_y <= mouse_pos[1] <= email_y + 40:
                        active_field = "email"
                    else:
                        pwd_y = panel_y + 140
                        if input_x <= mouse_pos[0] <= input_x + input_width and pwd_y <= mouse_pos[1] <= pwd_y + 40:
                            active_field = "password"
                        else:
                            btn_width = 180
                            btn_x = panel_x + (panel_width - btn_width) // 2
                            btn_y = panel_y + 240
                            if btn_x <= mouse_pos[0] <= btn_x + btn_width and btn_y <= mouse_pos[1] <= btn_y + 45:
                                if email and password:
                                    success, msg = firebase_auth.login(email, password)
                                    message = msg
                                    message_color = (100, 255, 100) if success else (255, 100, 100)
                                    message_timer = 180
                                    if success:
                                        return "logged_in"
                            elif panel_x + 50 <= mouse_pos[0] <= panel_x + 370 and panel_y + 310 <= mouse_pos[1] <= panel_y + 330:
                                mode = "register"
                                active_field = "email"
                                message = ""
                else:
                    email_y = panel_y + 60
                    if input_x <= mouse_pos[0] <= input_x + input_width and email_y <= mouse_pos[1] <= email_y + 40:
                        active_field = "email"
                    else:
                        user_y = panel_y + 125
                        if input_x <= mouse_pos[0] <= input_x + input_width and user_y <= mouse_pos[1] <= user_y + 40:
                            active_field = "username"
                        else:
                            pwd_y = panel_y + 190
                            if input_x <= mouse_pos[0] <= input_x + input_width and pwd_y <= mouse_pos[1] <= pwd_y + 40:
                                active_field = "password"
                            else:
                                btn_width = 180
                                btn_x = panel_x + (panel_width - btn_width) // 2
                                btn_y = panel_y + 285
                                if btn_x <= mouse_pos[0] <= btn_x + btn_width and btn_y <= mouse_pos[1] <= btn_y + 45:
                                    if email and password and username:
                                        success, msg = firebase_auth.register(email, password, username)
                                        message = msg
                                        message_color = (100, 255, 100) if success else (255, 100, 100)
                                        message_timer = 180
                                        if success:
                                            return "logged_in"
                                elif panel_x + 50 <= mouse_pos[0] <= panel_x + 370 and panel_y + 355 <= mouse_pos[1] <= panel_y + 375:
                                    mode = "login"
                                    active_field = "email"
                                    message = ""
        
        # Vẽ
        screen.fill((135, 206, 235))
        screen.blit(background, (0, 0))
        
        panel_width = 420
        panel_height = 350 if mode == "login" else 400
        panel = pygame.Surface((panel_width, panel_height))
        panel.fill((30, 30, 50))
        pygame.draw.rect(panel, (100, 150, 255), (0, 0, panel_width, panel_height), 6)
        panel_x = (600 - panel_width) // 2
        panel_y = 150
        screen.blit(panel, (panel_x, panel_y))
        
        # Title
        title = _("login_title") if mode == "login" else _("register_title")
        title_font = pygame.font.SysFont("Segoe UI", 28, bold=True)
        draw_text_with_outline(screen, title, title_font, panel_x + 130, panel_y + 15, (255, 255, 150))
        
        if mode == "login":
            input_width = 360
            input_x = panel_x + 30
            
            y_pos = panel_y + 70
            draw_text_with_outline(screen, _("email_label"), font_small, input_x + 5, y_pos - 25, (200, 200, 255))
            draw_input_box(screen, font_small, input_x, y_pos, input_width, 40, email, active_field == "email")
            
            y_pos += 70
            draw_text_with_outline(screen, _("password_label"), font_small, input_x + 5, y_pos - 25, (200, 200, 255))
            draw_input_box(screen, font_small, input_x, y_pos, input_width, 40, password, active_field == "password", password=True)
            
            btn_width = 180
            btn_height = 45
            btn_x = panel_x + (panel_width - btn_width) // 2
            btn_y = panel_y + 240
            login_btn = pygame.Surface((btn_width, btn_height))
            login_btn.fill((50, 150, 50))
            pygame.draw.rect(login_btn, (100, 255, 100), (0, 0, btn_width, btn_height), 3)
            screen.blit(login_btn, (btn_x, btn_y))
            draw_text_with_outline(screen, _("login_button"), font_small, btn_x + 45, btn_y + 12, (255, 255, 255))
            
            draw_text_with_outline(screen, _("switch_to_register"), font_small, panel_x + 50, panel_y + 310, (200, 200, 255))
        
        else:
            input_width = 360
            input_x = panel_x + 30
            
            y_pos = panel_y + 60
            draw_text_with_outline(screen, _("email_label"), font_small, input_x + 5, y_pos - 22, (200, 200, 255))
            draw_input_box(screen, font_small, input_x, y_pos, input_width, 40, email, active_field == "email")
            
            y_pos += 65
            draw_text_with_outline(screen, _("username_label"), font_small, input_x + 5, y_pos - 22, (200, 200, 255))
            draw_input_box(screen, font_small, input_x, y_pos, input_width, 40, username, active_field == "username")
            
            y_pos += 65
            draw_text_with_outline(screen, _("password_label"), font_small, input_x + 5, y_pos - 22, (200, 200, 255))
            draw_input_box(screen, font_small, input_x, y_pos, input_width, 40, password, active_field == "password", password=True)
            
            btn_width = 180
            btn_height = 45
            btn_x = panel_x + (panel_width - btn_width) // 2
            btn_y = panel_y + 285
            register_btn = pygame.Surface((btn_width, btn_height))
            register_btn.fill((50, 100, 150))
            pygame.draw.rect(register_btn, (100, 150, 255), (0, 0, btn_width, btn_height), 3)
            screen.blit(register_btn, (btn_x, btn_y))
            draw_text_with_outline(screen, _("register_button"), font_small, btn_x + 55, btn_y + 12, (255, 255, 255))
            
            draw_text_with_outline(screen, _("switch_to_login"), font_small, panel_x + 50, panel_y + 355, (200, 200, 255))
        
        if message:
            msg_y = panel_y + panel_height + 20
            msg_width_estimate = len(message) * 10
            msg_x = (600 - msg_width_estimate) // 2
            draw_text_with_outline(screen, message, font_small, msg_x, msg_y, message_color)
        
        draw_text_with_outline(screen, _("back_instruction"), font_small, 240, 730, (180, 180, 180))
        
        pygame.display.flip()