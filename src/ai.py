import heapq
import random
import math
import time
from collections import deque
from config import *
from utils import check_furniture_collision, find_nearest_free_position
from collections import defaultdict
import sys
sys.setrecursionlimit(5000)  # Tăng giới hạn đệ quy lên 5000

def create_thief_vision_zone(thief_pos, direction, rows, cols):
    row, col = thief_pos
    vision_range = THIEF_VISION_RANGE
    zone = set()

    # Tạo vùng tầm nhìn hình tròn cho thief
    for i in range(max(0, row - vision_range), min(rows, row + vision_range + 1)):
        for j in range(max(0, col - vision_range), min(cols, col + vision_range + 1)):
            distance = math.sqrt((i - row) ** 2 + (j - col) ** 2)
            if distance <= vision_range:
                zone.add((i, j))

    return zone

def create_master_vision_zone(master_pos, rows, cols):
    row, col = master_pos
    vision_range = MASTER_VISION_RANGE
    zone = set()

    # Tạo vùng tầm nhìn hình tròn cho master
    for i in range(max(0, row - vision_range), min(rows, row + vision_range + 1)):
        for j in range(max(0, col - vision_range), min(cols, col + vision_range + 1)):
            distance = math.sqrt((i - row) ** 2 + (j - col) ** 2)
            if distance <= vision_range:
                zone.add((i, j))

    return zone

def check_vision_zone_intersection(thief_zone, master_zone):
    # Kiểm tra xem có ô nào thuộc cả hai vùng tầm nhìn không
    return bool(thief_zone & master_zone)

def master_vision(master_pos, thief_pos, rows, cols):
    zone = create_master_vision_zone(master_pos, rows, cols)
    return (thief_pos[0], thief_pos[1]) in zone

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def bfs(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols):
    if start is None or goal is None:
        print("Error: Start or goal position is None!")
        return None, 0, 0

    adjusted_start = find_nearest_free_position(start, character_size, furniture_rects, grid, 
                                               scaled_grid_size, offset_x, offset_y, rows, cols)
    if adjusted_start != start:
        print(f"Adjusted start position from {start} to {adjusted_start}")
        start = adjusted_start

    start_time = time.time()
    expanded_nodes = 0

    queue = deque([[start]])
    visited = {tuple(start)}

    while queue:
        path = queue.popleft()
        x, y = path[-1]

        if [x, y] == goal:
            end_time = time.time()
            execution_time = end_time - start_time
            return path, expanded_nodes, execution_time

        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_x, next_y = x + dx, y + dy
            next_pos = [next_x, next_y]

            if (0 <= next_x < len(grid) and 0 <= next_y < len(grid[0]) and 
                grid[next_x][next_y] != 1 and 
                not check_furniture_collision(next_pos, character_size, furniture_rects, 
                                             scaled_grid_size, offset_x, offset_y) and 
                tuple(next_pos) not in visited):
                visited.add(tuple(next_pos))
                queue.append(path + [next_pos])
                expanded_nodes += 1
    
    end_time = time.time()
    execution_time = end_time - start_time
    print("BFS: No path found!")
    return None, expanded_nodes, execution_time

def a_star(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols):
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    if start is None or goal is None:
        print("Error: Start or goal position is None!")
        return None, 0, 0
    
    adjusted_start = find_nearest_free_position(start, character_size, furniture_rects, grid, 
                                               scaled_grid_size, offset_x, offset_y, rows, cols)
    if adjusted_start != start:
        print(f"Adjusted start position from {start} to {adjusted_start}")
        start = adjusted_start

    start_time = time.time()
    expanded_nodes = 0

    pq = [(0 + heuristic(start, goal), 0, [start])]
    visited = {tuple(start): 0}
    
    while pq:
        _, cost, path = heapq.heappop(pq)
        x, y = path[-1]
        
        if [x, y] == goal:
            end_time = time.time()
            execution_time = end_time - start_time
            return path, expanded_nodes, execution_time
        
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_x, new_y = x + dx, y + dy
            next_pos = [next_x, new_y]
            new_cost = cost + 1
            
            if (0 <= next_x < len(grid) and 0 <= new_y < len(grid[0]) and 
                grid[next_x][new_y] != 1 and 
                not check_furniture_collision(next_pos, character_size, furniture_rects, 
                                             scaled_grid_size, offset_x, offset_y) and 
                (tuple(next_pos) not in visited or new_cost < visited[tuple(next_pos)])):
                visited[tuple(next_pos)] = new_cost
                priority = new_cost + heuristic(next_pos, goal)
                heapq.heappush(pq, (priority, new_cost, path + [next_pos]))
                expanded_nodes += 1
    
    end_time = time.time()
    execution_time = end_time - start_time
    print("A* Search: No path found!")
    return None, expanded_nodes, execution_time

