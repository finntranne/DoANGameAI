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
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
LIGHT_BLUE = (135, 206, 250)
LIGHT_PURPLE = (147, 112, 219)
YELLOW = (255, 255, 0)

# Font để hiển thị debug
font = pygame.font.SysFont(None, 30)

# Tầm nhìn
THIEF_VISION_RANGE = 2
MASTER_VISION_RANGE = 3

# Frame rate cho hoạt hình
FRAME_RATE = 1