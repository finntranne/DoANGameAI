import pygame
import sys
import pytmx
import csv
import time
import os
from config import *
from map_loader import *
from characters import *
from ai import *
from utils import *
from menu import Menu, OptionMenu

# Khởi tạo pygame.mixer để xử lý âm thanh
pygame.mixer.init()

# Load âm thanh hiệu ứng
try:
    success_sound = pygame.mixer.Sound(SOUND_FILES["success"])
    game_over_sound = pygame.mixer.Sound(SOUND_FILES["game_over"])
    gold_sound = pygame.mixer.Sound(SOUND_FILES["gold"])
    hurt_sound = pygame.mixer.Sound(SOUND_FILES["hurt"])
    alert_sound = pygame.mixer.Sound(SOUND_FILES.get("alert", "assets/sounds/alert.wav"))
    escaped_sound = pygame.mixer.Sound(SOUND_FILES["escaped"])
except pygame.error as e:
    print(f"Error loading sound: {e}")
    success_sound = None
    game_over_sound = None
    gold_sound = None
    hurt_sound = None
    alert_sound = None
    escaped_sound = None

# Load nhạc nền cho game
try:
    fun_music = pygame.mixer.Sound(SOUND_FILES["fun_music"])
    dramatic_music = pygame.mixer.Sound(SOUND_FILES["dramatic_music"])
except pygame.error as e:
    print(f"Error loading music: {e}")
    fun_music = None
    dramatic_music = None

# Load nhạc nền cho menu
try:
    menu_music = pygame.mixer.Sound(SOUND_FILES["menu_music"])
except pygame.error as e:
    print(f"Error loading menu music: {e}")
    menu_music = None

# Ánh xạ tên thuật toán sang hàm thực tế
AI_ALGORITHM_FUNCTIONS = {
    "Breadth-First Search": bfs,
    "A* Search": a_star,
    "Beam Search": beam_search,
    "partial_observe" : partial_observe,
    "Q Learning": q_learning
}

# Khởi tạo menu chính và menu tạm dừng
menu = Menu(AI_ALGORITHMS, MAPS, background_image="assets/images/menu_background.png")
option_menu = OptionMenu(sound_enabled=True)

# Trạng thái trò chơi
state = "menu"
menu_state = "main"
selected_params = None
current_run = 0
sound_enabled = True
is_thief_detected = False
current_music = None
menu_music_playing = False
last_detected_state = False

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
master_idle_sprites = None
coin_sprites = None
trap_sprites = None
THIEF_SIZE = None
MASTER_SIZE = None
TRAP_SIZE = None
is_master_resting = False
rest_timer = 0

# Biến thống kê
success_count = 0
failure_count = 0
total_path_length = 0
total_completion_time = 0
total_expanded_nodes = 0
total_execution_time = 0
run_stats = []

#partial_value
map_thief = [[None] * 48 for _ in range(32)]
visited = []
queue_visit = []

def generate_patrol_waypoints(master_pos, rows, cols, map_grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, traps, num_waypoints=12):
    waypoints = []
    trap_positions = {tuple(trap["pos"]) for trap in traps} if traps else set()
    attempts = 0
    max_attempts = 100
    while len(waypoints) < num_waypoints and attempts < max_attempts:
        x = random.randint(1, rows - 2)
        y = random.randint(1, cols - 2)
        pos = [x, y]
        if (map_grid[x][y] == 0 and 
            not check_furniture_collision(pos, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y) and 
            tuple(pos) not in trap_positions and 
            pos not in waypoints):
            waypoints.append(pos)
        attempts += 1
    if len(waypoints) < num_waypoints:
        print(f"Warning: Only generated {len(waypoints)} waypoints after {max_attempts} attempts")
    return waypoints

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

