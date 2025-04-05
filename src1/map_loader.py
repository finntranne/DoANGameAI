import pytmx
import pygame
from config import *

# Load bản đồ Tiled
tmx_data = pytmx.load_pygame("map/6.tmx")
GRID_SIZE = tmx_data.tilewidth
ROWS = tmx_data.height
COLS = tmx_data.width

# Tính toán kích thước bản đồ gốc
MAP_WIDTH = COLS * GRID_SIZE
MAP_HEIGHT = ROWS * GRID_SIZE

# Tính hệ số phóng to
scale_factor = min(SCREEN_WIDTH / MAP_WIDTH, SCREEN_HEIGHT / MAP_HEIGHT)
SCALED_GRID_SIZE = GRID_SIZE * scale_factor

# Căn giữa bản đồ
OFFSET_X = (SCREEN_WIDTH - MAP_WIDTH * scale_factor) // 2
OFFSET_Y = (SCREEN_HEIGHT - MAP_HEIGHT * scale_factor) // 2

# Tạo lưới từ lớp "Wall"
map_grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
wall_layer = tmx_data.get_layer_by_name("Wall")
for x in range(COLS):
    for y in range(ROWS):
        if wall_layer.data[y][x] != 0:
            map_grid[y][x] = 1

# Lưu danh sách hình chữ nhật của đồ nội thất
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

# Load vị trí từ lớp "Objects"
def load_positions():
    thief_pos = None
    master_pos = None
    items = []
    exit_pos = None
    for obj in tmx_data.objects:
        if obj.name == "thief":
            thief_pos = [int(obj.y // GRID_SIZE), int(obj.x // GRID_SIZE)]
        elif obj.name == "master":
            master_pos = [int(obj.y // GRID_SIZE), int(obj.x // GRID_SIZE)]
        elif obj.name == "item":
            items.append([int(obj.y // GRID_SIZE), int(obj.x // GRID_SIZE)])
        elif obj.name == "exit":
            exit_pos = [int(obj.y // GRID_SIZE), int(obj.x // GRID_SIZE)]
    return thief_pos, master_pos, items, exit_pos

# Vẽ bản đồ từ Tiled với phóng to
def draw_map(screen, tmx_data, tmx_file_path="map/6.tmx"):
    import xml.etree.ElementTree as ET
    tree = ET.parse(tmx_file_path)
    root = tree.getroot()
    gid_map = {}
    for objgroup in root.findall(".//objectgroup[@name='FurnitureObjects']/object"):
        obj_id = int(objgroup.get("id"))
        gid = int(objgroup.get("gid", 0))
        gid_map[obj_id] = gid

    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, image in layer.tiles():
                gid = layer.data[y][x]
                if gid == 0:
                    continue
                scaled_image = pygame.transform.scale(image, (int(SCALED_GRID_SIZE), int(SCALED_GRID_SIZE)))
                draw_x = x * SCALED_GRID_SIZE + OFFSET_X
                draw_y = y * SCALED_GRID_SIZE + OFFSET_Y
                screen.blit(scaled_image, (draw_x, draw_y))

    furniture_layer = tmx_data.get_layer_by_name("FurnitureObjects")
    for obj in furniture_layer:
        if not hasattr(obj, 'image') or not obj.image:
            continue

        gid = obj.gid if hasattr(obj, 'gid') else 0
        if gid == 0:
            continue

        obj_id = int(obj.id)
        raw_gid = gid_map.get(obj_id, gid)
        gid = int(raw_gid)

        FLIP_HORIZONTAL = 1 << 31
        FLIP_VERTICAL = 1 << 30
        FLIP_DIAGONAL = 1 << 29

        flip_x = bool(gid & FLIP_HORIZONTAL)
        flip_y = bool(gid & FLIP_VERTICAL)
        flip_diagonal = bool(gid & FLIP_DIAGONAL)
        real_gid = gid & ~(FLIP_HORIZONTAL | FLIP_VERTICAL | FLIP_DIAGONAL)

        image = obj.image.convert_alpha()

        tile_width = obj.width if hasattr(obj, 'width') else GRID_SIZE
        tile_height = obj.height if hasattr(obj, 'height') else GRID_SIZE

        scaled_width = tile_width * scale_factor
        scaled_height = tile_height * scale_factor

        tile_width_in_grids = tile_width / GRID_SIZE
        tile_height_in_grids = tile_height / GRID_SIZE

        offset_x = (SCALED_GRID_SIZE * tile_width_in_grids - scaled_width) / 2
        offset_y = (SCALED_GRID_SIZE * tile_height_in_grids - scaled_height) / 2

        scaled_image = pygame.transform.scale(image, (int(scaled_width), int(scaled_height)))

        if flip_x:
            scaled_image = pygame.transform.flip(scaled_image, True, False)
        if flip_y:
            scaled_image = pygame.transform.flip(scaled_image, False, True)

        rotation = getattr(obj, 'rotation', 0)
        if rotation != 0:
            scaled_image = pygame.transform.rotate(scaled_image, -rotation)

        draw_x = obj.x * scale_factor + OFFSET_X + offset_x
        draw_y = obj.y * scale_factor + OFFSET_Y + offset_y

        if rotation != 0:
            rotated_rect = scaled_image.get_rect(center=(draw_x + scaled_width / 2, draw_y + scaled_height / 2))
            draw_x = rotated_rect.x
            draw_y = rotated_rect.y

        screen.blit(scaled_image, (draw_x, draw_y))