import pygame
import sys
from config import *
from map_loader import *
from characters import thief_sprites, master_sprites, coin_sprites, THIEF_SIZE, MASTER_SIZE
from ai import create_thief_vision_zone, create_master_vision_zone, master_vision, a_star, master_patrol, master_chase
from utils import check_furniture_collision, find_nearest_free_position
from config import *

# Khởi tạo game
thief_pos, master_pos, items, exit_pos = load_positions()

if thief_pos is None:
    print("Warning: Thief position not found in the map! Using default position.")
    thief_pos = [1, 1]
else:
    thief_pos = find_nearest_free_position(thief_pos, THIEF_SIZE, furniture_rects, map_grid)

if master_pos is None:
    print("Warning: Master position not found in the map! Using default position.")
    master_pos = [5, 5]
else:
    master_pos = find_nearest_free_position(master_pos, MASTER_SIZE, furniture_rects, map_grid)

if exit_pos is None:
    print("Warning: Exit position not found in the map! Using default position.")
    exit_pos = [10, 10]

coin_types = ["red", "silver", "gold"]
item_coins = [(pos, coin_types[i % len(coin_types)]) for i, pos in enumerate(items)]
exit_img = pygame.Surface((SCALED_GRID_SIZE, SCALED_GRID_SIZE))
exit_img.fill(WHITE)

# Biến trạng thái game
collected_items = 0
path = None
master_waypoints = []
master_path = None
game_over = False
thief_direction = "right"
master_direction = "right"
thief_frame = 0
master_frame = 0
coin_frame = 0
frame_counter = 0
master_patrol_counter = 0

# Vòng lặp chính
clock = pygame.time.Clock()
while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Tìm mục tiêu cho nhân vật trộm
    if collected_items < len(items):
        path = a_star(thief_pos, items[collected_items], map_grid, THIEF_SIZE, furniture_rects)
    else:
        path = a_star(thief_pos, exit_pos, map_grid, THIEF_SIZE, furniture_rects)

    # Di chuyển nhân vật trộm và cập nhật hướng
    if path and len(path) > 1:
        next_pos = path[1]
        if not check_furniture_collision(next_pos, THIEF_SIZE, furniture_rects):
            dx = next_pos[0] - thief_pos[0]
            dy = next_pos[1] - thief_pos[1]
            if dx == -1:
                thief_direction = "up"
            elif dx == 1:
                thief_direction = "down"
            elif dy == -1:
                thief_direction = "left"
            elif dy == 1:
                thief_direction = "right"
            thief_pos = next_pos
            path.pop(0)

            for i, (item_pos, _) in enumerate(item_coins):
                if thief_pos == item_pos:
                    item_coins.pop(i)
                    collected_items += 1
                    break

            if thief_pos == exit_pos and collected_items == len(items):
                print("Tên trộm đã thoát!")
                game_over = True
        else:
            path = None

    # Di chuyển ông chủ
    if master_vision(master_pos, thief_pos):
        master_path = master_chase(master_pos, thief_pos)
        if master_path and len(master_path) > 1:
            next_pos = master_path[1]
            if not check_furniture_collision(next_pos, MASTER_SIZE, furniture_rects):
                dx = next_pos[0] - master_pos[0]
                dy = next_pos[1] - master_pos[1]
                if dx == -1:
                    master_direction = "up"
                elif dx == 1:
                    master_direction = "down"
                elif dy == -1:
                    master_direction = "left"
                elif dy == 1:
                    master_direction = "right"
                master_pos = next_pos
                master_path.pop(0)
    else:
        if master_path is None or len(master_path) <= 1:
            master_path = master_patrol(master_pos, master_waypoints)
        master_patrol_counter += 1
        if master_patrol_counter >= 2:
            if master_path and len(master_path) > 1:
                next_pos = master_path[1]
                if not check_furniture_collision(next_pos, MASTER_SIZE, furniture_rects):
                    dx = next_pos[0] - master_pos[0]
                    dy = next_pos[1] - master_pos[1]
                    if dx == -1:
                        master_direction = "up"
                    elif dx == 1:
                        master_direction = "down"
                    elif dy == -1:
                        master_direction = "left"
                    elif dy == 1:
                        master_direction = "right"
                    master_pos = next_pos
                    master_path.pop(0)
            master_patrol_counter = 0

    if master_pos == thief_pos:
        print("Bị ông chủ bắt!")
        game_over = True

    # Cập nhật frame cho hoạt hình
    frame_counter += 1
    if frame_counter >= FRAME_RATE:
        thief_frame = (thief_frame + 1) % len(thief_sprites[thief_direction])
        master_frame = (master_frame + 1) % len(master_sprites[master_direction])
        coin_frame = (coin_frame + 1) % 5
        frame_counter = 0

    # Vẽ game
    screen.fill(GRAY)
    draw_map(screen, tmx_data)

    thief_vision_zone = create_thief_vision_zone(thief_pos, thief_direction)
    for i, j in thief_vision_zone:
        pygame.draw.rect(screen, LIGHT_BLUE, (j * SCALED_GRID_SIZE + OFFSET_X, i * SCALED_GRID_SIZE + OFFSET_Y, SCALED_GRID_SIZE, SCALED_GRID_SIZE), width=2)

    master_vision_zone = create_master_vision_zone(master_pos)
    for i, j in master_vision_zone:
        pygame.draw.rect(screen, LIGHT_PURPLE, (j * SCALED_GRID_SIZE + OFFSET_X, i * SCALED_GRID_SIZE + OFFSET_Y, SCALED_GRID_SIZE, SCALED_GRID_SIZE), width=2)

    thief_img = thief_sprites[thief_direction][thief_frame]
    screen.blit(thief_img, (thief_pos[1] * SCALED_GRID_SIZE + OFFSET_X, thief_pos[0] * SCALED_GRID_SIZE + OFFSET_Y))

    master_img = master_sprites[master_direction][master_frame]
    screen.blit(master_img, (master_pos[1] * SCALED_GRID_SIZE + OFFSET_X, master_pos[0] * SCALED_GRID_SIZE + OFFSET_Y))

    for item_pos, coin_type in item_coins:
        coin_img = coin_sprites[coin_type][coin_frame]
        screen.blit(coin_img, (item_pos[1] * SCALED_GRID_SIZE + OFFSET_X, item_pos[0] * SCALED_GRID_SIZE + OFFSET_Y))

    screen.blit(exit_img, (exit_pos[1] * SCALED_GRID_SIZE + OFFSET_X, exit_pos[0] * SCALED_GRID_SIZE + OFFSET_Y))

    mode = "Đuổi theo" if master_vision(master_pos, thief_pos) else "Tuần tra"
    master_status = f"Ông chủ: {master_pos}, Chế độ: {mode}, Hướng trộm: {thief_direction}"
    status_text = font.render(master_status, True, BLACK)
    screen.blit(status_text, (10, 10))

    pygame.display.flip()
    clock.tick(10)