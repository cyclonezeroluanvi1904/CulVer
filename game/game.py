import pygame
import sys
import os
from level1 import Level1
from level2 import Level2
pygame.init()

# ----------------- Cấu hình -----------------
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RPG Pixel Demo")

clock = pygame.time.Clock()

# ---- Font ----
base_dir = os.path.dirname(os.path.abspath(__file__))
font_path = os.path.join(base_dir, "font", "PressStart2P-Regular.ttf")
font_game = pygame.font.Font(font_path, 20)
font_title = pygame.font.Font(font_path, 32)
font_vn = pygame.font.SysFont("tahoma", 28)  # font hỗ trợ tiếng Việt

chapters = ["Chapter 1: Màn 1", "Chapter 2: Màn 2"]

# ----------------- State -----------------
state = "menu"
fade_alpha = 0
fade_speed = int(255 / (0.4 * 60))
fade_direction = None

# Message
message_text = "Chào mừng bạn đã đến với Rộc Tưng 800 000 năm trước"
message_active = False
message_start_time = 0
message_duration = 5000
message_alpha = 0

# Chapter fade
chapter_alpha = 0
chapter_fade_speed = 5

# ----------------- Load hình ảnh -----------------
def load_image(path: str) -> pygame.Surface:
    if not os.path.exists(path):
        return None
    return pygame.image.load(path).convert_alpha()

bg_path = os.path.join(base_dir, "background", "background.png")
play_btn_path = os.path.join(base_dir, "background", "play.png")
welcome_bg_path = os.path.join(base_dir, "background", "welcomebackground.png")

background_surface = load_image(bg_path)
play_surface = load_image(play_btn_path)
welcome_surface = load_image(welcome_bg_path)

if background_surface is None:
    background_surface = pygame.Surface((WIDTH, HEIGHT))
    background_surface.fill((100, 150, 200))

if play_surface is None:
    play_surface = pygame.Surface((200, 80))
    play_surface.fill((255, 200, 0))

play_surface_original = play_surface

# ----------------- Layout cập nhật -----------------
def update_layout():
    """Cập nhật vị trí theo kích thước mới"""
    global WIDTH, HEIGHT, title_pos, chapter_button_spacing
    info = pygame.display.Info()
    WIDTH, HEIGHT = info.current_w, info.current_h
    title_pos = (WIDTH // 2, HEIGHT // 5)
    chapter_button_spacing = int(HEIGHT * 0.25)

update_layout()

# ----------------- Vẽ Menu -----------------
def draw_menu():
    scaled_bg = pygame.transform.scale(background_surface, (WIDTH, HEIGHT))
    screen.blit(scaled_bg, (0, 0))

    shorter_side = min(WIDTH, HEIGHT)
    target_height = max(1, int(shorter_side * 0.3))
    scale_ratio = target_height / play_surface_original.get_height()
    target_width = max(1, int(play_surface_original.get_width() * scale_ratio))
    scaled_play = pygame.transform.smoothscale(play_surface_original, (target_width, target_height))
    center_x = WIDTH // 2
    center_y = HEIGHT // 2 + int(HEIGHT * 0.1)
    base_rect = scaled_play.get_rect(center=(center_x, center_y))

    mouse_x, mouse_y = pygame.mouse.get_pos()
    is_hovered = base_rect.collidepoint(mouse_x, mouse_y)
    hover_scale = 1.04
    if is_hovered:
        scaled_w = int(target_width * hover_scale)
        scaled_h = int(target_height * hover_scale)
        scaled_play = pygame.transform.smoothscale(play_surface_original, (scaled_w, scaled_h))
        draw_rect = scaled_play.get_rect(center=(center_x, center_y))
    else:
        draw_rect = base_rect

    screen.blit(scaled_play, draw_rect)
    return draw_rect

# ----------------- Fade -----------------
def draw_fade():
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill((0, 0, 0))
    fade_surface.set_alpha(fade_alpha)
    screen.blit(fade_surface, (0, 0))

# ----------------- Outline text -----------------
def render_text_with_outline(text, font, text_color, outline_color, outline_width):
    base = font.render(text, True, text_color)
    size = (base.get_width() + outline_width * 2, base.get_height() + outline_width * 2)
    outline_image = pygame.Surface(size, pygame.SRCALPHA)

    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx * dx + dy * dy <= outline_width * outline_width:
                pos = (dx + outline_width, dy + outline_width)
                outline_image.blit(font.render(text, True, outline_color), pos)
    outline_image.blit(base, (outline_width, outline_width))
    return outline_image

# ----------------- Vẽ Message -----------------
def draw_message():
    global message_alpha, message_active, state
    elapsed = pygame.time.get_ticks() - message_start_time

    if elapsed < 500 and message_alpha < 255:
        message_alpha = min(255, message_alpha + 10)
    elif elapsed > message_duration:
        message_alpha = max(0, message_alpha - 10)
        if message_alpha == 0:
            message_active = False
            state = "chapter_select"

    # --- Nền welcome ---
    if welcome_surface:
        bg_scaled = pygame.transform.scale(welcome_surface, (WIDTH, HEIGHT))
        screen.blit(bg_scaled, (0, 0))
    else:
        screen.fill((0, 0, 0))

    # --- Chữ ---
    if message_alpha > 0:
        text_surf = render_text_with_outline(message_text, font_vn, (255, 255, 255), (0, 0, 0), 3)
        text_surf.set_alpha(message_alpha)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text_surf, text_rect)

