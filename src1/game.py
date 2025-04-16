import pygame
import sys
import pytmx
from config import *
from map_loader import *
from characters import thief_sprites, master_sprites, coin_sprites, THIEF_SIZE, MASTER_SIZE
from ai import create_thief_vision_zone, create_master_vision_zone, master_vision, a_star, master_patrol, master_chase
from utils import check_furniture_collision, find_nearest_free_position
from menu import Menu  # Import Menu từ menu.py

# Danh sách thuật toán
AI_ALGORITHMS = {
    "Breadth-First Search": None,
    "Depth-First Search": None,
    "Uniform Cost Search": None,
    "Iterative Deepening DFS": None,
    "Greedy Best-First Search": None,
    "A* Search": a_star,  # Chỉ A* được triển khai
    "IDA* Search": None,
    "Simple Hill Climbing": None,
    "Steepest Hill Climbing": None,
    "Stochastic Hill Climbing": None,
    "Simulated Annealing": None,
    "Beam Search": None
}

# Danh sách bản đồ
MAPS = {
    "Map 1": "map/1.tmx",
    "Map 2": "map/2.tmx",
    "Map 3": "map/3.tmx",
    "Map 4": "map/4.tmx",
    "Map 5": "map/5.tmx",
    "Map 6": "map/6.tmx",
    "Map 7": "map/7.tmx",
    "Map 8": "map/8.tmx",
    "Map 9": "map/9.tmx"
}

# Khởi tạo menu
menu = Menu(AI_ALGORITHMS, MAPS, background_image="assets/images/menu_background.png")

# Trạng thái trò chơi
state = "menu"  # Bắt đầu ở trạng thái menu
selected_params = None  # Lưu thông số từ menu
current_run = 0  # Đếm số lần thực hiện

# Biến trò chơi
tmx_data = None
map_grid = None
furniture_rects = None
thief_pos = None
master_pos = None
items = None
exit_pos = None

# Vòng lặp chính
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if state == "menu":
            result = menu.handle_event(event, screen)
            if result:
                selected_params = result
                state = "game"
                current_run = 0  # Reset số lần chạy
                # Load bản đồ được chọn
                map_file = MAPS[selected_params["map"]]
                tmx_data = pytmx.load_pygame(map_file)
                GRID_SIZE = tmx_data.tilewidth
                ROWS = tmx_data.height
                COLS = tmx_data.width
                MAP_WIDTH = COLS * GRID_SIZE
                MAP_HEIGHT = ROWS * GRID_SIZE
                scale_factor = min(SCREEN_WIDTH / MAP_WIDTH, SCREEN_HEIGHT / MAP_HEIGHT)
                SCALED_GRID_SIZE = GRID_SIZE * scale_factor
                OFFSET_X = (SCREEN_WIDTH - MAP_WIDTH * scale_factor) // 2
                OFFSET_Y = (SCREEN_HEIGHT - MAP_HEIGHT * scale_factor) // 2
                map_grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
                wall_layer = tmx_data.get_layer_by_name("Wall")
                for x in range(COLS):
                    for y in range(ROWS):
                        if wall_layer.data[y][x] != 0:
                            map_grid[y][x] = 1
                furniture_rects = []
                furniture_layer = tmx_data.get_layer_by_name("FurnitureObjects")
                for obj in furniture_layer:
                    if hasattr(obj, 'x') and hasattr(obj, 'y') and hasattr(obj, 'width') and hasattr(obj, 'height'):
                        scaled_width = obj.width * scale_factor
                        scaled_height = obj.height * scale_factor
                        tile_width_in_grids = obj.width / GRID_SIZE
                        tile_height_in_grids = obj.height / GRID_SIZE
                        offset_x = (SCALED_GRID_SIZE * tile_width_in_grids - scaled_width) / 2
                        offset_y = (SCALED_GRID_SIZE * tile_height_in_grids - scaled_height) / 2
                        draw_x = obj.x * scale_factor + OFFSET_X + offset_x
                        draw_y = obj.y * scale_factor + OFFSET_Y + offset_y
                        furniture_rect = pygame.Rect(draw_x, draw_y, scaled_width, scaled_height)
                        furniture_rects.append(furniture_rect)
                # Load vị trí từ bản đồ
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
                # Khởi tạo các biến trò chơi
                coin_types = ["red", "silver", "gold"]
                item_coins = [(pos, coin_types[i % len(coin_types)]) for i, pos in enumerate(items)]
                exit_img = pygame.Surface((SCALED_GRID_SIZE, SCALED_GRID_SIZE))
                exit_img.fill(WHITE)
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

    if state == "menu":
        menu.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    elif state == "game":
        if current_run < selected_params["num_runs"]:
            if game_over:
                current_run += 1
                if current_run < selected_params["num_runs"]:
                    # Reset trò chơi để chạy lần tiếp theo
                    thief_pos, master_pos, items, exit_pos = load_positions()
                    if thief_pos is None:
                        thief_pos = [1, 1]
                    else:
                        thief_pos = find_nearest_free_position(thief_pos, THIEF_SIZE, furniture_rects, map_grid)
                    if master_pos is None:
                        master_pos = [5, 5]
                    else:
                        master_pos = find_nearest_free_position(master_pos, MASTER_SIZE, furniture_rects, map_grid)
                    if exit_pos is None:
                        exit_pos = [10, 10]
                    item_coins = [(pos, coin_types[i % len(coin_types)]) for i, pos in enumerate(items)]
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
                else:
                    state = "menu"  # Quay lại menu sau khi hoàn thành tất cả các lần chạy
            else:
                # Chọn thuật toán
                algorithm = AI_ALGORITHMS[selected_params["algorithm"]]
                if algorithm is None:
                    print(f"Thuật toán {selected_params['algorithm']} chưa được triển khai!")
                    state = "menu"
                    continue

                # Tìm mục tiêu cho nhân vật trộm
                if collected_items < len(items):
                    path = algorithm(thief_pos, items[collected_items], map_grid, THIEF_SIZE, furniture_rects)
                else:
                    path = algorithm(thief_pos, exit_pos, map_grid, THIEF_SIZE, furniture_rects)

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
                            print(f"Run {current_run + 1}/{selected_params['num_runs']}: Ten trom da thoat")
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
                            else:
                                if master_waypoints:
                                    print("Removing unreachable waypoint:", master_waypoints[0])
                                    master_waypoints.pop(0)
                                    master_path = None
                        else:
                            if master_waypoints:
                                print("Removing unreachable waypoint:", master_waypoints[0])
                                master_waypoints.pop(0)
                                master_path = None
                        master_patrol_counter = 0

                if master_pos == thief_pos:
                    print(f"Run {current_run + 1}/{selected_params['num_runs']}: Ten trom bi bat")
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

                # mode = "Đuổi theo" if master_vision(master_pos, thief_pos) else "Tuần tra"
                # master_status = f"Ông chủ: {master_pos}, Chế độ: {mode}, Hướng trộm: {thief_direction}"
                # status_text = font.render(master_status, True, BLACK)
                # screen.blit(status_text, (10, 10))

                pygame.display.flip()
                clock.tick(10)
