import pygame
from config import *

def load_thief_sprites(scaled_grid_size):
    # Load sprite sheet cho nhân vật thief
    try:
        thief_sprite_sheet = pygame.image.load("assets/images/Player.png")
    except pygame.error as e:
        print(f"Error loading thief sprite sheet: {e}")
        thief_sprite_sheet = pygame.Surface((scaled_grid_size * 4, scaled_grid_size * 4))
        thief_sprite_sheet.fill(RED)

    # Cắt sprite sheet
    SPRITE_ROWS = 4
    SPRITE_COLS = 4
    sprite_width = thief_sprite_sheet.get_width() // SPRITE_COLS
    sprite_height = thief_sprite_sheet.get_height() // SPRITE_ROWS

    THIEF_SCALE_FACTOR = 1.5
    THIEF_SIZE = int(scaled_grid_size * THIEF_SCALE_FACTOR)

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

    return thief_sprites, THIEF_SIZE

def load_master_sprites(scaled_grid_size):
    # Load sprite sheet cho master
    try:
        master_sprite_sheet = pygame.image.load("assets/images/MasterWalk.png")
    except pygame.error as e:
        print(f"Error loading master sprite sheet: {e}")
        master_sprite_sheet = pygame.Surface((scaled_grid_size * 4, scaled_grid_size * 4))
        master_sprite_sheet.fill(BLUE)

    # Cắt sprite sheet
    SPRITE_ROWS = 4
    SPRITE_COLS = 4
    sprite_width = master_sprite_sheet.get_width() // SPRITE_COLS
    sprite_height = master_sprite_sheet.get_height() // SPRITE_ROWS

    MASTER_SCALE_FACTOR = 1.5
    MASTER_SIZE = int(scaled_grid_size * MASTER_SCALE_FACTOR)

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

    return master_sprites, MASTER_SIZE

def load_master_idle_sprites(scaled_grid_size):
    # Load sprite sheet cho master idle
    try:
        master_idle_sprite_sheet = pygame.image.load("assets/images/MasterIdle.png")
    except pygame.error as e:
        print(f"Error loading master idle sprite sheet: {e}")
        master_idle_sprite_sheet = pygame.Surface((scaled_grid_size * 4, scaled_grid_size))
        master_idle_sprite_sheet.fill(BLUE)

    # Cắt sprite sheet (1 hàng, 4 cột)
    SPRITE_ROWS = 1
    SPRITE_COLS = 4
    sprite_width = master_idle_sprite_sheet.get_width() // SPRITE_COLS
    sprite_height = master_idle_sprite_sheet.get_height() // SPRITE_ROWS

    MASTER_SCALE_FACTOR = 1.5
    MASTER_SIZE = int(scaled_grid_size * MASTER_SCALE_FACTOR)

    # Cắt sprite sheet cho master idle
    master_idle_sprites = {"down": [], "up": [], "left": [], "right": []}
    for row in range(SPRITE_ROWS):
        for col in range(SPRITE_COLS):
            sprite_rect = pygame.Rect(col * sprite_width, row * sprite_height, sprite_width, sprite_height)
            sprite_image = master_idle_sprite_sheet.subsurface(sprite_rect)
            sprite_image = pygame.transform.scale(sprite_image, (MASTER_SIZE, MASTER_SIZE))
            if col == 0:
                master_idle_sprites["down"].append(sprite_image)
            elif col == 1:
                master_idle_sprites["up"].append(sprite_image)
            elif col == 2:
                master_idle_sprites["left"].append(sprite_image)
            elif col == 3:
                master_idle_sprites["right"].append(sprite_image)

    return master_idle_sprites