def play_background_music():
    global current_music, is_thief_detected, sound_enabled
    if not sound_enabled or state != "game":
        if current_music:
            current_music.stop()
            current_music = None
        return

    if current_music:
        current_music.stop()
        current_music = None

    if is_thief_detected and dramatic_music:
        current_music = dramatic_music
        current_music.play(loops=-1)
        print("Playing dramatic music")
    elif not is_thief_detected and fun_music:
        current_music = fun_music
        current_music.play(loops=-1)
        print("Playing fun music")
    else:
        current_music = None
        print("No music played: music files not loaded or invalid state")

def play_menu_music():
    global menu_music_playing, sound_enabled
    if menu_music and sound_enabled and state == "menu" and menu_state == "main":
        if not menu_music_playing:
            menu_music.play(loops=-1)
            menu_music_playing = True

def stop_menu_music():
    global menu_music_playing
    if menu_music and menu_music_playing:
        menu_music.stop()
        menu_music_playing = False

def reset_game_state():
    global thief_pos, master_pos, items, traps, exit_pos, item_coins, collected_items, path, master_waypoints, master_path, game_over, thief_direction, master_direction, thief_frame, master_frame, coin_frame, trap_frame, frame_counter, master_patrol_counter, is_thief_detected, last_detected_state, is_master_resting, rest_timer, master_stamina, blood, run_start_time, path_length, map_thief, visited, queue_visit
    thief_pos, master_pos, items, traps, exit_pos = load_positions(tmx_data)
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
    item_coins = [(pos, coin_types[i % len(coin_types)], False) for i, pos in enumerate(items)]
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
    is_thief_detected = False
    last_detected_state = False
    is_master_resting = False
    rest_timer = 0
    master_stamina = MASTER_MAX_STAMINA
    blood = MAX_BLOOD  # Reset blood to MAX_BLOOD
    run_start_time = time.time()
    path_length = 0
    map_thief = [[None] * 48 for _ in range(32)]
    visited = []
    queue_visit = []

