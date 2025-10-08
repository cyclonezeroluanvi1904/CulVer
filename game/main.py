import os
import sys
import pygame

def load_background(path: str) -> pygame.Surface:
    if not os.path.exists(path):
        raise SystemExit(
            f"Không tìm thấy ảnh nền tại '{path}'. Hãy kiểm tra đường dẫn và tên file."
        )
    try:
        # Tải ảnh thô trước, chưa convert để tránh lỗi "no video mode has been set"
        return pygame.image.load(path)
    except pygame.error as e:
        raise SystemExit(f"Không thể tải ảnh nền: {e}")
def main() -> None:
    pygame.init()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    bg_path = os.path.join(base_dir, "background", "background.jpg")
    play_btn_path = os.path.join(base_dir, "background", "play.png")

    try:
        background_surface = load_background(bg_path)
        play_surface = load_background(play_btn_path)
    except SystemExit as e:
        print(e)
        pygame.quit()
        sys.exit(1)

    width, height = background_surface.get_size()
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

    pygame.display.set_caption("Cửa sổ Pygame với hình nền")

    # Chỉ convert sau khi đã có video mode
    if background_surface.get_alpha() is not None:
        background_surface = background_surface.convert_alpha()
    else:
        background_surface = background_surface.convert()

    # Convert nút chơi sau khi có video mode
    if play_surface.get_alpha() is not None:
        play_surface = play_surface.convert_alpha()
    else:
        play_surface = play_surface.convert()

    # Lưu ảnh gốc của nút chơi để scale theo kích thước cửa sổ mà không bị giảm chất lượng dần
    play_surface_original = play_surface

    clock = pygame.time.Clock()
    running = True
    fade_active = False
    fade_alpha = 0
    fade_max = 255  # Độ tối tối đa (0-255, tối hẳn)
    fade_speed = 4  # Tốc độ chuyển fade (giảm để hiệu ứng chậm hơn)
    fade_pause = False
    fade_pause_time = 0
    fade_pause_duration = 1000  # ms, giữ tối trong 1 giây
    show_message = False
    message_text = "Thái Vĩ Luân"
    font = pygame.font.SysFont(None, 48)
    message_box_size = (400, 120)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not fade_active and not show_message:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # Kiểm tra click vào nút play
                current_width, current_height = screen.get_size()
                shorter_side = min(current_width, current_height)
                target_height = max(1, int(shorter_side * 0.3))
                scale_ratio = target_height / play_surface_original.get_height()
                target_width = max(1, int(play_surface_original.get_width() * scale_ratio))
                center_x = current_width // 2
                center_y = current_height // 2 + int(current_height * 0.1)
                scaled_play = pygame.transform.smoothscale(play_surface_original, (target_width, target_height))
                base_rect = scaled_play.get_rect()
                base_rect.center = (center_x, center_y)
                if base_rect.collidepoint(mouse_x, mouse_y):
                    fade_active = True
                    fade_alpha = 0

        # Lấy kích thước cửa sổ hiện tại
        current_width, current_height = screen.get_size()
        scaled_bg = pygame.transform.scale(background_surface, (current_width, current_height))
        screen.blit(scaled_bg, (0, 0))

        # Tính kích thước nút chơi tỉ lệ theo cửa sổ, giữ nguyên tỉ lệ khung hình
        shorter_side = min(current_width, current_height)
        target_height = max(1, int(shorter_side * 0.3))
        scale_ratio = target_height / play_surface_original.get_height()
        target_width = max(1, int(play_surface_original.get_width() * scale_ratio))
        scaled_play = pygame.transform.smoothscale(play_surface_original, (target_width, target_height))
        center_x = current_width // 2
        center_y = current_height // 2 + int(current_height * 0.1)
        base_rect = scaled_play.get_rect()
        base_rect.center = (center_x, center_y)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        is_hovered = base_rect.collidepoint(mouse_x, mouse_y)
        hover_scale = 1.04
        if is_hovered:
            scaled_w = max(1, int(target_width * hover_scale))
            scaled_h = max(1, int(target_height * hover_scale))
            scaled_play = pygame.transform.smoothscale(play_surface_original, (scaled_w, scaled_h))
            draw_rect = scaled_play.get_rect()
            draw_rect.center = (center_x, center_y)
        else:
            draw_rect = base_rect
        if not show_message:
            screen.blit(scaled_play, draw_rect)

        # Hiệu ứng fade: tối dần rồi sáng dần
        if fade_active:
            if not fade_pause:
                fade_alpha += fade_speed
                if fade_alpha >= fade_max:
                    fade_alpha = fade_max
                    fade_pause = True
                    fade_pause_time = pygame.time.get_ticks()
                elif fade_alpha <= 0 and fade_speed < 0:
                    fade_active = False
                    fade_speed = abs(fade_speed)
                    show_message = True
            else:
                # Đang pause ở trạng thái tối đen
                if pygame.time.get_ticks() - fade_pause_time >= fade_pause_duration:
                    fade_pause = False
                    fade_speed = -abs(fade_speed)  # Bắt đầu sáng dần
            fade_surface = pygame.Surface((current_width, current_height))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(fade_alpha)
            screen.blit(fade_surface, (0, 0))

        # Hiện ô thông báo
        if show_message:
            # Vẽ nền mờ
            overlay = pygame.Surface((current_width, current_height))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(120)
            screen.blit(overlay, (0, 0))
            # Vẽ box
            box_rect = pygame.Rect(0, 0, *message_box_size)
            box_rect.center = (current_width // 2, current_height // 2)
            pygame.draw.rect(screen, (255, 255, 255), box_rect, border_radius=18)
            pygame.draw.rect(screen, (0, 0, 0), box_rect, 3, border_radius=18)
            # Vẽ text
            text_surf = font.render(message_text, True, (0, 0, 0))
            text_rect = text_surf.get_rect(center=box_rect.center)
            screen.blit(text_surf, text_rect)

        pygame.display.flip()
        clock.tick(60)


    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()


