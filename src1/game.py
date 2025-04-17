import pygame
import sys
import pytmx
from config import *
from map_loader import *
from characters import *
from ai import *
from utils import *
from menu import Menu

# Khởi tạo pygame.mixer để xử lý âm thanh
pygame.mixer.init()

# Load âm thanh
try:
    success_sound = pygame.mixer.Sound("assets/sounds/Success.wav")
    game_over_sound = pygame.mixer.Sound("assets/sounds/GameOver.wav")
except pygame.error as e:
    print(f"Error loading sound: {e}")
    success_sound = None
    game_over_sound = None

# Danh sách thuật toán
AI_ALGORITHMS = {
    "Breadth-First Search": bfs,
    "Depth-First Search": dfs,
    "Uniform Cost Search": uniform_cost_search,
    "Iterative Deepening DFS": iddfs,
    "Greedy Best-First Search": greedy_best_first_search,
    "A* Search": a_star,
    "IDA* Search": ida_star,
    "Simple Hill Climbing": simple_hill_climbing,
    "Steepest Hill Climbing": steepest_hill_climbing,
    "Stochastic Hill Climbing": stochastic_hill_climbing,
    "Simulated Annealing": simulated_annealing,
    "Beam Search": beam_search
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
state = "menu"
selected_params = None
current_run = 0

# Biến trò chơi
tmx_data = None
map_grid = None
furniture_rects = None
thief_pos = None
master_pos = None
items = None
traps = None
exit_pos = None
map_data = None
map_file = None
thief_sprites = None
master_sprites = None
coin_sprites = None
trap_sprites = None
THIEF_SIZE = None
MASTER_SIZE = None
TRAP_SIZE = None

def transition_effect(screen, message, color, duration=2000):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.fill(color)
    overlay.set_alpha(0)

    font = pygame.font.Font("assets/fonts/PressStart2P.ttf", 80)
    text_surface = font.render(message, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    transition_duration = duration
    start_time = pygame.time.get_ticks()

    while True:
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - start_time

        alpha = min(255, (elapsed_time / transition_duration) * 255)
        overlay.set_alpha(int(alpha))

        screen.blit(overlay, (0, 0))
        screen.blit(text_surface, text_rect)
        pygame.display.flip()

        if elapsed_time >= transition_duration:
            break

        pygame.time.wait(10)

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
                current_run = 0
                # Load bản đồ được chọn
                map_file = MAPS[selected_params["map"]]
                map_data = load_map(map_file)
                # Extract map data
                tmx_data = map_data["tmx_data"]
                GRID_SIZE = map_data["GRID_SIZE"]
                ROWS = map_data["ROWS"]
                COLS = map_data["COLS"]
                MAP_WIDTH = map_data["MAP_WIDTH"]
                MAP_HEIGHT = map_data["MAP_HEIGHT"]
                scale_factor = map_data["scale_factor"]
                SCALED_GRID_SIZE = map_data["SCALED_GRID_SIZE"]
                OFFSET_X = map_data["OFFSET_X"]
                OFFSET_Y = map_data["OFFSET_Y"]
                map_grid = map_data["map_grid"]
                furniture_rects = map_data["furniture_rects"]
                # Load sprites với SCALED_GRID_SIZE
                thief_sprites, THIEF_SIZE = load_thief_sprites(SCALED_GRID_SIZE)
                master_sprites, MASTER_SIZE = load_master_sprites(SCALED_GRID_SIZE)
                coin_sprites = load_coin_sprites(SCALED_GRID_SIZE)
                trap_sprites, TRAP_SIZE = load_trap_sprites(SCALED_GRID_SIZE)
                # Load vị trí từ bản đồ
                thief_pos, master_pos, items, traps, exit_pos = load_positions(tmx_data)
                print(f"Loaded traps: {traps}")  # Debug: Kiểm tra danh sách bẫy
                if not traps:
                    print("Warning: No traps found in the map!")
                if thief_pos is None:
                    print("Warning: Thief position not found in the map! Using default position.")
                    thief_pos = [1, 1]
                else:
                    thief_pos = find_nearest_free_position(thief_pos, THIEF_SIZE, furniture_rects, map_grid, 
                                                          SCALED_GRID_SIZE, OFFSET_X, OFFSET_Y, ROWS, COLS)
                if master_pos is None:
                    print("Warning: Master position not found in the map! Using default position.")
                    master_pos = [5, 5]
                else:
                    master_pos = find_nearest_free_position(master_pos, MASTER_SIZE, furniture_rects, map_grid, 
                                                           SCALED_GRID_SIZE, OFFSET_X, OFFSET_Y, ROWS, COLS)
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
                trap_frame = 0
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
                    thief_pos, master_pos, items, traps, exit_pos = load_positions(tmx_data)
                    print(f"Reloaded traps for run {current_run + 1}: {traps}")  # Debug: Kiểm tra danh sách bẫy khi reset
                    if not traps:
                        print("Warning: No traps found in the map during reset!")
                    if thief_pos is None:
                        thief_pos = [1, 1]
                    else:
                        thief_pos = find_nearest_free_position(thief_pos, THIEF_SIZE, furniture_rects, map_grid, 
                                                              SCALED_GRID_SIZE, OFFSET_X, OFFSET_Y, ROWS, COLS)
                    if master_pos is None:
                        master_pos = [5, 5]
                    else:
                        master_pos = find_nearest_free_position(master_pos, MASTER_SIZE, furniture_rects, map_grid, 
                                                               SCALED_GRID_SIZE, OFFSET_X, OFFSET_Y, ROWS, COLS)
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
                    trap_frame = 0
                    frame_counter = 0
                    master_patrol_counter = 0
                else:
                    state = "menu"
            else:
                # Chọn thuật toán
                algorithm = AI_ALGORITHMS[selected_params["algorithm"]]
                if algorithm is None:
                    print(f"Thuật toán {selected_params['algorithm']} chưa được triển khai!")
                    state = "menu"
                    continue

                # Tìm mục tiêu cho nhân vật trộm
                if collected_items < len(items):
                    path = algorithm(thief_pos, items[collected_items], map_grid, THIEF_SIZE, furniture_rects, 
                                     SCALED_GRID_SIZE, OFFSET_X, OFFSET_Y, ROWS, COLS)
                else:
                    path = algorithm(thief_pos, exit_pos, map_grid, THIEF_SIZE, furniture_rects, 
                                     SCALED_GRID_SIZE, OFFSET_X, OFFSET_Y, ROWS, COLS)

                # Di chuyển nhân vật trộm và cập nhật hướng
                if path and len(path) > 1:
                    next_pos = path[1]
                    if not check_furniture_collision(next_pos, THIEF_SIZE, furniture_rects, SCALED_GRID_SIZE, OFFSET_X, OFFSET_Y):
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
                            if success_sound:
                                success_sound.play()
                            transition_effect(screen, "Success!", (0, 255, 0))
                            game_over = True
                    else:
                        path = None

                # Kiểm tra va chạm với bẫy
                trap_type = check_trap_collision(thief_pos, THIEF_SIZE, traps, SCALED_GRID_SIZE, OFFSET_X, OFFSET_Y)
                if trap_type:
                    print(f"Run {current_run + 1}/{selected_params['num_runs']}: Ten trom bi bat boi {trap_type} trap")
                    if game_over_sound:
                        game_over_sound.play()
                    transition_effect(screen, "Game Over!", (255, 0, 0))
                    game_over = True

                # Di chuyển ông chủ
                if master_vision(master_pos, thief_pos, ROWS, COLS):
                    master_path = master_chase(master_pos, thief_pos, map_grid, MASTER_SIZE, furniture_rects, 
                                              SCALED_GRID_SIZE, OFFSET_X, OFFSET_Y, ROWS, COLS)
                    if master_path and len(master_path) > 1:
                        next_pos = master_path[1]
                        if not check_furniture_collision(next_pos, MASTER_SIZE, furniture_rects, SCALED_GRID_SIZE, OFFSET_X, OFFSET_Y):
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
                        master_path = master_patrol(master_pos, master_waypoints, map_grid, ROWS, COLS, MASTER_SIZE, 
                                                   furniture_rects, SCALED_GRID_SIZE, OFFSET_X, OFFSET_Y)
                    master_patrol_counter += 1
                    if master_patrol_counter >= 2:
                        if master_path and len(master_path) > 1:
                            next_pos = master_path[1]
                            if not check_furniture_collision(next_pos, MASTER_SIZE, furniture_rects, SCALED_GRID_SIZE, OFFSET_X, OFFSET_Y):
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
                    if game_over_sound:
                        game_over_sound.play()
                    transition_effect(screen, "Game Over!", (255, 0, 0))
                    game_over = True

                # Cập nhật frame cho hoạt hình
                frame_counter += 1
                if frame_counter >= FRAME_RATE:
                    thief_frame = (thief_frame + 1) % len(thief_sprites[thief_direction])
                    master_frame = (master_frame + 1) % len(master_sprites[master_direction])
                    coin_frame = (coin_frame + 1) % 5
                    trap_frame = (trap_frame + 1) % 14  # 14 frames cho bẫy theo load_trap_sprites
                    frame_counter = 0

                # Vẽ game
                screen.fill(GRAY)
                draw_map(screen, tmx_data, map_data, map_file)

                thief_vision_zone = create_thief_vision_zone(thief_pos, thief_direction, ROWS, COLS)
                for i, j in thief_vision_zone:
                    pygame.draw.rect(screen, LIGHT_BLUE, (j * SCALED_GRID_SIZE + OFFSET_X, i * SCALED_GRID_SIZE + OFFSET_Y, SCALED_GRID_SIZE, SCALED_GRID_SIZE), width=2)

                master_vision_zone = create_master_vision_zone(master_pos, ROWS, COLS)
                for i, j in master_vision_zone:
                    pygame.draw.rect(screen, LIGHT_PURPLE, (j * SCALED_GRID_SIZE + OFFSET_X, i * SCALED_GRID_SIZE + OFFSET_Y, SCALED_GRID_SIZE, SCALED_GRID_SIZE), width=2)

                # Vẽ bẫy
                for trap in traps:
                    trap_img = trap_sprites[trap["type"]][trap_frame]
                    draw_x = trap["pos"][1] * SCALED_GRID_SIZE + OFFSET_X
                    draw_y = trap["pos"][0] * SCALED_GRID_SIZE + OFFSET_Y
                    print(f"Drawing trap {trap['type']} at ({draw_x}, {draw_y})")  # Debug: Kiểm tra tọa độ vẽ bẫy
                    screen.blit(trap_img, (int(draw_x), int(draw_y)))

                thief_img = thief_sprites[thief_direction][thief_frame]
                screen.blit(thief_img, (thief_pos[1] * SCALED_GRID_SIZE + OFFSET_X, thief_pos[0] * SCALED_GRID_SIZE + OFFSET_Y))

                master_img = master_sprites[master_direction][master_frame]
                screen.blit(master_img, (master_pos[1] * SCALED_GRID_SIZE + OFFSET_X, master_pos[0] * SCALED_GRID_SIZE + OFFSET_Y))

                for item_pos, coin_type in item_coins:
                    coin_img = coin_sprites[coin_type][coin_frame]
                    screen.blit(coin_img, (item_pos[1] * SCALED_GRID_SIZE + OFFSET_X, item_pos[0] * SCALED_GRID_SIZE + OFFSET_Y))

                screen.blit(exit_img, (exit_pos[1] * SCALED_GRID_SIZE + OFFSET_X, exit_pos[0] * SCALED_GRID_SIZE + OFFSET_Y))

                pygame.display.flip()
                clock.tick(10)