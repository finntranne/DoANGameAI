import pygame

# Khởi tạo Pygame
pygame.init()

# Cài đặt màn hình
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 780
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Thief's Escape with Vision Zones")

# Màu sắc
WHITE = (255, 255, 255)  # Sàn/lối ra
BLACK = (0, 0, 0)  # Tường
RED = (255, 0, 0)  # Nhân vật trộm (mặc định nếu lỗi)
GREEN = (0, 255, 0)  # Vật phẩm (mặc định nếu lỗi)
BLUE = (0, 0, 255)  # Ông chủ (mặc định nếu lỗi)
GRAY = (128, 128, 128)  # Màu nền
LIGHT_BLUE = (135, 206, 250)  # Viền tầm nhìn trộm
LIGHT_PURPLE = (147, 112, 219)  # Viền tầm nhìn ông chủ
YELLOW = (255, 255, 0)  # Viền đối tượng nội thất

# Font để hiển thị debug
font = pygame.font.SysFont(None, 30)

# Tầm nhìn
THIEF_VISION_RANGE = 4
MASTER_VISION_RANGE = 6

# Frame rate cho hoạt hình
FRAME_RATE = 1