def load_coin_sprites(scaled_grid_size):
    COIN_SIZE = 16
    COIN_FRAMES = 5
    COIN_SCALE_FACTOR = scaled_grid_size / COIN_SIZE

    coin_sprites = {"red": [], "silver": [], "gold": []}

    # Load red coin
    try:
        red_coin_sheet = pygame.image.load("assets/images/coin/ruby.png")
        for i in range(COIN_FRAMES):
            frame_rect = pygame.Rect(i * COIN_SIZE, 0, COIN_SIZE, COIN_SIZE)
            frame = red_coin_sheet.subsurface(frame_rect)
            frame = pygame.transform.scale(frame, (int(scaled_grid_size), int(scaled_grid_size)))
            coin_sprites["red"].append(frame)
    except pygame.error as e:
        print(f"Error loading red coin sprite sheet: {e}")
        for i in range(COIN_FRAMES):
            frame = pygame.Surface((scaled_grid_size, scaled_grid_size))
            frame.fill(GREEN)
            coin_sprites["red"].append(frame)

    # Load silver coin
    try:
        silver_coin_sheet = pygame.image.load("assets/images/coin/silver.png")
        for i in range(COIN_FRAMES):
            frame_rect = pygame.Rect(i * COIN_SIZE, 0, COIN_SIZE, COIN_SIZE)
            frame = silver_coin_sheet.subsurface(frame_rect)
            frame = pygame.transform.scale(frame, (int(scaled_grid_size), int(scaled_grid_size)))
            coin_sprites["silver"].append(frame)
    except pygame.error as e:
        print(f"Error loading silver coin sprite sheet: {e}")
        for i in range(COIN_FRAMES):
            frame = pygame.Surface((scaled_grid_size, scaled_grid_size))
            frame.fill(GREEN)
            coin_sprites["silver"].append(frame)

    # Load gold coin
    try:
        gold_coin_sheet = pygame.image.load("assets/images/coin/gold.png")
        for i in range(COIN_FRAMES):
            frame_rect = pygame.Rect(i * COIN_SIZE, 0, COIN_SIZE, COIN_SIZE)
            frame = gold_coin_sheet.subsurface(frame_rect)
            frame = pygame.transform.scale(frame, (int(scaled_grid_size), int(scaled_grid_size)))
            coin_sprites["gold"].append(frame)
    except pygame.error as e:
        print(f"Error loading gold coin sprite sheet: {e}")
        for i in range(COIN_FRAMES):
            frame = pygame.Surface((scaled_grid_size, scaled_grid_size))
            frame.fill(GREEN)
            coin_sprites["gold"].append(frame)

    return coin_sprites

def load_trap_sprites(scaled_grid_size):
    # Load sprite sheet cho bẫy
    TRAP_SIZE = int(scaled_grid_size)  # Tương tự nhân vật
    SPRITE_WIDTH = 32
    SPRITE_HEIGHT = 32
    FRAME_COUNT = 14

    trap_sprites = {"spike": [], "fire": []}

    # Load Spike Trap
    try:
        spike_trap_sheet = pygame.image.load("assets/images/Spike_Trap.png")
        for i in range(FRAME_COUNT):
            frame_rect = pygame.Rect(i * SPRITE_WIDTH, 0, SPRITE_WIDTH, SPRITE_HEIGHT)
            frame = spike_trap_sheet.subsurface(frame_rect)
            frame = pygame.transform.scale(frame, (TRAP_SIZE, TRAP_SIZE))
            trap_sprites["spike"].append(frame)
    except pygame.error as e:
        print(f"Error loading spike trap sprite sheet: {e}")
        for i in range(FRAME_COUNT):
            frame = pygame.Surface((TRAP_SIZE, TRAP_SIZE))
            frame.fill(RED)
            trap_sprites["spike"].append(frame)

    # Load fire Trap
    try:
        fire_trap_sheet = pygame.image.load("assets/images/Fire_Trap.png")
        for i in range(FRAME_COUNT):
            frame_rect = pygame.Rect(i * SPRITE_WIDTH, 0, SPRITE_WIDTH, SPRITE_HEIGHT)
            frame = fire_trap_sheet.subsurface(frame_rect)
            frame = pygame.transform.scale(frame, (TRAP_SIZE, TRAP_SIZE))
            trap_sprites["fire"].append(frame)
    except pygame.error as e:
        print(f"Error loading fire trap sprite sheet: {e}")
        for i in range(FRAME_COUNT):
            frame = pygame.Surface((TRAP_SIZE, TRAP_SIZE))
            frame.fill(YELLOW)
            trap_sprites["fire"].append(frame)

    return trap_sprites, TRAP_SIZE