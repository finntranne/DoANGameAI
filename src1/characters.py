import pygame
from config import *
from map_loader import *

# Load sprite sheet cho nhân vật thief
try:
    thief_sprite_sheet = pygame.image.load("assets/images/Player.png")
except pygame.error as e:
    print(f"Error loading thief sprite sheet: {e}")
    thief_sprite_sheet = pygame.Surface((SCALED_GRID_SIZE * 4, SCALED_GRID_SIZE * 4))
    thief_sprite_sheet.fill(RED)

# Load sprite sheet cho master
try:
    master_sprite_sheet = pygame.image.load("assets/images/Master.png")
except pygame.error as e:
    print(f"Error loading master sprite sheet: {e}")
    master_sprite_sheet = pygame.Surface((SCALED_GRID_SIZE * 4, SCALED_GRID_SIZE * 4))
    master_sprite_sheet.fill(BLUE)

# Cắt sprite sheet
SPRITE_ROWS = 4
SPRITE_COLS = 4
sprite_width = thief_sprite_sheet.get_width() // SPRITE_COLS
sprite_height = thief_sprite_sheet.get_height() // SPRITE_ROWS

THIEF_SCALE_FACTOR = 1.5
THIEF_SIZE = int(SCALED_GRID_SIZE * THIEF_SCALE_FACTOR)
MASTER_SIZE = THIEF_SIZE

# Cắt sprite sheet cho thief
thief_sprites = {"down": [], "up": [], "left": [], "right": []}
for row in range(SPRITE_ROWS):
    for col in range(SPRITE_COLS):
        sprite_rect = pygame.Rect(col * sprite_width, row * sprite_height, sprite_width, sprite_height)
        sprite_image = thief_sprite_sheet.subsurface(sprite_rect)
        sprite_image = pygame.transform.scale(sprite_image, (THIEF_SIZE, THIEF_SIZE))
        if col == 0:
            thief_sprites["down"].append(sprite_image)
        elif col == 1:
            thief_sprites["up"].append(sprite_image)
        elif col == 2:
            thief_sprites["left"].append(sprite_image)
        elif col == 3:
            thief_sprites["right"].append(sprite_image)

# Cắt sprite sheet cho master
master_sprites = {"down": [], "up": [], "left": [], "right": []}
for row in range(SPRITE_ROWS):
    for col in range(SPRITE_COLS):
        sprite_rect = pygame.Rect(col * sprite_width, row * sprite_height, sprite_width, sprite_height)
        sprite_image = master_sprite_sheet.subsurface(sprite_rect)
        sprite_image = pygame.transform.scale(sprite_image, (MASTER_SIZE, MASTER_SIZE))
        if col == 0:
            master_sprites["down"].append(sprite_image)
        elif col == 1:
            master_sprites["up"].append(sprite_image)
        elif col == 2:
            master_sprites["left"].append(sprite_image)
        elif col == 3:
            master_sprites["right"].append(sprite_image)

# Load sprite sheet cho đồng xu
COIN_SIZE = 16
COIN_FRAMES = 5
COIN_SCALE_FACTOR = SCALED_GRID_SIZE / COIN_SIZE

coin_sprites = {"red": [], "silver": [], "gold": []}

# Load red coin
try:
    red_coin_sheet = pygame.image.load("assets/images/coin/ruby.png")
    for i in range(COIN_FRAMES):
        frame_rect = pygame.Rect(i * COIN_SIZE, 0, COIN_SIZE, COIN_SIZE)
        frame = red_coin_sheet.subsurface(frame_rect)
        frame = pygame.transform.scale(frame, (int(SCALED_GRID_SIZE), int(SCALED_GRID_SIZE)))
        coin_sprites["red"].append(frame)
except pygame.error as e:
    print(f"Error loading red coin sprite sheet: {e}")
    for i in range(COIN_FRAMES):
        frame = pygame.Surface((SCALED_GRID_SIZE, SCALED_GRID_SIZE))
        frame.fill(GREEN)
        coin_sprites["red"].append(frame)

# Load silver coin
try:
    silver_coin_sheet = pygame.image.load("assets/images/coin/silver.png")
    for i in range(COIN_FRAMES):
        frame_rect = pygame.Rect(i * COIN_SIZE, 0, COIN_SIZE, COIN_SIZE)
        frame = silver_coin_sheet.subsurface(frame_rect)
        frame = pygame.transform.scale(frame, (int(SCALED_GRID_SIZE), int(SCALED_GRID_SIZE)))
        coin_sprites["silver"].append(frame)
except pygame.error as e:
    print(f"Error loading silver coin sprite sheet: {e}")
    for i in range(COIN_FRAMES):
        frame = pygame.Surface((SCALED_GRID_SIZE, SCALED_GRID_SIZE))
        frame.fill(GREEN)
        coin_sprites["silver"].append(frame)

# Load gold coin
try:
    gold_coin_sheet = pygame.image.load("assets/images/coin/gold.png")
    for i in range(COIN_FRAMES):
        frame_rect = pygame.Rect(i * COIN_SIZE, 0, COIN_SIZE, COIN_SIZE)
        frame = gold_coin_sheet.subsurface(frame_rect)
        frame = pygame.transform.scale(frame, (int(SCALED_GRID_SIZE), int(SCALED_GRID_SIZE)))
        coin_sprites["gold"].append(frame)
except pygame.error as e:
    print(f"Error loading gold coin sprite sheet: {e}")
    for i in range(COIN_FRAMES):
        frame = pygame.Surface((SCALED_GRID_SIZE, SCALED_GRID_SIZE))
        frame.fill(GREEN)
        coin_sprites["gold"].append(frame)