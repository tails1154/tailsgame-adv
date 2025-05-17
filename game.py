import pygame
import json
import os
from random import randint
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRAVITY = 0.5
JUMP_STRENGTH = 10
MOVEMENT_SPEED = 5
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
global lives
lives = 5
# Sfx
global HitSfx
global HitSfxFinal
global JumpSfx
HitSfx = pygame.mixer.Sound("images/hit.mp3")
HitSfxFinal = pygame.mixer.Sound("images/hitfinal.mp3")
JumpSfx = pygame.mixer.Sound("images/jump.mp3")

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Platformer Game")

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = SCREEN_HEIGHT - 100
        self.vel_y = 0
        self.on_ground = False

    def update(self, platforms, win_tile):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= MOVEMENT_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += MOVEMENT_SPEED

        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -JUMP_STRENGTH
            JumpSfx.play()

        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        self.on_ground = False

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0

        return self.rect.colliderect(win_tile.rect)

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color=BLACK):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
class MovingPlatform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, y_range):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill((150, 0, 150))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.start_y = y
        self.range = y_range
        self.speed = 2
        self.direction = 1

    def update(self):
        self.rect.y += self.speed * self.direction
        if self.rect.y > self.start_y + self.range or self.rect.y < self.start_y:
            self.direction *= -1

class WinTile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(topleft=(x, y))

def load_level(index):
    filename = f"maps/level{index}.json"
    if not os.path.exists(filename):
        return None
    with open(filename) as f:
        return json.load(f)

def play_game():
    level_index = 0
    key_sequence = [
        pygame.K_UP, pygame.K_UP,
        pygame.K_DOWN, pygame.K_DOWN,
        pygame.K_LEFT, pygame.K_RIGHT,
        pygame.K_LEFT, pygame.K_RIGHT,
        pygame.K_UP, pygame.K_DOWN,
        pygame.K_UP, pygame.K_DOWN
    ]
    input_buffer = []
    pygame.mixer.music.load("images/level.mp3", namehint="mp3")
    pygame.mixer.music.play()
    while True:
        level_data = load_level(level_index)
        if not level_data:
            print("No more levels.")
            ending()
            break

        player = Player()
        platforms = pygame.sprite.Group()
        win_tile = WinTile(level_data['win_tile']['x'], level_data['win_tile']['y'])
        all_sprites = pygame.sprite.Group(player, win_tile)
        moving_platforms = pygame.sprite.Group()
        platforms.update()  # allows MovingPlatforms to animate
