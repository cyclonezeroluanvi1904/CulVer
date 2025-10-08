import pygame
import sys
import os
import random


class Buffalo:
    def __init__(self, base_dir, ground_y, screen_width):
        self.images = []
        self.masks = []
        for i in range(6):
            path = os.path.join(base_dir, f"tile{i}.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (160, 120))
                self.images.append(img)
                self.masks.append(pygame.mask.from_surface(img))

        if not self.images:
            surf = pygame.Surface((160, 120), pygame.SRCALPHA)
            pygame.draw.rect(surf, (255, 0, 0), surf.get_rect(), 2)
            self.images = [surf]
            self.masks = [pygame.mask.from_surface(surf)]

        self.index = 0
        self.timer = pygame.time.get_ticks()
        self.animation_speed = 120

        self.x = random.randint(100, screen_width - 200)
        self.y = ground_y
        self.speed = 0
        self.max_speed = 3
        self.accel = 0.05
        self.decel = 0.1
        self.direction = random.choice([-1, 1])
        self.ground_y = ground_y
        self.screen_width = screen_width

        self.aggro_range = 250
        self.charge_speed = 7
        self.state = "idle"  # idle | charge | overrun | cooldown
        self.cooldown_timer = 0
        self.charge_target_x = None

    def update(self, player_rect):
        now = pygame.time.get_ticks()

        # hoạt ảnh
        if now - self.timer >= self.animation_speed:
            self.index = (self.index + 1) % len(self.images)
            self.timer = now

        # hết cooldown → idle
        if self.state == "cooldown" and now - self.cooldown_timer >= 2500:
            self.state = "idle"
            # ✨ có thể quay lại chiều ngược (50%)
            if random.random() < 0.5:
                self.direction *= -1

        dx = player_rect.centerx - self.x
        distance = abs(dx)

        # idle mà thấy player → charge
        if self.state == "idle" and distance < self.aggro_range:
            self.state = "charge"
            self.direction = 1 if dx > 0 else -1
            self.charge_target_x = player_rect.centerx + self.direction * 200

        # hành vi
        if self.state == "idle":
            if self.speed < self.max_speed:
                self.speed += self.accel
            self.x += self.direction * self.speed

            if random.random() < 0.005:
                if self.speed > 0.3:
                    self.speed -= self.decel * 5
                else:
                    self.direction *= -1

        elif self.state == "charge":
            self.x += self.direction * self.charge_speed
            # nếu vượt mục tiêu → overrun (chạy thêm quán tính)
            if (self.direction == 1 and self.x >= self.charge_target_x) or \
               (self.direction == -1 and self.x <= self.charge_target_x):
                self.state = "overrun"
                self.cooldown_timer = now

        elif self.state == "overrun":
            if now - self.cooldown_timer >= 1000:
                self.state = "cooldown"
                self.cooldown_timer = now

        elif self.state == "cooldown":
            self.speed = max(0, self.speed - self.decel * 2)
            self.x += self.direction * self.speed

        # giới hạn màn hình
        if self.x < 80:
            self.x = 80
            self.direction = 1
        elif self.x > self.screen_width - 80:
            self.x = self.screen_width - 80
            self.direction = -1

    def draw(self, screen):
        img = self.images[self.index]
        mask = self.masks[self.index]

        if self.direction == 1:
            img = pygame.transform.flip(img, True, False)
            mask = pygame.mask.from_surface(img)

        rect = img.get_rect(midbottom=(self.x, self.ground_y))
        screen.blit(img, rect)
        return rect, mask


class Level2:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True

        self.WIDTH, self.HEIGHT = screen.get_size()
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # background
        bg_path = os.path.join(base_dir, "background", "nenlevel2.png")
        if os.path.exists(bg_path):
            bg_raw = pygame.image.load(bg_path).convert()
            self.background = pygame.transform.scale(bg_raw, (self.WIDTH, self.HEIGHT))
        else:
            self.background = pygame.Surface((self.WIDTH, self.HEIGHT))
            self.background.fill((150, 200, 250))

        # ground
        ground_path = os.path.join(base_dir, "background", "dat.jpg")
        if os.path.exists(ground_path):
            ground_raw = pygame.image.load(ground_path).convert_alpha()
        else:
            ground_raw = pygame.Surface((100, 100))
            ground_raw.fill((139, 69, 19))
        ground_height = self.HEIGHT // 6
        self.ground = pygame.transform.scale(ground_raw, (self.WIDTH, ground_height))
        self.ground_rect = self.ground.get_rect(midbottom=(self.WIDTH // 2, self.HEIGHT))

        # ✅ Player animation
        player_dir = os.path.join(base_dir, "player")
        self.anim_stand = []
        for i in range(2):
            p = os.path.join(player_dir, f"stand{i}.png")
            if os.path.exists(p):
                img = pygame.image.load(p).convert_alpha()
                self.anim_stand.append(pygame.transform.scale(img, (100, 150)))

        self.anim_walk = []
        for i in range(6):
            p = os.path.join(player_dir, f"walkleft{i}.png")
            if os.path.exists(p):
                img = pygame.image.load(p).convert_alpha()
                self.anim_walk.append(pygame.transform.scale(img, (100, 150)))

        # fallback
        if not self.anim_stand:
            surf = pygame.Surface((100, 150))
            surf.fill((255, 255, 0))
            self.anim_stand = [surf]
        if not self.anim_walk:
            surf = pygame.Surface((100, 150))
            surf.fill((0, 255, 0))
            self.anim_walk = [surf]

        self.player_anim_index = 0
        self.player_timer = pygame.time.get_ticks()
        self.player_anim_speed = 150
        self.player_state = "stand"  # stand | walk
        self.player_dir = 1  # 1 = phải, -1 = trái

        self.player_x = self.WIDTH // 2
        self.player_y = self.ground_rect.top + 75
        self.vel_y = 0
        self.on_ground = True
        self.speed = 4
        self.gravity = 0.8
        self.jump_strength = 15

        self.invincible = False
        self.invincible_timer = 0
        self.flash = False

        # buffalo
        npc_dir = os.path.join(base_dir, "buffalo")
        self.buffalo = Buffalo(npc_dir, self.ground_rect.top + 80, self.WIDTH)
        while abs(self.buffalo.x - self.player_x) < 300:
            self.buffalo.x = random.randint(100, self.WIDTH - 200)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        moving = False

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player_x -= self.speed
            self.player_dir = -1
            moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player_x += self.speed
            self.player_dir = 1
            moving = True
        if (keys[pygame.K_UP] or keys[pygame.K_SPACE]) and self.on_ground:
            self.vel_y = -self.jump_strength
            self.on_ground = False

        self.player_state = "walk" if moving else "stand"
        self.player_x = max(50, min(self.player_x, self.WIDTH - 50))

    def apply_physics(self):
        self.vel_y += self.gravity
        self.player_y += self.vel_y
        ground_y = self.ground_rect.top + 75
        if self.player_y >= ground_y:
            self.player_y = ground_y
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False

    def get_current_player_image(self):
        now = pygame.time.get_ticks()
        anims = self.anim_walk if self.player_state == "walk" else self.anim_stand

        # đảm bảo chỉ số luôn hợp lệ
        if self.player_anim_index >= len(anims):
            self.player_anim_index = 0

        # cập nhật hoạt ảnh theo thời gian
        if now - self.player_timer >= self.player_anim_speed:
            self.player_anim_index = (self.player_anim_index + 1) % len(anims)
            self.player_timer = now

        img = anims[self.player_anim_index]
        if self.player_dir == 1:
            img = pygame.transform.flip(img, True, False)
        return img


    def run(self):
        while self.running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.handle_input()
            self.apply_physics()

            player_img = self.get_current_player_image()
            player_rect = player_img.get_rect(midbottom=(self.player_x, self.player_y))

            self.buffalo.update(player_rect)

            buffalo_rect, buffalo_mask = self.buffalo.draw(self.screen)

# --- va chạm pixel-perfect ---
            player_mask = pygame.mask.from_surface(player_img)
            offset = (buffalo_rect.x - player_rect.x, buffalo_rect.y - player_rect.y)
            collision = player_mask.overlap(buffalo_mask, offset)

            if collision and not self.invincible:
                self.invincible = True
                self.invincible_timer = pygame.time.get_ticks()
                self.vel_y = -12
                self.buffalo.state = "cooldown"
                self.buffalo.cooldown_timer = pygame.time.get_ticks()


            # invincible nhấp nháy
            if self.invincible:
                now = pygame.time.get_ticks()
                if now - self.invincible_timer >= 2000:
                    self.invincible = False
                else:
                    self.flash = (now // 100) % 2 == 0

            # render
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.ground, self.ground_rect.topleft)
            self.buffalo.draw(self.screen)
            if not (self.invincible and self.flash):
                self.screen.blit(player_img, player_rect)

            pygame.display.flip()
            self.clock.tick(60)

    