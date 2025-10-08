import pygame
import sys
import os
import random
import math


class Level1:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True

        # --- Movement / Physics ---
        self.player_speed = 4
        self.vel_y = 0
        self.gravity = 0.8
        self.jump_strength = 15
        self.on_ground = True

        self.WIDTH, self.HEIGHT = screen.get_size()
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # --- Background ---
        bg_path = os.path.join(base_dir, "background", "nenlevel1.jpg")
        if os.path.exists(bg_path):
            bg_raw = pygame.image.load(bg_path).convert()
            self.background = pygame.transform.scale(bg_raw, (self.WIDTH, self.HEIGHT))
        else:
            self.background = pygame.Surface((self.WIDTH, self.HEIGHT))
            self.background.fill((100, 200, 100))

        # --- Ground ---
        ground_path = os.path.join(base_dir, "background", "dat.jpg")
        if os.path.exists(ground_path):
            ground_raw = pygame.image.load(ground_path).convert_alpha()
        else:
            ground_raw = pygame.Surface((100, 100))
            ground_raw.fill((139, 69, 19))
        ground_height = self.HEIGHT // 6
        self.ground = pygame.transform.scale(ground_raw, (self.WIDTH, ground_height))
        self.ground_rect = self.ground.get_rect(midbottom=(self.WIDTH // 2, self.HEIGHT))

        # --- Player images ---
        player_dir = os.path.join(base_dir, "player")

        def safe_load(name):
            path = os.path.join(player_dir, name)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (120, 160))
                return img
            else:
                surf = pygame.Surface((120, 160))
                surf.fill((255, 0, 0))
                return surf

        self.stand_images = [safe_load("stand0.png")]
        walk_left_imgs = [safe_load(f"walkleft{i}.png") for i in range(5)]
        self.walk_left_images = walk_left_imgs
        self.walk_right_images = [pygame.transform.flip(img, True, False) for img in walk_left_imgs]

        # --- Player state ---
        self.direction = "right"
        self.moving = False
        self.current_images = self.stand_images
        self.player_index = 0
        self.animation_speed_ms = 120
        self.animation_timer = pygame.time.get_ticks()

        # --- Player position ---
        self.player_x = self.WIDTH // 2
        self.player_y = self.ground_rect.top + 80

        # --- Font ---
        font_path = os.path.join(base_dir, "font", "DejaVuSans.ttf")
        if os.path.exists(font_path):
            self.font = pygame.font.Font(font_path, 32)
        else:
            self.font = pygame.font.SysFont("arial", 32)

        # --- Stones ---
        stone_dir = os.path.join(base_dir, "background")
        def load_stone(name):
            path = os.path.join(stone_dir, name)
            if os.path.exists(path):
                return pygame.transform.scale(pygame.image.load(path).convert_alpha(), (80, 80))
            s = pygame.Surface((80, 80))
            s.fill((120, 120, 120))
            return s

        self.stone_img = [
            load_stone("stone1.png"),
            load_stone("stone2.png"),
            load_stone("stone3.png"),
        ]

        self.num_stones = len(self.stone_img)
        self.collected = [False] * self.num_stones
        self.randomize_stones()

        # --- Arrow indicator ---
        arrow_path = os.path.join(stone_dir, "arrow.png")
        if os.path.exists(arrow_path):
            self.arrow = pygame.image.load(arrow_path).convert_alpha()
            self.arrow = pygame.transform.scale(self.arrow, (60, 60))
            self.arrow = pygame.transform.flip(self.arrow, False, True)
        else:
            self.arrow = pygame.Surface((60, 60))
            self.arrow.fill((255, 255, 0))
        self.arrow_y_offset = 0
        self.arrow_timer = pygame.time.get_ticks()

        # --- Reward ---
        stonereal_path = os.path.join(stone_dir, "stonereal.png")
        if os.path.exists(stonereal_path):
            self.stonereal = pygame.transform.scale(
                pygame.image.load(stonereal_path).convert_alpha(), (180, 180)
            )
        else:
            self.stonereal = pygame.Surface((180, 180))
            self.stonereal.fill((255, 255, 0))
        self.show_reward = False

        # --- Combo logic ---
        self.selection_order = []

    # -----------------------------
    # Utility: randomize stone positions
    # -----------------------------
    def randomize_stones(self):
        self.stone_positions = []
        for _ in range(self.num_stones):
            x = random.randint(100, self.WIDTH - 100)
            y = self.ground_rect.top + 10
            self.stone_positions.append(pygame.Vector2(x, y))

    # -----------------------------
    # Input
    # -----------------------------
    def handle_input(self):
        keys = pygame.key.get_pressed()
        moving = False

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player_x -= self.player_speed
            self.direction = "left"
            moving = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player_x += self.player_speed
            self.direction = "right"
            moving = True

        if (keys[pygame.K_UP] or keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = -self.jump_strength
            self.on_ground = False

        self.moving = moving
        if self.moving:
            if self.direction == "left":
                self.current_images = self.walk_left_images
            else:
                self.current_images = self.walk_right_images
        else:
            self.current_images = self.stand_images

        if not self.current_images:
            self.current_images = self.stand_images
            self.player_index = 0

    # -----------------------------
    # Physics
    # -----------------------------
    def apply_physics(self):
        self.vel_y += self.gravity
        self.player_y += self.vel_y

        ground_y = self.ground_rect.top + 35
        if self.player_y >= ground_y:
            self.player_y = ground_y
            if abs(self.vel_y) > 1.5:
                self.vel_y = -self.vel_y * 0.18
            else:
                self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False

    # -----------------------------
    # Animation
    # -----------------------------
    def update_animation(self):
        if not self.current_images:
            self.current_images = self.stand_images
        now = pygame.time.get_ticks()
        if now - self.animation_timer >= self.animation_speed_ms:
            self.animation_timer = now
            self.player_index = (self.player_index + 1) % len(self.current_images)
        self.arrow_y_offset = int(5 * math.sin(now * 0.005))

    # -----------------------------
    # Draw text with outline
    # -----------------------------
    def draw_text_center(self, text, y, color=(255, 255, 255), outline_color=(0, 0, 0), outline_width=2):
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(self.WIDTH // 2, y))
        for dx in (-outline_width, 0, outline_width):
            for dy in (-outline_width, 0, outline_width):
                if dx == 0 and dy == 0:
                    continue
                outline_surface = self.font.render(text, True, outline_color)
                outline_rect = outline_surface.get_rect(center=(self.WIDTH // 2 + dx, y + dy))
                self.screen.blit(outline_surface, outline_rect)
        self.screen.blit(text_surface, text_rect)

    # -----------------------------
    # Pick logic
    # -----------------------------
    def handle_pick(self, i):
        if self.show_reward:
            return

        # Nhặt viên thứ i
        if not self.collected[i]:
            self.collected[i] = True
            self.selection_order.append(i)

        # Khi đã chọn 2 viên → kiểm tra combo
        if len(self.selection_order) == 2:
            a, b = self.selection_order
            if set((a, b)) == {0, 1}:
                self.show_reward = True
            else:
                # Chọn sai → reset toàn bộ
                self.collected = [False] * self.num_stones
                self.randomize_stones()
            self.selection_order.clear()

    # -----------------------------
    # Main loop
    # -----------------------------
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.handle_input()
            self.apply_physics()
            self.update_animation()

            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.ground, self.ground_rect.topleft)

            player_rect = pygame.Rect(self.player_x - 40, self.player_y - 160, 80, 160)

            # Draw stones
            for i, pos in enumerate(self.stone_positions):
                if not self.collected[i]:
                    rect = self.stone_img[i].get_rect(midbottom=(pos.x, self.ground_rect.top + 10))
                    self.screen.blit(self.stone_img[i], rect)
                    self.screen.blit(self.arrow, (rect.centerx - 30, rect.top - 60 + self.arrow_y_offset))

                    if player_rect.colliderect(rect):
                        self.draw_text_center("Nhấn F để nhặt", rect.y - 60, (255, 255, 0))
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_f]:
                            self.handle_pick(i)

            # Reward
            if self.show_reward:
                self.draw_text_center("Bạn đã chế tác được rìu tay!", 100, (255, 255, 255))
                self.screen.blit(self.stonereal, (self.WIDTH // 2 - 90, 150))

            # Draw player safely
            if not self.current_images:
                self.current_images = self.stand_images
            if self.player_index >= len(self.current_images):
                self.player_index = 0

            img = self.current_images[self.player_index]
            player_rect = img.get_rect(midbottom=(self.player_x, self.player_y))
            self.screen.blit(img, player_rect)

            pygame.display.flip()
            self.clock.tick(60)