#
#         for p in level_data['platforms']:
#             plat = Platform(p['x'], p['y'], p['width'], p['height'])
#             platforms.add(plat)
#             all_sprites.add(plat)
#         for p in level_data['platforms']:
#             if p.get('type') == 'moving':
#                 plat = MovingPlatform(p['x'], p['y'], p['width'], p['height'], p['range'])
#             else:
#                 plat = Platform(p['x'], p['y'], p['width'], p['height'])
#             platforms.add(plat)
#             all_sprites.add(plat)
        for p in level_data['platforms']:
            if p.get('type') == 'moving':
                plat = MovingPlatform(p['x'], p['y'], p['width'], p['height'], p['range'])
                moving_platforms.add(plat)
            else:
                plat = Platform(p['x'], p['y'], p['width'], p['height'])
            platforms.add(plat)
            all_sprites.add(plat)



        clock = pygame.time.Clock()
        running = True
        restart_level = False

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

                if event.type == pygame.KEYDOWN:
                    input_buffer.append(event.key)
                    input_buffer = input_buffer[-len(key_sequence):]

                    if input_buffer == key_sequence:
                        try:
                            level_index = int(input("Enter level number to load: "))
                        except ValueError:
                            print("Invalid level index")
                        restart_level = True
                        running = False  # Reload

                    if event.key == pygame.K_r:
                        restart_level = True
                        running = False  # Reload current level
            if player.update(platforms, win_tile):
                print(f"Level {level_index} complete!")
                level_index += 1
                break
            moving_platforms.update()
            if player.rect.y > 1000:
                global lives
                pygame.mixer.music.stop()
                pygame.mixer.music.load("images/death.mp3", namehint="mp3")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    1+1
                screen.fill("black")
                my_font = pygame.font.SysFont('Comic Sans MS', 30)
                lives = lives - 1
                if lives >= 0:
                    text_surface = my_font.render('Lives: ' + str(lives), False, (255, 255, 255))
                    screen.blit(text_surface, (50, 100))
                    pygame.display.flip()
                    pygame.time.wait(1000)
                    print(lives)
                    screen.fill("black")
                if lives < 0:
                    screen.fill("black")
                    pygame.mixer.music.load("images/over.mp3", namehint="mp3")
                    pygame.mixer.music.play()
                    my_font = pygame.font.SysFont("Comic Sans MS", 30)
                    text_surface = my_font.render("GAME         OVER", False, (255, 255, 255))
                    screen.blit(text_surface, (400, 100))
                    pygame.display.flip()
                    while pygame.mixer.music.get_busy():
                        1+1
                    screen.fill("black")
                    lives = 5
                    title_screen()
                    play_game()
                    restart_level = True
                    running = False
                else:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load("images/level.mp3", namehint="mp3")
                    pygame.mixer.music.play()
                    restart_level = True
                    running = False
                    # lives = lives - 1
            screen.fill((0, 0, 255))
            all_sprites.draw(screen)
            pygame.display.flip()
            clock.tick(60)

        if level_index == 4:
            boss_fight(5)
            level_index += 1
            continue
        if level_index == 7:
             boss_fight(6)
             level_index += 1
        if level_index == 12:
            boss_fight(3)
            level_index += 1
        if level_index == 13:
            boss_fight(5)
            level_index += 1
        if level_index == 14:
            boss_fight(10)
            level_index += 1
        if level_index == 16:
            boss_fight(1)
            level_index += 1
        if level_index == 18:
            ground_boss_fight(5)
            level_index += 1
        if level_index == 20:
            ground_boss_fight(3)
            boss_fight(3)
            level_index += 1
        if restart_level:
            continue  # Jump to top of while True to reload level


    pygame.quit()
