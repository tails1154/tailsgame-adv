import pygame
import json
import os

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLATFORM_WIDTH = 100
PLATFORM_HEIGHT = 20
WIN_TILE_SIZE = 50
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Level Editor")

class EditorPlatform(pygame.sprite.Sprite):
    def __init__(self, x, y, type="static", move_range=0):
        super().__init__()
        self.type = type
        self.range = move_range
        self.image = pygame.Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
        self.image.fill((0, 0, 0) if type == "static" else (0, 0, 255))
        self.rect = self.image.get_rect(topleft=(x, y))

class WinTile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((WIN_TILE_SIZE, WIN_TILE_SIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(topleft=(x, y))

def save_level(platforms, win_tile, index):
    os.makedirs("maps", exist_ok=True)
    data = {
        "platforms": [{
            "x": p.rect.x,
            "y": p.rect.y,
            "width": PLATFORM_WIDTH,
            "height": PLATFORM_HEIGHT,
            "type": p.type,
            "range": p.range
        } for p in platforms],
        "win_tile": {"x": win_tile.rect.x, "y": win_tile.rect.y} if win_tile else {"x": 700, "y": 250}
    }
    with open(f"maps/level{index}.json", "w") as f:
        json.dump(data, f, indent=4)
    print(f"Saved to maps/level{index}.json")

def load_level(index):
    path = f"maps/level{index}.json"
    if not os.path.exists(path):
        print("Level file not found.")
        return [], None
    with open(path) as f:
        data = json.load(f)

    platforms = pygame.sprite.Group()
    for p in data["platforms"]:
        plat = EditorPlatform(p["x"], p["y"], p.get("type", "static"), p.get("range", 0))
        platforms.add(plat)
    win_tile = WinTile(data["win_tile"]["x"], data["win_tile"]["y"])
    return platforms, win_tile

def prompt_level_action():
    while True:
        choice = input("N = New level, L = Load level: ").strip().lower()
        if choice in ['n', 'l']:
            break
    level_index = int(input("Level number: "))
    return choice, level_index

def level_editor_loop():
    action, level_index = prompt_level_action()

    if action == 'l':
        platforms, win_tile = load_level(level_index)
    else:
        platforms = pygame.sprite.Group()
        win_tile = None

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                if not win_tile:
                    win_tile = WinTile(x - WIN_TILE_SIZE//2, y - WIN_TILE_SIZE//2)
                else:
                    platforms.add(EditorPlatform(x - PLATFORM_WIDTH//2, y - PLATFORM_HEIGHT//2))

            if event.type == pygame.KEYDOWN:
                x, y = pygame.mouse.get_pos()

                if event.key == pygame.K_m:  # Add moving platform
                    platforms.add(EditorPlatform(x - PLATFORM_WIDTH//2, y - PLATFORM_HEIGHT//2, type="moving", move_range=100))

                elif event.key == pygame.K_p:  # Edit range of moving platform
                    for p in platforms:
                        if p.rect.collidepoint((x, y)) and p.type == "moving":
                            try:
                                new_range = int(input("Enter new vertical range in pixels: "))
                                p.range = new_range
                            except ValueError:
                                print("Invalid input.")
                            break

                elif event.key == pygame.K_BACKSPACE:
                    for p in platforms:
                        if p.rect.collidepoint((x, y)):
                            platforms.remove(p)
                            break
                    if win_tile and win_tile.rect.collidepoint((x, y)):
                        win_tile = None

                elif event.key == pygame.K_s:
                    save_level(platforms, win_tile, level_index)

        screen.fill(WHITE)
        platforms.draw(screen)
        if win_tile:
            screen.blit(win_tile.image, win_tile.rect)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    level_editor_loop()
