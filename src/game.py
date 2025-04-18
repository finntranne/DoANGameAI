import pygame
import sys
import pytmx
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
    success_sound = pygame.mixer.Sound("assets/sounds/Success.wav")
    game_over_sound = pygame.mixer.Sound("assets/sounds/GameOver.wav")
    gold_sound = pygame.mixer.Sound("assets/sounds/Gold.wav")
    hurt_sound = pygame.mixer.Sound("assets/sounds/Hurt.mp3")
except pygame.error as e:
    print(f"Error loading sound: {e}")
    success_sound = None
    game_over_sound = None
    gold_sound = None
    hurt_sound = None

# Load nhạc nền cho game
try:
    fun_music = pygame.mixer.Sound("assets/sounds/Fun.mp3")
    dramatic_music = pygame.mixer.Sound("assets/sounds/Dramatic.mp3")
except pygame.error as e:
    print(f"Error loading music: {e}")
    fun_music = None
    dramatic_music = None

# Load nhạc nền cho menu
try:
    menu_music = pygame.mixer.Sound("assets/sounds/Menu.mp3")
except pygame.error as e:
    print(f"Error loading menu music: {e}")
    menu_music = None

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
current_music = None  # Nhạc nền trong game (Fun.mp3 hoặc Dramatic.mp3)
menu_music_playing = False  # Biến để theo dõi trạng thái phát Menu.mp3

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

def play_background_music():
    global current_music, is_thief_detected, sound_enabled
    if current_music:
        current_music.stop()
    
    if sound_enabled and state == "game":
        if is_thief_detected and dramatic_music:
            current_music = dramatic_music
        elif not is_thief_detected and fun_music:
            current_music = fun_music
        else:
            current_music = None
        
        if current_music:
            current_music.play(loops=-1)

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