def ground_boss_fight(hits):
    print("GROUND BOSS FIGHT!")
    pygame.mixer.music.load("images/boss.mp3", namehint="mp3")
    pygame.mixer.music.play()

    class GroundBoss(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.image = pygame.Surface((120, 60))
            self.image.fill((200, 0, 0))
            self.rect = self.image.get_rect(bottomleft=(0, SCREEN_HEIGHT - 40))
            self.health = hits
            self.speed = 6
            self.state = "dash"
            self.timer = 0
            self.direction = 1  # 1 for right, -1 for left
            self.cooldown = 60

        def update(self):
            self.timer += 1
            if self.state == "dash":
                self.rect.x += self.speed * self.direction
                if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
                    self.direction *= -1
                    self.state = "shoot"
                    self.timer = 0
            elif self.state == "shoot" and self.timer >= self.cooldown:
                self.state = "throw"
                self.timer = 0
            elif self.state == "throw" and self.timer >= self.cooldown:
                self.state = "dash"
                self.timer = 0

        def hit(self):
            self.health -= 1
            print(f"Boss hit! Health: {self.health}")
            HitSfx.play()

    class Bullet(pygame.sprite.Sprite):
        def __init__(self, x, y, direction):
            super().__init__()
            self.image = pygame.Surface((10, 10))
            self.image.fill((0, 0, 0))
            self.rect = self.image.get_rect(center=(x, y))
            self.speed = 6 * direction

        def update(self):
            self.rect.x += self.speed
            if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
                self.kill()

    class ReflectBox(pygame.sprite.Sprite):
        def __init__(self, x, y, direction):
            super().__init__()
            self.image = pygame.Surface((30, 30))
            self.image.fill((255, 200, 0))
            self.rect = self.image.get_rect(center=(x, y))
            self.direction = direction
            self.used = False
            self.speed_x = 5 * direction

        def update(self):
            if not self.used:
                self.rect.x += self.speed_x
                # self.rect.y += 2  # gravity/arc look
            else:
                for box in boxes:
                    if not box.used and box.rect.colliderect(player.rect):
                        box.used = True  # reflect it
                        box.speed_x *= -1  # reverse direction

                # self.rect.x -= self.speed_x  # Reflect back
                # self.rect.y -= 6

            if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT or self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
                self.kill()

    player = Player()
    player.rect.midbottom = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40)

    boss = GroundBoss()
    bullets = pygame.sprite.Group()
    boxes = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group(player, boss)

    ground = Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40)
    platforms.add(ground)
    all_sprites.add(ground)

    bullet_timer = 0
    box_thrown = False
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                ground_boss_fight(hits)
                return

        if player.update(platforms, WinTile(0, 0)):
            pass

        boss.update()

        # Shooting logic
        if boss.state == "shoot" and boss.timer % 20 == 0:
            bullet_dir = 1 if player.rect.centerx > boss.rect.centerx else -1
            bullet = Bullet(boss.rect.centerx, boss.rect.top, bullet_dir)
            bullets.add(bullet)
            all_sprites.add(bullet)

        # Box throw
        if boss.state == "throw" and not box_thrown:
            box_dir = 1 if player.rect.centerx > boss.rect.centerx else -1
            box = ReflectBox(boss.rect.centerx, boss.rect.centery, box_dir)
            boxes.add(box)
            all_sprites.add(box)
            box_thrown = True


        # Bullet collision with player
        for bullet in bullets:
            if bullet.rect.colliderect(player.rect):
                print("Player hit! Restarting ground boss fight.")
                pygame.mixer.music.stop()
                ground_boss_fight(hits)
                return

        # Box interaction
        for box in boxes:
            if not box.used and box.rect.colliderect(player.rect):
                box.used = True
                box.rect.centerx = boss.rect.centerx  # aim it

            if box.used and box.rect.colliderect(boss.rect):
                boss.hit()
                box.kill()
                box_thrown = False
                if boss.health <= 0:
                    print("Ground Boss defeated!")
                    pygame.mixer.music.stop()
                    HitSfxFinal.play()
                    pygame.mixer.music.load("images/level.mp3", namehint="mp3")
                    pygame.mixer.music.play()
                    return

        bullets.update()
        boxes.update()

        screen.fill((80, 40, 40))
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(60)

