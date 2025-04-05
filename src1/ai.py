import heapq
import random
from config import *
from utils import check_furniture_collision, find_nearest_free_position
from map_loader import *
from characters import *

def create_thief_vision_zone(thief_pos, direction):
    row, col = thief_pos
    vision_range = THIEF_VISION_RANGE
    zone = set()
    for i in range(max(0, row - 1), min(ROWS, row + 2)):
        for j in range(max(0, col - 1), min(COLS, col + 2)):
            if abs(i - row) + abs(j - col) <= 1:
                zone.add((i, j))
    if direction == "up":
        for i in range(max(0, row - vision_range), row + 1):
            width = vision_range - abs(i - row)
            for j in range(max(0, col - width), min(COLS, col + width + 1)):
                zone.add((i, j))
    elif direction == "down":
        for i in range(row, min(ROWS, row + vision_range + 1)):
            width = vision_range - abs(i - row)
            for j in range(max(0, col - width), min(COLS, col + width + 1)):
                zone.add((i, j))
    elif direction == "left":
        for j in range(max(0, col - vision_range), col + 1):
            height = vision_range - abs(j - col)
            for i in range(max(0, row - height), min(ROWS, row + height + 1)):
                zone.add((i, j))
    elif direction == "right":
        for j in range(col, min(COLS, col + vision_range + 1)):
            height = vision_range - abs(j - col)
            for i in range(max(0, row - height), min(ROWS, row + height + 1)):
                zone.add((i, j))
    return zone

def create_master_vision_zone(master_pos):
    row, col = master_pos
    vision_range = MASTER_VISION_RANGE
    zone = set()
    for i in range(max(0, row - vision_range), min(ROWS, row + vision_range + 1)):
        for j in range(max(0, col - vision_range), min(COLS, col + vision_range + 1)):
            if abs(i - row) + abs(j - col) <= vision_range:
                zone.add((i, j))
    return zone

def master_vision(master_pos, thief_pos):
    zone = create_master_vision_zone(master_pos)
    return (thief_pos[0], thief_pos[1]) in zone

def a_star(start, goal, grid, character_size, furniture_rects):
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    if start is None or goal is None:
        print("Error: Start or goal position is None!")
        return None
    
    adjusted_start = find_nearest_free_position(start, character_size, furniture_rects, grid)
    if adjusted_start != start:
        print(f"Adjusted start position from {start} to {adjusted_start}")
        start = adjusted_start

    pq = [(0 + heuristic(start, goal), 0, [start])]
    visited = {tuple(start): 0}
    while pq:
        _, cost, path = heapq.heappop(pq)
        x, y = path[-1]
        if [x, y] == goal:
            return path
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_x, next_y = x + dx, y + dy
            next_pos = [next_x, next_y]
            new_cost = cost + 1
            if (0 <= next_x < len(grid) and 0 <= next_y < len(grid[0]) and 
                grid[next_x][next_y] != 1 and 
                not check_furniture_collision(next_pos, character_size, furniture_rects) and 
                (tuple(next_pos) not in visited or new_cost < visited[tuple(next_pos)])):
                visited[tuple(next_pos)] = new_cost
                priority = new_cost + heuristic(next_pos, goal)
                heapq.heappush(pq, (priority, new_cost, path + [next_pos]))
    return None

def master_patrol(master_pos, waypoints):
    if not waypoints:
        while True:
            new_waypoint = [random.randint(1, ROWS-2), random.randint(1, COLS-2)]
            if map_grid[new_waypoint[0]][new_waypoint[1]] == 0 and not check_furniture_collision(new_waypoint, MASTER_SIZE, furniture_rects):
                waypoints.append(new_waypoint)
                break
    return a_star(master_pos, waypoints[0], map_grid, MASTER_SIZE, furniture_rects)

def master_chase(master_pos, thief_pos):
    return a_star(master_pos, thief_pos, map_grid, MASTER_SIZE, furniture_rects)