# Vòng lặp chính
clock = pygame.time.Clock()
play_menu_music()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if state == "game":
                state = "paused"
                option_menu.was_opened_by_quit = True
                option_menu.sound_enabled = sound_enabled
                option_menu.update_sound_button()
                if current_music:
                    current_music.stop()
            elif state == "menu":
                if menu_state == "options":
                    menu_state = "main"
                    play_menu_music()
                else:
                    stop_menu_music()
                    pygame.quit()
                    sys.exit()

        if state == "menu":
            if menu_state == "main":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    menu_state = "options"
                    option_menu.was_opened_by_quit = False
                    option_menu.sound_enabled = sound_enabled
                    option_menu.update_sound_button()
                    stop_menu_music()
                else:
                    result = menu.handle_event(event, screen, sound_enabled)
                    if result:
                        stop_menu_music()
                        selected_params = result
                        state = "game"
                        menu_state = "main"
                        current_run = 0
                        blood = 100
                        master_stamina = MASTER_MAX_STAMINA
                        success_count = 0
                        failure_count = 0
                        total_path_length = 0
                        total_completion_time = 0
                        total_expanded_nodes = 0
                        total_execution_time = 0
                        run_stats = []
                        map_file = MAPS[selected_params["map"]]
                        map_data = load_map(map_file)
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
                        thief_sprites, THIEF_SIZE = load_thief_sprites(SCALED_GRID_SIZE)
                        master_sprites, MASTER_SIZE = load_master_sprites(SCALED_GRID_SIZE)
                        master_idle_sprites = load_master_idle_sprites(SCALED_GRID_SIZE)
                        coin_sprites = load_coin_sprites(SCALED_GRID_SIZE)
                        trap_sprites, TRAP_SIZE = load_trap_sprites(SCALED_GRID_SIZE)
                        thief_pos, master_pos, items, traps, exit_pos = load_positions(tmx_data)
                        coin_types = ["red", "silver", "gold"]
                        item_coins = [(pos, coin_types[i % len(coin_types)], False) for i, pos in enumerate(items)]
                        exit_img = pygame.Surface((SCALED_GRID_SIZE, SCALED_GRID_SIZE))
                        exit_img.fill(WHITE)
                        reset_game_state()
                        play_background_music()
            elif menu_state == "options":
                result = option_menu.handle_event(event, sound_enabled)
                if result == "home" or result == "repeat":
                    menu_state = "main"
                    play_menu_music()
                elif result == "toggle_sound":
                    sound_enabled = option_menu.sound_enabled
                    print(f"Sound {'enabled' if sound_enabled else 'disabled'}")
                    if state == "game":
                        play_background_music()
                    elif state == "menu" and menu_state == "main":
                        play_menu_music()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    menu_state = "main"
                    play_menu_music()

        elif state == "game":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = "paused"
                option_menu.was_opened_by_quit = False
                option_menu.sound_enabled = sound_enabled
                option_menu.update_sound_button()
                if current_music:
                    current_music.stop()

        elif state == "paused":
            result = option_menu.handle_event(event, sound_enabled)
            if result == "home":
                state = "menu"
                menu_state = "main"
                if current_music:
                    current_music.stop()
                play_menu_music()
            elif result == "toggle_sound":
                sound_enabled = option_menu.sound_enabled
                print(f"Sound {'enabled' if sound_enabled else 'disabled'}")
                if state == "game":
                    play_background_music()
            elif result == "repeat":
                state = "game"
                play_background_music()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = "game"
                option_menu.was_opened_by_quit = False
                play_background_music()

    if state == "menu":
        if menu_state == "main":
            menu.draw(screen)
        elif menu_state == "options":
            menu.draw(screen)
            option_menu.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    elif state == "game":
        if current_run < selected_params["num_runs"]:
            if game_over:
                current_run += 1
                if current_run < selected_params["num_runs"]:
                    reset_game_state()
                    play_background_music()
                else:
                    print("Saving stats to stats.csv in append mode...")
                    file_exists = os.path.exists("stats.csv") and os.path.getsize("stats.csv") > 0
                    print(f"File exists: {file_exists}, File size: {os.path.getsize('stats.csv') if os.path.exists('stats.csv') else 0}")
                    with open("stats.csv", mode="a", newline="") as file:
                        writer = csv.writer(file)
                        if not file_exists:
                            print("Writing CSV header...")
                            writer.writerow([
                                "Run", "Algorithm", "Map", "Success", "Path_Length", 
                                "Completion_Time", "Expanded_Nodes", "Collected_Coins", 
                                "Remaining_Blood"
                            ])
                        print(f"Appending {len(run_stats)} records to stats.csv...")
                        for stat in run_stats:
                            writer.writerow(stat)
                    state = "menu"
                    menu_state = "main"
                    if current_music:
                        current_music.stop()
                    play_menu_music()
            else:
                algorithm = AI_ALGORITHM_FUNCTIONS[selected_params["algorithm"]]
                if algorithm is None:
                    print(f"Thuật toán {selected_params['algorithm']} chưa được triển khai!")
                    run_stats.append([
                        current_run + 1, selected_params["algorithm"], selected_params["map"],
                        0, 0, 0, 0, collected_items, blood
                    ])
                    current_run += 1
                    if current_run < selected_params["num_runs"]:
                        reset_game_state()  # Reset khi thuật toán không tồn tại
                        play_background_music()
                    else:
                        state = "menu"
                        menu_state = "main"
                        if current_music:
                            current_music.stop()
                        play_menu_music()
                    continue

                # Kiểm tra giao nhau giữa vùng tầm nhìn
                thief_zone = create_thief_vision_zone(thief_pos, thief_direction, ROWS, COLS)
                master_zone = create_master_vision_zone(master_pos, ROWS, COLS)
                zones_intersect = check_vision_zone_intersection(thief_zone, master_zone)

                # Cập nhật trạng thái phát hiện
                if zones_intersect:
                    detection_timer += 1 / 10
                    if detection_timer >= 0.1:  # Tăng lên 1 giây
                        new_detected_state = True
                else:
                    detection_timer = 0
                    new_detected_state = False
                    
                if new_detected_state != last_detected_state:
                    is_thief_detected = new_detected_state
                    last_detected_state = new_detected_state
                    if not game_over and sound_enabled:
                        if is_thief_detected and alert_sound:
                            alert_sound.play()
                        play_background_music()
                    if is_thief_detected:
                        # Khi phát hiện trộm, hủy đường đi tuần tra và chuyển sang đuổi ngay
                        master_waypoints = []
                        master_path = None
                        master_patrol_counter = 0
                        is_master_resting = False
                        rest_timer = 0
                        print("Master detected thief, switching to chase mode immediately")
                    else:
                        # Giữ waypoint cuối hoặc tạo mới nếu rỗng
                        if master_waypoints and isinstance(master_waypoints[-1], list) and len(master_waypoints[-1]) == 2:
                            master_waypoints = [master_waypoints[-1]]
                        else:
                            master_waypoints = generate_patrol_waypoints(master_pos, ROWS, COLS, map_grid, MASTER_SIZE, furniture_rects, 
                                                                        SCALED_GRID_SIZE, OFFSET_X, OFFSET_Y, traps, num_waypoints=12)
                        master_path = None
                        master_patrol_counter = 0
                        is_master_resting = False
                        rest_timer = 0
                        print("Master switching to patrol mode, using last waypoint or generating new waypoints")

                # Quản lý thể lực của master
                if is_thief_detected and zones_intersect > 0:
                    master_stamina -= MASTER_STAMINA_DRAIN_RATE
                    if master_stamina <= 0:
                        is_thief_detected = False
                        last_detected_state = False
                        master_path = None
                        is_master_resting = False
                        rest_timer = 0
                        master_patrol_counter = 0
                        # Tạo hoặc sử dụng waypoints khi mệt
                        if not master_waypoints:
                            master_waypoints = generate_patrol_waypoints(master_pos, ROWS, COLS, map_grid, MASTER_SIZE, furniture_rects, 
                                                                        SCALED_GRID_SIZE, OFFSET_X, OFFSET_Y, traps, num_waypoints=12)
                        print("Master exhausted, switching to patrol mode with existing or new waypoints")
                else:
                    master_stamina = min(master_stamina + MASTER_STAMINA_RECOVER_RATE, MASTER_MAX_STAMINA)

                # Logic di chuyển của thief
                available_coins = [(pos, coin_type) for pos, coin_type, collected in item_coins if not collected]
                if is_thief_detected:
                    if selected_params["algorithm"] == "partial_observe":
                        map_thief,path,expanded_nodes, execution_time,queue_visit,visited = algorithm(thief_pos, exit_pos, map_grid, THIEF_SIZE, furniture_rects, 
                                                                    SCALED_GRID_SIZE, OFFSET_X, OFFSET_Y, ROWS, COLS,items,map_thief,queue_visit,visited, traps)
                    else:
                        # Trộm chạy về phía cửa thoát
                        path, expanded_nodes, execution_time = algorithm(thief_pos, exit_pos, map_grid, THIEF_SIZE, furniture_rects, 
                                                                        SCALED_GRID_SIZE, OFFSET_X, OFFSET_Y, ROWS, COLS, traps)
                else:
                    if selected_params["algorithm"] == "partial_observe":
                        print(len(items))
                        if len(items) > 0:
                            map_thief, path,expanded_nodes, execution_time,queue_visit,visited = algorithm(thief_pos, exit_pos, map_grid, THIEF_SIZE, furniture_rects, 
                                                                    SCALED_GRID_SIZE, OFFSET_X, OFFSET_Y, ROWS, COLS,items,map_thief,queue_visit,visited, traps)
                        else:
                            path, expanded_nodes, execution_time = a_star(thief_pos, exit_pos, map_grid, THIEF_SIZE, furniture_rects, 
                                                                            SCALED_GRID_SIZE, OFFSET_X, OFFSET_Y, ROWS, COLS, traps)
                    if selected_params["algorithm"] != "partial_observe":
                        # Trộm tìm coin gần nhất chưa được nhặt
                        if available_coins:
                            nearest_coin = min(available_coins, key=lambda x: calculate_distance(thief_pos, x[0]))
                            path, expanded_nodes, execution_time = algorithm(thief_pos, nearest_coin[0], map_grid, THIEF_SIZE, furniture_rects, 
                                                                            SCALED_GRID_SIZE, OFFSET_X, OFFSET_Y, ROWS, COLS, traps)
                        else:
                            # Nếu không còn coin, chạy về cửa thoát
                            path, expanded_nodes, execution_time = algorithm(thief_pos, exit_pos, map_grid, THIEF_SIZE, furniture_rects, 
                                                                            SCALED_GRID_SIZE, OFFSET_X, OFFSET_Y, ROWS, COLS, traps)

                # Logic di chuyển của master
                if is_thief_detected:
                    if master_path is None or len(master_path) <= 1:
                        master_path, _, _ = master_chase(master_pos, thief_pos, map_grid, MASTER_SIZE, furniture_rects, 
                                                        SCALED_GRID_SIZE, OFFSET_X, OFFSET_Y, ROWS, COLS, traps)
                    is_master_resting = False
                    rest_timer = 0
                    master_patrol_counter = 0
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
                    if is_master_resting:
                        rest_timer += 1 / 10
                        if rest_timer >= REST_DURATION:
                            is_master_resting = False
                            rest_timer = 0
                            master_path = None
                    else:
                        if master_path is None or len(master_path) <= 1:
                            # Kiểm tra định dạng master_waypoints
                            if master_waypoints and not all(isinstance(wp, list) and len(wp) == 2 and all(isinstance(coord, int) for coord in wp) for wp in master_waypoints):
                                print(f"Invalid waypoints detected: {master_waypoints}, regenerating waypoints")
                                master_waypoints = generate_patrol_waypoints(master_pos, ROWS, COLS, map_grid, MASTER_SIZE, furniture_rects, 
                                                                            SCALED_GRID_SIZE, OFFSET_X, OFFSET_Y, traps, num_waypoints=12)
                            master_path, _, _ = master_patrol(master_pos, master_waypoints, map_grid, ROWS, COLS, MASTER_SIZE, 
                                                            furniture_rects, SCALED_GRID_SIZE, OFFSET_X, OFFSET_Y, traps)
                            if master_path is None or len(master_path) <= 1:
                                if master_waypoints:
                                    print("Removing unreachable waypoint:", master_waypoints[0])
                                    master_waypoints.pop(0)
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
                                    if len(master_path) <= 1:
                                        is_master_resting = True
                                        rest_timer = 0
                                else:
                                    if master_waypoints:
                                        print("Removing unreachable waypoint:", master_waypoints[0])
                                        master_waypoints.pop(0)
                                        master_path = None
                            master_patrol_counter = 0

                total_expanded_nodes += expanded_nodes
                total_execution_time += execution_time

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
                        path_length += 1
                        path.pop(0)

                        if not is_thief_detected:
                            for i, (item_pos, coin_type, collected) in enumerate(item_coins):
                                if thief_pos == item_pos and not collected:
                                    item_coins[i] = (item_pos, coin_type, True)
                                    if selected_params["algorithm"] == "partial_observe":
                                        items.remove(item_pos)
                                    collected_items += 1
                                    if sound_enabled and gold_sound:
                                        if current_music:
                                            current_music.stop()
                                        gold_sound.play()
                                        play_background_music()
                                    print(f"Item collected! Total collected: {collected_items}")
                                    break

                        if thief_pos == exit_pos:
                            completion_time = time.time() - run_start_time
                            total_completion_time += completion_time
                            total_path_length += path_length
                            run_stats.append([
                                current_run + 1, selected_params["algorithm"], selected_params["map"],
                                1, path_length, completion_time, expanded_nodes, 
                                collected_items, blood
                            ])
                            if collected_items < len(items):
                                print(f"Run {current_run + 1}/{selected_params['num_runs']}: Ten trom da thoat nhung chua thu thap du item")
                                if sound_enabled and escaped_sound:
                                    if current_music:
                                        current_music.stop()
                                    escaped_sound.play()
                                transition_effect(screen, "Escaped!", (255, 165, 0))
                            else:
                                print(f"Run {current_run + 1}/{selected_params['num_runs']}: Ten trom da thoat voi du item")
                                if sound_enabled and success_sound:
                                    if current_music:
                                        current_music.stop()
                                    success_sound.play()
                                transition_effect(screen, "Success!", (0, 255, 0))
                            success_count += 1
                            game_over = True
                    else:
                        path = None
                # Kiểm tra va chạm với trap
                trap_type = check_trap_collision(thief_pos, THIEF_SIZE, traps, SCALED_GRID_SIZE, OFFSET_X, OFFSET_Y)
                if trap_type:
                    for trap in traps:
                        if trap["pos"] == thief_pos:
                            print(f"Run {current_run + 1}/{selected_params['num_runs']}: Ten trom bi bat boi {trap_type} trap")
                            blood -= 5
                            print("dap bay")
                            if sound_enabled:
                                if hurt_sound:
                                    hurt_sound.play()
                            print(f"Trap triggered at {thief_pos}, Blood remaining: {blood}")
                            break
                    if blood <= 0:
                        print(f"Run {current_run + 1}/{selected_params['num_runs']}: Thief has no blood left! Game Over!")
                        if sound_enabled and game_over_sound:
                            game_over_sound.play()
                        transition_effect(screen, "Game Over!", (255, 0, 0))
                        completion_time = time.time() - run_start_time
                        run_stats.append([
                            current_run + 1, selected_params["algorithm"], selected_params["map"],
                            0, path_length, completion_time, expanded_nodes, 
                            collected_items, blood
                        ])
                        game_over = True
                        current_run = selected_params["num_runs"]
                        state = "menu"
                        menu_state = "main"
                        if current_music:
                            current_music.stop()
                        play_menu_music()
                        continue

                if master_pos == thief_pos:
                    print(f"Run {current_run + 1}/{selected_params['num_runs']}: Ten trom bi bat")
                    failure_count += 1
                    completion_time = time.time() - run_start_time
                    total_completion_time += completion_time
                    total_path_length += path_length
                    run_stats.append([
                        current_run + 1, selected_params["algorithm"], selected_params["map"],
                        0, path_length, completion_time, expanded_nodes, 
                        collected_items, blood
                    ])
                    if sound_enabled:
                        if current_music:
                            current_music.stop()
                        if game_over_sound:
                            game_over_sound.play()
                    transition_effect(screen, "Game Over!", (255, 0, 0))
                    game_over = True

                frame_counter += 1
                if frame_counter >= FRAME_RATE:
                    thief_frame = (thief_frame + 1) % len(thief_sprites[thief_direction])
                    if not is_master_resting:
                        master_frame = (master_frame + 1) % len(master_sprites[master_direction])
                    coin_frame = (coin_frame + 1) % 5
                    trap_frame = (trap_frame + 1) % 14
                    frame_counter = 0

    if state in ["game", "paused"]:
        screen.fill(GRAY)
        draw_map(screen, tmx_data, map_data, map_file)
                # Tạo và vẽ lớp phủ đêm
        night_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        night_overlay.fill((0, 0, 0, NIGHT_OPACITY))  # Đen bán trong suốt
        # Xóa vùng nhìn của thief
        thief_center_x = thief_pos[1] * SCALED_GRID_SIZE + OFFSET_X + SCALED_GRID_SIZE / 2
        thief_center_y = thief_pos[0] * SCALED_GRID_SIZE + OFFSET_Y + SCALED_GRID_SIZE / 2
        pygame.draw.circle(night_overlay, (0, 0, 0, 0), (int(thief_center_x), int(thief_center_y)), THIEF_VISION_RANGE * SCALED_GRID_SIZE)
        # Xóa vùng nhìn của master
        master_center_x = master_pos[1] * SCALED_GRID_SIZE + OFFSET_X + SCALED_GRID_SIZE / 2
        master_center_y = master_pos[0] * SCALED_GRID_SIZE + OFFSET_Y + SCALED_GRID_SIZE / 2
        pygame.draw.circle(night_overlay, (0, 0, 0, 0), (int(master_center_x), int(master_center_y)), MASTER_VISION_RANGE * SCALED_GRID_SIZE)
        screen.blit(night_overlay, (0, 0))
        
        center_x = thief_pos[1] * SCALED_GRID_SIZE + OFFSET_X + SCALED_GRID_SIZE / 2
        center_y = thief_pos[0] * SCALED_GRID_SIZE + OFFSET_Y + SCALED_GRID_SIZE / 2
        radius = THIEF_VISION_RANGE * SCALED_GRID_SIZE
        pygame.draw.circle(screen, LIGHT_BLUE, (center_x, center_y), radius, 2)

        center_x = master_pos[1] * SCALED_GRID_SIZE + OFFSET_X + SCALED_GRID_SIZE / 2
        center_y = master_pos[0] * SCALED_GRID_SIZE + OFFSET_Y + SCALED_GRID_SIZE / 2
        radius = MASTER_VISION_RANGE * SCALED_GRID_SIZE
        pygame.draw.circle(screen, LIGHT_PURPLE, (center_x, center_y), radius, 2)

        for trap in traps:
            trap_img = trap_sprites[trap["type"]][trap_frame]
            draw_x = trap["pos"][1] * SCALED_GRID_SIZE + OFFSET_X
            draw_y = trap["pos"][0] * SCALED_GRID_SIZE + OFFSET_Y
            screen.blit(trap_img, (int(draw_x), int(draw_y)))

        # Vẽ thanh máu trên đầu trộm
        bar_width = THIEF_SIZE
        bar_height = 5
        bar_x = thief_pos[1] * SCALED_GRID_SIZE + OFFSET_X + (THIEF_SIZE - bar_width) / 2
        bar_y = thief_pos[0] * SCALED_GRID_SIZE + OFFSET_Y - bar_height - 5
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        filled_width = (blood / MAX_BLOOD) * bar_width
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, filled_width, bar_height))

        # Vẽ thanh thể lực trên đầu master
        draw_stamina_bar(screen, master_pos, MASTER_SIZE, master_stamina, MASTER_MAX_STAMINA, SCALED_GRID_SIZE, OFFSET_X, OFFSET_Y)

        thief_img = thief_sprites[thief_direction][thief_frame]
        screen.blit(thief_img, (thief_pos[1] * SCALED_GRID_SIZE + OFFSET_X, thief_pos[0] * SCALED_GRID_SIZE + OFFSET_Y))

        master_img = master_idle_sprites[master_direction][0] if is_master_resting else master_sprites[master_direction][master_frame]
        screen.blit(master_img, (master_pos[1] * SCALED_GRID_SIZE + OFFSET_X, master_pos[0] * SCALED_GRID_SIZE + OFFSET_Y))

        for item_pos, coin_type, collected in item_coins:
            if not collected:
                coin_img = coin_sprites[coin_type][coin_frame]
                screen.blit(coin_img, (item_pos[1] * SCALED_GRID_SIZE + OFFSET_X, item_pos[0] * SCALED_GRID_SIZE + OFFSET_Y))

        screen.blit(exit_img, (exit_pos[1] * SCALED_GRID_SIZE + OFFSET_X, exit_pos[0] * SCALED_GRID_SIZE + OFFSET_Y))

        if state == "paused":
            option_menu.draw(screen)

        pygame.display.flip()
        clock.tick(10)