def boss_fight(hits):
    print("BOSS FIGHT!")
    pygame.mixer.music.load("images/boss.mp3", namehint="mp3")
    pygame.mixer.music.play()
    class Boss(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.image = pygame.Surface((200, 40))
            self.image.fill((255, 0, 0))
            self.rect = self.image.get_rect(midtop=(SCREEN_WIDTH // 2, 0))
            self.health = hits

        def hit(self):
            self.health -= 1
            print(f"Boss hit! Health: {self.health}")
            HitSfx.play()

    class Bullet(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.image = pygame.Surface((10, 20))
            self.image.fill((0, 0, 0))
            self.rect = self.image.get_rect(center=(x, y))
            self.speed = randint(5,10)

        def update(self):
            self.rect.y += self.speed
            if self.rect.top > SCREEN_HEIGHT:
                self.kill()

    class Box(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.image = pygame.Surface((30, 30))
            self.image.fill((100, 100, 255))
            self.rect = self.image.get_rect(center=(x, y))
            self.used = False
            self.vel_y = 5

        def update(self):
            if not self.used:
                self.rect.y += 4
            else:
                self.rect.y -= 8
            if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
                self.kill()

    player = Player()
    player.rect.x = SCREEN_WIDTH // 2
    player.rect.y = SCREEN_HEIGHT - 100

    boss = Boss()
    all_sprites = pygame.sprite.Group(player, boss)
    bullets = pygame.sprite.Group()
    boxes = pygame.sprite.Group()
    platforms = pygame.sprite.Group()

    # 🆕 Add ground platform
    ground = Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40)
    platforms.add(ground)
    all_sprites.add(ground)



    bullet_timer = 0
    box_timer = 0
    clock = pygame.time.Clock()
    input_buffer = []
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:
                input_buffer.append(event.key)
                input_buffer = input_buffer[-12:]
                if input_buffer == [
                    pygame.K_UP, pygame.K_UP, pygame.K_DOWN, pygame.K_DOWN,
                    pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RIGHT,
                    pygame.K_UP, pygame.K_DOWN, pygame.K_UP, pygame.K_DOWN,
                ]:
                    try:
                        new_level = int(input("Enter level number to load: "))
                        load_level(new_level)
                        return
                    except ValueError:
                        pass

                if event.key == pygame.K_r:
                    boss_fight(hits)
                    return

        if player.update(platforms, WinTile(0, 0)):  # dummy
            pass

        bullet_timer += 1
        box_timer += 1
        if bullet_timer >= randint(0,900):
            bullet = Bullet(randint(0,600), boss.rect.centery)
            bullets.add(bullet)
            all_sprites.add(bullet)
            bullet_timer = 0

        if box_timer >= 120:
            box = Box(randint(0,600), boss.rect.bottom)
            boxes.add(box)
            all_sprites.add(box)
            box_timer = 0

        for bullet in bullets:
            if bullet.rect.colliderect(player.rect):
                print("Hit by bullet! Restarting boss fight.")
                pygame.mixer.music.stop()
                boss_fight(hits)
                return

        for box in boxes:
            if not box.used and box.rect.colliderect(player.rect):
                box.used = True
                box.rect.centerx = boss.rect.centerx

        for box in boxes:
            if box.used and box.rect.colliderect(boss.rect):
                boss.hit()
                box.kill()
                if boss.health <= 0:
                    print("Boss defeated!")
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load("images/level.mp3", namehint="mp3")
                    pygame.mixer.music.play()
                    HitSfxFinal.play()
                    return

        bullets.update()
        boxes.update()

        screen.fill((50, 50, 100))
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(60)
def ending():
    print("ENDING SEQUENCE")
    pygame.mixer.music.load("images/ending.mp3", namehint="mp3")
    pygame.mixer.music.play()

    class Checkmark(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.image = pygame.Surface((50, 50))
            self.image.fill((0, 255, 0))  # Green box as placeholder for checkmark
            self.rect = self.image.get_rect(topleft=(x, y))

    player = Player()
    player.rect.bottomleft = (0, SCREEN_HEIGHT - 40)

    platform = Platform(0, SCREEN_HEIGHT - 40, 1600, 40)
    checkmark = Checkmark(1500, SCREEN_HEIGHT - 90)

    all_sprites = pygame.sprite.Group(player, platform, checkmark)
    platforms = pygame.sprite.Group(platform)

    clock = pygame.time.Clock()
    scroll_x = 0
    timer = 0

    while timer < 1800:  # 30 seconds at 60 FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        player.rect.x += 2
        if player.rect.x - scroll_x > 400:
            scroll_x += 2

        player.update(platforms, WinTile(0, 0))  # dummy win tile

        screen.fill((100, 200, 255))
        for sprite in all_sprites:
            screen.blit(sprite.image, (sprite.rect.x - scroll_x, sprite.rect.y))

        pygame.display.flip()
        clock.tick(60)
        timer += 1

    pygame.time.wait(5000)
    title_screen()
    play_game()
def title_screen():

    pygame.font.init() # you have to call this at the start,
                   # if you want to use this module.

    pygame.mixer.music.load("images/title.mp3", namehint="mp3")
    pygame.mixer.music.play()
    my_font = pygame.font.SysFont('Comic Sans MS', 30)
    text_surface = my_font.render('tailsgame-adv', False, (255, 255, 255))
    screen.blit(text_surface, (50, 100))
    text_surface = my_font.render('Press ENTER', False, (255, 255, 255))
    screen.blit(text_surface, (50, 500))
    runningt = True
    while runningt:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RETURN]:
                    runningt = False
                    pygame.mixer.music.stop()
        pygame.display.flip()
    return


title_screen()
play_game()
