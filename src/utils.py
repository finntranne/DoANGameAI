import pygame
from config import *

def get_character_hitbox(pos, size, scaled_grid_size, offset_x, offset_y):
    draw_x = pos[1] * scaled_grid_size + offset_x
    draw_y = pos[0] * scaled_grid_size + offset_y
    return pygame.Rect(draw_x, draw_y, size, size)

def check_furniture_collision(pos, size, furniture_rects, scaled_grid_size, offset_x, offset_y):
    character_rect = get_character_hitbox(pos, size, scaled_grid_size, offset_x, offset_y)
    for furniture_rect in furniture_rects:
        if character_rect.colliderect(furniture_rect):
            return True
    return False

def find_nearest_free_position(start_pos, size, furniture_rects, grid, scaled_grid_size, offset_x, offset_y, rows, cols):
    if not check_furniture_collision(start_pos, size, furniture_rects, scaled_grid_size, offset_x, offset_y):
        return start_pos
    
    queue = [(start_pos[0], start_pos[1])]
    visited = {(start_pos[0], start_pos[1])}
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    
    while queue:
        row, col = queue.pop(0)
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            new_pos = [new_row, new_col]
            if (0 <= new_row < rows and 0 <= new_col < cols and 
                (new_row, new_col) not in visited and 
                grid[new_row][new_col] != 1 and 
                not check_furniture_collision(new_pos, size, furniture_rects, scaled_grid_size, offset_x, offset_y)):
                return new_pos
            if 0 <= new_row < rows and 0 <= new_col < cols and (new_row, new_col) not in visited:
                visited.add((new_row, new_col))
                queue.append((new_row, new_col))
    
    print("Cảnh báo: Không tìm thấy vị trí trống!")
    return [1, 1]

def draw_health_bar(screen, pos, size, health, max_health, scaled_grid_size, offset_x, offset_y):
    # Tính toán vị trí phía trên đầu nhân vật
    bar_width = size
    bar_height = 10
    bar_x = pos[1] * scaled_grid_size + offset_x
    bar_y = pos[0] * scaled_grid_size + offset_y - bar_height - 5  # Cách đầu 5 pixel
    # Vẽ nền (viền đen)
    pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height))
    # Vẽ máu (màu xanh lá)
    health_width = (health / max_health) * (bar_width - 2)
    if health_width > 0:
        pygame.draw.rect(screen, GREEN, (bar_x + 1, bar_y + 1, health_width, bar_height - 2))

def draw_stamina_bar(screen, pos, size, stamina, max_stamina, scaled_grid_size, offset_x, offset_y):
    # Tính toán vị trí phía trên đầu nhân vật
    bar_width = size
    bar_height = 10
    bar_x = pos[1] * scaled_grid_size + offset_x
    bar_y = pos[0] * scaled_grid_size + offset_y - bar_height - 5  # Cách đầu 5 pixel
    # Vẽ nền (viền đen)
    pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height))
    # Vẽ thể lực (màu xanh lam)
    stamina_width = (stamina / max_stamina) * (bar_width - 2)
    if stamina_width > 0:
        pygame.draw.rect(screen, CYAN, (bar_x + 1, bar_y + 1, stamina_width, bar_height - 2))