def beam_search(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols, beam_width=20):
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    if start is None or goal is None:
        print("Error: Start or goal position is None!")
        return None, 0, 0
    
    # Adjust start position if necessary
    adjusted_start = find_nearest_free_position(start, character_size, furniture_rects, grid, 
                                               scaled_grid_size, offset_x, offset_y, rows, cols)
    if adjusted_start != start:
        print(f"Adjusted start position from {start} to {adjusted_start}")
        start = adjusted_start

    start_time = time.time()
    expanded_nodes = 0

    # Initialize beam with the starting path
    beam = [(heuristic(start, goal), 0, [start])]  # (heuristic_score, cost, path)
    visited = {tuple(start): 0}  # Track visited positions with their cost

    while beam:
        # Select top beam_width paths
        next_beam = []
        for _ in range(min(len(beam), beam_width)):
            if not beam:
                break
            _, cost, path = heapq.heappop(beam)
            x, y = path[-1]

            # Check if goal is reached
            if [x, y] == goal:
                end_time = time.time()
                execution_time = end_time - start_time
                return path, expanded_nodes, execution_time

            # Explore neighbors
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                next_x, next_y = x + dx, y + dy
                next_pos = [next_x, next_y]
                new_cost = cost + 1

                # Check if move is valid
                if (0 <= next_x < len(grid) and 0 <= next_y < len(grid[0]) and 
                    grid[next_x][next_y] != 1 and 
                    not check_furniture_collision(next_pos, character_size, furniture_rects, 
                                                 scaled_grid_size, offset_x, offset_y) and 
                    (tuple(next_pos) not in visited or new_cost < visited[tuple(next_pos)])):
                    visited[tuple(next_pos)] = new_cost
                    new_path = path + [next_pos]
                    score = new_cost + heuristic(next_pos, goal)  # f(n) = g(n) + h(n)
                    heapq.heappush(next_beam, (score, new_cost, new_path))
                    expanded_nodes += 1

        # Update beam with the best paths
        beam = next_beam

    end_time = time.time()
    execution_time = end_time - start_time
    print("Beam Search: No path found!")
    return None, expanded_nodes, execution_time



def ac3(thief_pos, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols, master_pos):
    # Khởi tạo miền giá trị cho mỗi ô
    domains = defaultdict(list)
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] != 1 and not check_furniture_collision([i, j], character_size, furniture_rects, scaled_grid_size, offset_x, offset_y):
                domains[(i, j)] = [(i + di, j + dj) for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                                   if 0 <= i + di < rows and 0 <= j + dj < cols and grid[i + di][j + dj] != 1]

    # Loại bỏ các ô nằm trong tầm nhìn của master
    master_zone = create_master_vision_zone(master_pos, rows, cols)
    for pos in list(domains.keys()):
        if pos in master_zone:
            del domains[pos]
        else:
            domains[pos] = [next_pos for next_pos in domains[pos] if next_pos not in master_zone]

    # Tạo hàng đợi các ràng buộc
    queue = []
    for pos in domains:
        for neighbor in domains[pos]:
            queue.append((pos, neighbor))

    # Áp dụng AC-3
    while queue:
        (xi, xj) = queue.pop(0)
        removed = False
        for val in domains[xi][:]:
            if not any(check_constraints(val, neighbor, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, master_pos)
                       for neighbor in domains[xj]):
                domains[xi].remove(val)
                removed = True
        if removed:
            for xk in [p for p in domains if p != xj and xj in domains[p]]:
                queue.append((xk, xj))

    return domains

def check_constraints(pos, next_pos, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, master_pos):
    # Chuyển next_pos thành list nếu nó là tuple
    next_pos = list(next_pos) if isinstance(next_pos, tuple) else next_pos
    x, y = next_pos
    if not (0 <= x < len(grid) and 0 <= y < len(grid[0])):
        return False
    if grid[x][y] == 1:
        return False
    if check_furniture_collision(next_pos, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y):
        return False
    if master_vision(master_pos, next_pos, len(grid), len(grid[0])):
        return False
    return True

def backtracking_with_ac3(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols, master_pos):
    start_time = time.time()
    expanded_nodes = 0

    domains = ac3(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols, master_pos)

    def heuristic(pos):
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    visited = set()
    max_depth = rows * cols

    def backtrack(current_pos, path, depth=0):
        nonlocal expanded_nodes
        if depth > max_depth:
            return None
        if current_pos == tuple(goal):
            return path

        x, y = current_pos
        visited.add(current_pos)
        # Sắp xếp các ô tiếp theo theo heuristic
        next_positions = sorted(domains.get(current_pos, []), key=heuristic)
        for next_pos in next_positions:
            if next_pos not in visited and check_constraints(current_pos, next_pos, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, master_pos):
                expanded_nodes += 1
                result = backtrack(next_pos, path + [list(next_pos)], depth + 1)
                if result:
                    return result
        visited.remove(current_pos)
        return None

    path = backtrack(tuple(start), [start])
    end_time = time.time()
    execution_time = end_time - start_time

    if path is None:
        print("Backtracking with AC-3: No path found!")
        return None, expanded_nodes, execution_time

    return path, expanded_nodes, execution_time

def master_patrol(master_pos, waypoints, map_grid, rows, cols, character_size, furniture_rects, 
                  scaled_grid_size, offset_x, offset_y):
    if not waypoints:
        attempts = 0
        max_attempts = 10
        while attempts < max_attempts:
            new_waypoint = [random.randint(1, rows-2), random.randint(1, cols-2)]
            if (map_grid[new_waypoint[0]][new_waypoint[1]] == 0 and 
                not check_furniture_collision(new_waypoint, character_size, furniture_rects, 
                                             scaled_grid_size, offset_x, offset_y)):
                path, _, _ = a_star(master_pos, new_waypoint, map_grid, character_size, furniture_rects, 
                                    scaled_grid_size, offset_x, offset_y, rows, cols)
                if path:
                    waypoints.append(new_waypoint)
                    break
            attempts += 1
        if attempts >= max_attempts:
            print("Warning: Could not find a reachable waypoint!")
            return None
    return a_star(master_pos, waypoints[0], map_grid, character_size, furniture_rects, 
                  scaled_grid_size, offset_x, offset_y, rows, cols)

def master_chase(master_pos, thief_pos, map_grid, character_size, furniture_rects, 
                 scaled_grid_size, offset_x, offset_y, rows, cols):
    return a_star(master_pos, thief_pos, map_grid, character_size, furniture_rects, 
                  scaled_grid_size, offset_x, offset_y, rows, cols)