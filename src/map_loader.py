import pytmx
import pygame
from config import *


def load_map(map_file):
    # Load bản đồ Tiled
    tmx_data = pytmx.load_pygame(map_file)
    GRID_SIZE = tmx_data.tilewidth
    ROWS = tmx_data.height
    COLS = tmx_data.width

    # Tính toán kích thước bản đồ gốc
    MAP_WIDTH = COLS * GRID_SIZE
    MAP_HEIGHT = ROWS * GRID_SIZE

    # Tính hệ số phóng to
    scale_factor = min(SCREEN_WIDTH / MAP_WIDTH, SCREEN_HEIGHT / MAP_HEIGHT)
    SCALED_GRID_SIZE = int(GRID_SIZE * scale_factor)  # Round to integer to avoid fractional pixels

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

    # Return all necessary data
    return {
        "tmx_data": tmx_data,
        "GRID_SIZE": GRID_SIZE,
        "ROWS": ROWS,
        "COLS": COLS,
        "MAP_WIDTH": MAP_WIDTH,
        "MAP_HEIGHT": MAP_HEIGHT,
        "scale_factor": scale_factor,
        "SCALED_GRID_SIZE": SCALED_GRID_SIZE,
        "OFFSET_X": OFFSET_X,
        "OFFSET_Y": OFFSET_Y,
        "map_grid": map_grid,
        "furniture_rects": furniture_rects,
    }

def load_positions(tmx_data):
    thief_pos = None
    master_pos = None
    items = []
    traps = []
    exit_pos = None
    for obj in tmx_data.objects:
        # Thử truy xuất class theo nhiều cách
        trap_type = None
        # Cách 1: Truy xuất trực tiếp thuộc tính 'class'
        trap_type = getattr(obj, 'class', None)
        if trap_type is None:
            # Cách 2: Truy xuất thuộc tính 'type' (dùng trong Tiled phiên bản cũ)
            trap_type = getattr(obj, 'type', None)
        if trap_type is None:
            # Cách 3: Truy xuất từ properties (pytmx thường lưu thuộc tính tùy chỉnh ở đây)
            trap_type = getattr(obj, 'properties', {}).get('class', getattr(obj, 'properties', {}).get('trap_type', None))
        
        if obj.name == "thief":
            thief_pos = [int(obj.y // tmx_data.tilewidth), int(obj.x // tmx_data.tilewidth)]
        elif obj.name == "master":
            master_pos = [int(obj.y // tmx_data.tilewidth), int(obj.x // tmx_data.tilewidth)]
        elif obj.name == "item":
            items.append([int(obj.y // tmx_data.tilewidth), int(obj.x // tmx_data.tilewidth)])
        elif obj.name == "trap":
            if trap_type in ["spike", "fire"]:
                traps.append({
                    "pos": [int(obj.y // tmx_data.tilewidth), int(obj.x // tmx_data.tilewidth)],
                    "type": trap_type
                })
            else:
                print(f"Invalid trap type for object: {trap_type}")
        elif obj.name == "exit":
            exit_pos = [int(obj.y // tmx_data.tilewidth), int(obj.x // tmx_data.tilewidth)]
    return thief_pos, master_pos, items, traps, exit_pos

def check_trap_collision(pos, size, traps, scaled_grid_size, offset_x, offset_y):
    character_rect = pygame.Rect(
        pos[1] * scaled_grid_size + offset_x,
        pos[0] * scaled_grid_size + offset_y,
        size,
        size
    )
    for trap in traps:
        trap_rect = pygame.Rect(
            trap["pos"][1] * scaled_grid_size + offset_x,
            trap["pos"][0] * scaled_grid_size + offset_y,
            scaled_grid_size,
            scaled_grid_size
        )
        if character_rect.colliderect(trap_rect):
            return trap["type"]
    return None

def draw_map(screen, tmx_data, map_data, tmx_file_path):
    import xml.etree.ElementTree as ET
    tree = ET.parse(tmx_file_path)
    root = tree.getroot()
    gid_map = {}
    for objgroup in root.findall(".//objectgroup[@name='FurnitureObjects']/object"):
        obj_id = int(objgroup.get("id"))
        gid = int(objgroup.get("gid", 0))
        gid_map[obj_id] = gid

    # Draw a solid background layer to cover the entire map area
    background_surface = pygame.Surface((int(map_data["MAP_WIDTH"] * map_data["scale_factor"]), 
                                        int(map_data["MAP_HEIGHT"] * map_data["scale_factor"])))
    background_surface.fill(GRAY)
    screen.blit(background_surface, (map_data["OFFSET_X"], map_data["OFFSET_Y"]))

    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, image in layer.tiles():
                gid = layer.data[y][x]
                if gid == 0:
                    continue
                # Overscale tiles by 1 pixel to overlap and eliminate gaps
                tile_size = int(map_data["SCALED_GRID_SIZE"]) + 1
                scaled_image = pygame.transform.scale(image, (tile_size, tile_size))
                # Use integer positions to ensure tiles are adjacent
                draw_x = int(x * map_data["SCALED_GRID_SIZE"] + map_data["OFFSET_X"])
                draw_y = int(y * map_data["SCALED_GRID_SIZE"] + map_data["OFFSET_Y"])
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

        tile_width = obj.width if hasattr(obj, 'width') else map_data["GRID_SIZE"]
        tile_height = obj.height if hasattr(obj, 'height') else map_data["GRID_SIZE"]

        scaled_width = tile_width * map_data["scale_factor"]
        scaled_height = tile_height * map_data["scale_factor"]

        tile_width_in_grids = tile_width / map_data["GRID_SIZE"]
        tile_height_in_grids = tile_height / map_data["GRID_SIZE"]

        offset_x = (map_data["SCALED_GRID_SIZE"] * tile_width_in_grids - scaled_width) / 2
        offset_y = (map_data["SCALED_GRID_SIZE"] * tile_height_in_grids - scaled_height) / 2

        scaled_image = pygame.transform.scale(image, (int(scaled_width) + 1, int(scaled_height) + 1))

        if flip_x:
            scaled_image = pygame.transform.flip(scaled_image, True, False)
        if flip_y:
            scaled_image = pygame.transform.flip(scaled_image, False, True)

        rotation = getattr(obj, 'rotation', 0)
        if rotation != 0:
            scaled_image = pygame.transform.rotate(scaled_image, -rotation)

        draw_x = obj.x * map_data["scale_factor"] + map_data["OFFSET_X"] + offset_x
        draw_y = obj.y * map_data["scale_factor"] + map_data["OFFSET_Y"] + offset_y

        if rotation != 0:
            rotated_rect = scaled_image.get_rect(center=(draw_x + scaled_width / 2, draw_y + scaled_height / 2))
            draw_x = rotated_rect.x
            draw_y = rotated_rect.y

        screen.blit(scaled_image, (int(draw_x), int(draw_y)))