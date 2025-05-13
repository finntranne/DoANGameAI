import pygame

# Khởi tạo Pygame
pygame.init()

# Cài đặt màn hình
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Thief's Escape with Vision Zones")

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)  # Dùng cho thanh máu
CYAN = (0, 255, 255)  # Dùng cho thanh thể lực
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
LIGHT_BLUE = (135, 206, 250)
LIGHT_PURPLE = (147, 112, 219)
YELLOW = (255, 255, 0)

# Font để hiển thị debug
font = pygame.font.SysFont(None, 30)

# Tầm nhìn
THIEF_VISION_RANGE = 3
MASTER_VISION_RANGE = 3

# Frame rate cho hoạt hình
FRAME_RATE = 1

# Thời gian nghỉ của master
REST_DURATION = 2  # Thời gian nghỉ 1 giây

# Cài đặt máu và thể lực
THIEF_MAX_HEALTH = 100
THIEF_TRAP_DAMAGE = 5
MASTER_MAX_STAMINA = 100
MASTER_STAMINA_DRAIN_RATE = 5  # Giảm 2 thể lực mỗi giây khi truy đuổi
MASTER_STAMINA_RECOVER_RATE = 2  # Hồi 5 thể lực mỗi giây khi tuần tra
LOW_STAMINA_THRESHOLD = 20
blood = 100
MAX_BLOOD = 100
master_stamina = MASTER_MAX_STAMINA  # Thể lực ban đầu của master


NIGHT_OPACITY = 100

# Đường dẫn file âm thanh
SOUND_FILES = {
    "success": "assets/sounds/Success.wav",
    "game_over": "assets/sounds/GameOver.wav",
    "gold": "assets/sounds/Gold.wav",
    "hurt": "assets/sounds/Hurt.mp3",
    "fun_music": "assets/sounds/Fun.mp3",
    "dramatic_music": "assets/sounds/Dramatic.mp3",
    "menu_music": "assets/sounds/Menu.mp3",
    "alert": "assets/sounds/Alert.wav",
    "escaped": "assets/sounds/Escaped.wav",
}

# Danh sách thuật toán AI
AI_ALGORITHMS = {
    "Breadth-First Search": "bfs",
    "A* Search": "a_star",
    "Beam Search": "beam_search",
    "Backtracking with AC-3": "backtracking_with_ac3"
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

TRAP_COSTS = {
    "spike": 100,  # Chi phí cho bẫy spike
    "fire": 200   # Chi phí cho bẫy fire
}