# ----------------- Vẽ Chapter Select -----------------
def draw_chapter_select():
    global chapter_alpha
    if chapter_alpha < 255:
        chapter_alpha = min(255, chapter_alpha + chapter_fade_speed)

    screen.fill((245, 222, 179))

    title_surf = font_title.render("Chapter Select", True, (0, 0, 0))
    title_surf.set_alpha(chapter_alpha)
    title_rect = title_surf.get_rect(center=title_pos)
    screen.blit(title_surf, title_rect)

    chapter1_img = pygame.image.load(os.path.join(base_dir, "background", "chapter1.png")).convert_alpha()
    chapter2_img = pygame.image.load(os.path.join(base_dir, "background", "chapter2.png")).convert_alpha()

    target_width = int(WIDTH * 0.4)
    scale_ratio = target_width / chapter1_img.get_width()
    target_height = int(chapter1_img.get_height() * scale_ratio)

    chapter1_img = pygame.transform.smoothscale(chapter1_img, (target_width, target_height))
    chapter2_img = pygame.transform.smoothscale(chapter2_img, (target_width, target_height))

    chapter1_rect = chapter1_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - chapter_button_spacing // 2))
    chapter2_rect = chapter2_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + chapter_button_spacing // 2))

    mouse_x, mouse_y = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()[0]
    hover_scale = 1.05
    selected_chapter = None

    for img, rect, tag in [(chapter1_img, chapter1_rect, "chapter1"),
                           (chapter2_img, chapter2_rect, "chapter2")]:
        if rect.collidepoint(mouse_x, mouse_y):
            scaled = pygame.transform.smoothscale(img, (int(target_width * hover_scale), int(target_height * hover_scale)))
            new_rect = scaled.get_rect(center=rect.center)
            screen.blit(scaled, new_rect)
            if click:
                selected_chapter = tag
        else:
            screen.blit(img, rect)

    return selected_chapter

# ----------------- Main Loop -----------------
def main():
    global state, fade_alpha, fade_direction, chapter_alpha, WIDTH, HEIGHT, screen
    chosen_chapter = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if state == "menu":
                    play_rect = draw_menu()
                    if play_rect.collidepoint(mouse_x, mouse_y):
                        state = "fade_out_menu"
                        fade_direction = "out"
                        fade_alpha = 0
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_F11:
                    try:
                        pygame.display.toggle_fullscreen()
                    except pygame.error:
                        info = pygame.display.Info()
                        flags = screen.get_flags()
                        if flags & pygame.FULLSCREEN:
                            screen = pygame.display.set_mode((1280, 720))
                        else:
                            screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
                    update_layout()

        # ----- Logic theo state -----
        if state == "menu":
            draw_menu()
        elif state == "fade_out_menu":
            draw_menu()
            draw_fade()
            fade_alpha += fade_speed
            if fade_alpha >= 255:
                fade_alpha = 255
                state = "message"
                global message_start_time, message_active, message_alpha
                message_start_time = pygame.time.get_ticks()
                message_active = True
                message_alpha = 0
        elif state == "message":
            draw_message()
        elif state == "chapter_select":
            selected_chapter = draw_chapter_select()
            if selected_chapter:
                fade_direction = "out"
                fade_alpha = 0
                state = "fade_out_chapter"
                chosen_chapter = selected_chapter
        elif state == "fade_out_chapter":
            draw_chapter_select()
            draw_fade()
            fade_alpha += fade_speed
            if fade_alpha >= 255:
                fade_alpha = 255
                if chosen_chapter == "chapter1":
                    level = Level1(screen)
                else:
                    level = Level2(screen)
                for alpha in range(255, -1, -int(fade_speed * 1.5)):
                    screen.fill((0, 0, 0))
                    fade_surface = pygame.Surface((WIDTH, HEIGHT))
                    fade_surface.fill((0, 0, 0))
                    fade_surface.set_alpha(alpha)
                    screen.blit(fade_surface, (0, 0))
                    pygame.display.flip()
                    clock.tick(60)
                level.run()
                fade_alpha = 255
                state = "chapter_select"
                chapter_alpha = 0

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