# Vòng lặp chính
clock = pygame.time.Clock()
play_menu_music()  # Phát Menu.mp3 ngay khi bắt đầu (ở menu chính)
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
                    play_menu_music()  # Phát lại Menu.mp3 khi quay lại menu chính
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
                    stop_menu_music()  # Dừng Menu.mp3 khi mở menu Option
                else:
                    result = menu.handle_event(event, screen)
                    if result:
                        stop_menu_music()  # Dừng Menu.mp3 khi chuyển sang game
                        selected_params = result
                        state = "game"
                        menu_state = "main"
                        current_run = 0
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
                        coin_sprites = load_coin_sprites(SCALED_GRID_SIZE)
                        trap_sprites, TRAP_SIZE = load_trap_sprites(SCALED_GRID_SIZE)
                        thief_pos, master_pos, items, traps, exit_pos = load_positions(tmx_data)
                        print(f"Loaded traps: {traps}")
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
                        is_thief_detected = False
                        play_background_music()
            elif menu_state == "options":
                result = option_menu.handle_event(event)
                if result == "home" or result == "repeat":
                    menu_state = "main"
                    play_menu_music()  # Phát lại Menu.mp3 khi quay lại menu chính
                elif result == "toggle_sound":
                    sound_enabled = option_menu.sound_enabled
                    print(f"Sound {'enabled' if sound_enabled else 'disabled'}")
                    if state == "game":
                        play_background_music()
                    elif state == "menu" and menu_state == "main":
                        play_menu_music()  # Cập nhật trạng thái Menu.mp3 dựa trên sound_enabled
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    menu_state = "main"
                    play_menu_music()  # Phát lại Menu.mp3 khi quay lại menu chính

        elif state == "game":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = "paused"
                option_menu.was_opened_by_quit = False
                option_menu.sound_enabled = sound_enabled
                option_menu.update_sound_button()
                if current_music:
                    current_music.stop()

        elif state == "paused":
            result = option_menu.handle_event(event)
            if result == "home":
                state = "menu"
                menu_state = "main"
                if current_music:
                    current_music.stop()
                play_menu_music()  # Phát Menu.mp3 khi quay lại menu chính
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
                    thief_pos, master_pos, items, traps, exit_pos = load_positions(tmx_data)
                    print(f"Reloaded traps for run {current_run + 1}: {traps}")
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
                    is_thief_detected = False
                    play_background_music()
                else:
                    state = "menu"
                    menu_state = "main"
                    if current_music:
                        current_music.stop()
                    play_menu_music()  # Phát Menu.mp3 khi quay lại menu chính
            else:
                algorithm = AI_ALGORITHMS[selected_params["algorithm"]]
                if algorithm is None:
                    print(f"Thuật toán {selected_params['algorithm']} chưa được triển khai!")
                    state = "menu"
                    menu_state = "main"
                    if current_music:
                        current_music.stop()
                    play_menu_music()
                    continue

                if collected_items < len(items):
                    path = algorithm(thief_pos, items[collected_items], map_grid, THIEF_SIZE, furniture_rects, 
                                     SCALED_GRID_SIZE, OFFSET_X, OFFSET_Y, ROWS, COLS)
                else:
                    path = algorithm(thief_pos, exit_pos, map_grid, THIEF_SIZE, furniture_rects, 
                                     SCALED_GRID_SIZE, OFFSET_X, OFFSET_Y, ROWS, COLS)

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
                                if sound_enabled and gold_sound:
                                    if current_music:
                                        current_music.stop()
                                    gold_sound.play()
                                    play_background_music()
                                print(f"Item collected! Total collected: {collected_items}")
                                break

                        if thief_pos == exit_pos and collected_items == len(items):
                            print(f"Run {current_run + 1}/{selected_params['num_runs']}: Ten trom da thoat")
                            if sound_enabled and success_sound:
                                if current_music:
                                    current_music.stop()
                                success_sound.play()
                            transition_effect(screen, "Success!", (0, 255, 0))
                            game_over = True
                    else:
                        path = None

                trap_type = check_trap_collision(thief_pos, THIEF_SIZE, traps, SCALED_GRID_SIZE, OFFSET_X, OFFSET_Y)
                if trap_type:
                    print(f"Run {current_run + 1}/{selected_params['num_runs']}: Ten trom bi bat boi {trap_type} trap")
                    if sound_enabled:
                        if current_music:
                            current_music.stop()
                        if hurt_sound:
                            hurt_sound.play()
                        if game_over_sound:
                            game_over_sound.play()
                    transition_effect(screen, "Game Over!", (255, 0, 0))
                    game_over = True

                new_detected_state = master_vision(master_pos, thief_pos, ROWS, COLS)
                if new_detected_state != is_thief_detected:
                    is_thief_detected = new_detected_state
                    if not game_over:
                        play_background_music()

                if is_thief_detected:
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
                    master_frame = (master_frame + 1) % len(master_sprites[master_direction])
                    coin_frame = (coin_frame + 1) % 5
                    trap_frame = (trap_frame + 1) % 14
                    frame_counter = 0

    if state in ["game", "paused"]:
        screen.fill(GRAY)
        draw_map(screen, tmx_data, map_data, map_file)

        thief_vision_zone = create_thief_vision_zone(thief_pos, thief_direction, ROWS, COLS)
        for i, j in thief_vision_zone:
            pygame.draw.rect(screen, LIGHT_BLUE, (j * SCALED_GRID_SIZE + OFFSET_X, i * SCALED_GRID_SIZE + OFFSET_Y, SCALED_GRID_SIZE, SCALED_GRID_SIZE), width=2)

        master_vision_zone = create_master_vision_zone(master_pos, ROWS, COLS)
        for i, j in master_vision_zone:
            pygame.draw.rect(screen, LIGHT_PURPLE, (j * SCALED_GRID_SIZE + OFFSET_X, i * SCALED_GRID_SIZE + OFFSET_Y, SCALED_GRID_SIZE, SCALED_GRID_SIZE), width=2)

        for trap in traps:
            trap_img = trap_sprites[trap["type"]][trap_frame]
            draw_x = trap["pos"][1] * SCALED_GRID_SIZE + OFFSET_X
            draw_y = trap["pos"][0] * SCALED_GRID_SIZE + OFFSET_Y
            print(f"Drawing trap {trap['type']} at ({draw_x}, {draw_y})")
            screen.blit(trap_img, (int(draw_x), int(draw_y)))

        thief_img = thief_sprites[thief_direction][thief_frame]
        screen.blit(thief_img, (thief_pos[1] * SCALED_GRID_SIZE + OFFSET_X, thief_pos[0] * SCALED_GRID_SIZE + OFFSET_Y))

        master_img = master_sprites[master_direction][master_frame]
        screen.blit(master_img, (master_pos[1] * SCALED_GRID_SIZE + OFFSET_X, master_pos[0] * SCALED_GRID_SIZE + OFFSET_Y))

        for item_pos, coin_type in item_coins:
            coin_img = coin_sprites[coin_type][coin_frame]
            screen.blit(coin_img, (item_pos[1] * SCALED_GRID_SIZE + OFFSET_X, item_pos[0] * SCALED_GRID_SIZE + OFFSET_Y))

        screen.blit(exit_img, (exit_pos[1] * SCALED_GRID_SIZE + OFFSET_X, exit_pos[0] * SCALED_GRID_SIZE + OFFSET_Y))

        if state == "paused":
            option_menu.draw(screen)

        pygame.display.flip()
        clock.tick(10)