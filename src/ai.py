import heapq
import random
import math
from collections import deque
from config import *
from utils import check_furniture_collision, find_nearest_free_position

def create_thief_vision_zone(thief_pos, direction, rows, cols):
    row, col = thief_pos
    vision_range = THIEF_VISION_RANGE
    zone = set()
    for i in range(max(0, row - 1), min(rows, row + 2)):
        for j in range(max(0, col - 1), min(cols, col + 2)):
            if abs(i - row) + abs(j - col) <= 1:
                zone.add((i, j))
    if direction == "up":
        for i in range(max(0, row - vision_range), row + 1):
            width = vision_range - abs(i - row)
            for j in range(max(0, col - width), min(cols, col + width + 1)):
                zone.add((i, j))
    elif direction == "down":
        for i in range(row, min(rows, row + vision_range + 1)):
            width = vision_range - abs(i - row)
            for j in range(max(0, col - width), min(cols, col + width + 1)):
                zone.add((i, j))
    elif direction == "left":
        for j in range(max(0, col - vision_range), col + 1):
            height = vision_range - abs(j - col)
            for i in range(max(0, row - height), min(rows, row + height + 1)):
                zone.add((i, j))
    elif direction == "right":
        for j in range(col, min(cols, col + vision_range + 1)):
            height = vision_range - abs(j - col)
            for i in range(max(0, row - height), min(rows, row + height + 1)):
                zone.add((i, j))
    return zone

def create_master_vision_zone(master_pos, rows, cols):
    row, col = master_pos
    vision_range = MASTER_VISION_RANGE
    zone = set()
    for i in range(max(0, row - vision_range), min(rows, row + vision_range + 1)):
        for j in range(max(0, col - vision_range), min(cols, col + vision_range + 1)):
            if abs(i - row) + abs(j - col) <= vision_range:
                zone.add((i, j))
    return zone

def master_vision(master_pos, thief_pos, rows, cols):
    zone = create_master_vision_zone(master_pos, rows, cols)
    return (thief_pos[0], thief_pos[1]) in zone

# Hàm heuristic chung cho các thuật toán
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# Breadth-First Search (BFS) - Đã có từ trước
def bfs(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols):
    if start is None or goal is None:
        print("Error: Start or goal position is None!")
        return None

    adjusted_start = find_nearest_free_position(start, character_size, furniture_rects, grid, 
                                               scaled_grid_size, offset_x, offset_y, rows, cols)
    if adjusted_start != start:
        print(f"Adjusted start position from {start} to {adjusted_start}")
        start = adjusted_start

    queue = deque([[start]])
    visited = {tuple(start)}

    while queue:
        path = queue.popleft()
        x, y = path[-1]

        if [x, y] == goal:
            return path

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
    
    print("BFS: No path found!")
    return None

# Depth-First Search (DFS) - Đã có từ trước
def dfs(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols):
    if start is None or goal is None:
        print("Error: Start or goal position is None!")
        return None

    adjusted_start = find_nearest_free_position(start, character_size, furniture_rects, grid, 
                                               scaled_grid_size, offset_x, offset_y, rows, cols)
    if adjusted_start != start:
        print(f"Adjusted start position from {start} to {adjusted_start}")
        start = adjusted_start

    stack = [[start]]
    visited = {tuple(start)}

    while stack:
        path = stack.pop()
        x, y = path[-1]

        if [x, y] == goal:
            return path

        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_x, next_y = x + dx, y + dy
            next_pos = [next_x, next_y]

            if (0 <= next_x < len(grid) and 0 <= next_y < len(grid[0]) and 
                grid[next_x][next_y] != 1 and 
                not check_furniture_collision(next_pos, character_size, furniture_rects, 
                                             scaled_grid_size, offset_x, offset_y) and 
                tuple(next_pos) not in visited):
                visited.add(tuple(next_pos))
                stack.append(path + [next_pos])
    
    print("DFS: No path found!")
    return None

# Greedy Best-First Search - Đã có từ trước
def greedy_best_first_search(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols):
    if start is None or goal is None:
        print("Error: Start or goal position is None!")
        return None

    adjusted_start = find_nearest_free_position(start, character_size, furniture_rects, grid, 
                                               scaled_grid_size, offset_x, offset_y, rows, cols)
    if adjusted_start != start:
        print(f"Adjusted start position from {start} to {adjusted_start}")
        start = adjusted_start

    pq = [(heuristic(start, goal), [start])]
    visited = {tuple(start)}

    while pq:
        _, path = heapq.heappop(pq)
        x, y = path[-1]

        if [x, y] == goal:
            return path

        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_x, next_y = x + dx, y + dy
            next_pos = [next_x, next_y]

            if (0 <= next_x < len(grid) and 0 <= next_y < len(grid[0]) and 
                grid[next_x][next_y] != 1 and 
                not check_furniture_collision(next_pos, character_size, furniture_rects, 
                                             scaled_grid_size, offset_x, offset_y) and 
                tuple(next_pos) not in visited):
                visited.add(tuple(next_pos))
                priority = heuristic(next_pos, goal)
                heapq.heappush(pq, (priority, path + [next_pos]))
    
    print("Greedy Best-First Search: No path found!")
    return None

# A* Search - Đã có từ trước
def a_star(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols):
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    if start is None or goal is None:
        print("Error: Start or goal position is None!")
        return None
    
    adjusted_start = find_nearest_free_position(start, character_size, furniture_rects, grid, 
                                               scaled_grid_size, offset_x, offset_y, rows, cols)
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
                not check_furniture_collision(next_pos, character_size, furniture_rects, 
                                             scaled_grid_size, offset_x, offset_y) and 
                (tuple(next_pos) not in visited or new_cost < visited[tuple(next_pos)])):
                visited[tuple(next_pos)] = new_cost
                priority = new_cost + heuristic(next_pos, goal)
                heapq.heappush(pq, (priority, new_cost, path + [next_pos]))
    print("A* Search: No path found!")
    return None

# Uniform Cost Search (UCS)
def uniform_cost_search(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols):
    if start is None or goal is None:
        print("Error: Start or goal position is None!")
        return None

    adjusted_start = find_nearest_free_position(start, character_size, furniture_rects, grid, 
                                               scaled_grid_size, offset_x, offset_y, rows, cols)
    if adjusted_start != start:
        print(f"Adjusted start position from {start} to {adjusted_start}")
        start = adjusted_start

    pq = [(0, [start])]
    visited = {tuple(start): 0}

    while pq:
        cost, path = heapq.heappop(pq)
        x, y = path[-1]

        if [x, y] == goal:
            return path

        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_x, next_y = x + dx, y + dy
            next_pos = [next_x, next_y]
            new_cost = cost + 1

            if (0 <= next_x < len(grid) and 0 <= next_y < len(grid[0]) and 
                grid[next_x][next_y] != 1 and 
                not check_furniture_collision(next_pos, character_size, furniture_rects, 
                                             scaled_grid_size, offset_x, offset_y) and 
                (tuple(next_pos) not in visited or new_cost < visited[tuple(next_pos)])):
                visited[tuple(next_pos)] = new_cost
                heapq.heappush(pq, (new_cost, path + [next_pos]))
    
    print("Uniform Cost Search: No path found!")
    return None

# Iterative Deepening DFS (IDDFS)
def iddfs(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols):
    if start is None or goal is None:
        print("Error: Start or goal position is None!")
        return None

    adjusted_start = find_nearest_free_position(start, character_size, furniture_rects, grid, 
                                               scaled_grid_size, offset_x, offset_y, rows, cols)
    if adjusted_start != start:
        print(f"Adjusted start position from {start} to {adjusted_start}")
        start = adjusted_start

    def dls(path, depth, visited):
        if depth < 0:
            return None
        x, y = path[-1]
        if [x, y] == goal:
            return path
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_x, next_y = x + dx, y + dy
            next_pos = [next_x, next_y]
            if (0 <= next_x < len(grid) and 0 <= next_y < len(grid[0]) and 
                grid[next_x][next_y] != 1 and 
                not check_furniture_collision(next_pos, character_size, furniture_rects, 
                                             scaled_grid_size, offset_x, offset_y) and 
                tuple(next_pos) not in visited):
                visited.add(tuple(next_pos))
                result = dls(path + [next_pos], depth - 1, visited)
                if result:
                    return result
                visited.remove(tuple(next_pos))
        return None

    depth = 1
    max_depth = rows * cols  # Giới hạn độ sâu tối đa để tránh vòng lặp vô hạn
    while depth <= max_depth:
        visited = {tuple(start)}
        result = dls([start], depth, visited)
        if result:
            return result
        depth += 1
    
    print("IDDFS: No path found!")
    return None

# IDA* Search (Iterative Deepening A*)
def ida_star(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols):
    if start is None or goal is None:
        print("Error: Start or goal position is None!")
        return None

    adjusted_start = find_nearest_free_position(start, character_size, furniture_rects, grid, 
                                               scaled_grid_size, offset_x, offset_y, rows, cols)
    if adjusted_start != start:
        print(f"Adjusted start position from {start} to {adjusted_start}")
        start = adjusted_start

    def search(path, g, threshold, visited):
        x, y = path[-1]
        f = g + heuristic([x, y], goal)
        if f > threshold:
            return f, None
        if [x, y] == goal:
            return f, path
        min_threshold = float('inf')
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_x, next_y = x + dx, y + dy
            next_pos = [next_x, next_y]
            if (0 <= next_x < len(grid) and 0 <= next_y < len(grid[0]) and 
                grid[next_x][next_y] != 1 and 
                not check_furniture_collision(next_pos, character_size, furniture_rects, 
                                             scaled_grid_size, offset_x, offset_y) and 
                tuple(next_pos) not in visited):
                visited.add(tuple(next_pos))
                new_threshold, result = search(path + [next_pos], g + 1, threshold, visited)
                visited.remove(tuple(next_pos))
                if result:
                    return new_threshold, result
                min_threshold = min(min_threshold, new_threshold)
        return min_threshold, None

    threshold = heuristic(start, goal)
    while True:
        visited = {tuple(start)}
        new_threshold, path = search([start], 0, threshold, visited)
        if path:
            return path
        if new_threshold == float('inf'):
            print("IDA* Search: No path found!")
            return None
        threshold = new_threshold

# Simple Hill Climbing
def simple_hill_climbing(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols):
    if start is None or goal is None:
        print("Error: Start or goal position is None!")
        return None

    adjusted_start = find_nearest_free_position(start, character_size, furniture_rects, grid, 
                                               scaled_grid_size, offset_x, offset_y, rows, cols)
    if adjusted_start != start:
        print(f"Adjusted start position from {start} to {adjusted_start}")
        start = adjusted_start

    path = [start]
    current = start
    max_steps = rows * cols  # Giới hạn số bước để tránh vòng lặp vô hạn

    for _ in range(max_steps):
        if current == goal:
            return path
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_x, next_y = current[0] + dx, current[1] + dy
            next_pos = [next_x, next_y]
            if (0 <= next_x < len(grid) and 0 <= next_y < len(grid[0]) and 
                grid[next_x][next_y] != 1 and 
                not check_furniture_collision(next_pos, character_size, furniture_rects, 
                                             scaled_grid_size, offset_x, offset_y)):
                neighbors.append(next_pos)
        if not neighbors:
            print("Simple Hill Climbing: No valid neighbors!")
            return None
        # Chọn neighbor tốt nhất (gần goal nhất)
        best_neighbor = min(neighbors, key=lambda pos: heuristic(pos, goal))
        current = best_neighbor
        path.append(current)
    
    print("Simple Hill Climbing: No path found within max steps!")
    return None

# Steepest Hill Climbing
def steepest_hill_climbing(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols):
    if start is None or goal is None:
        print("Error: Start or goal position is None!")
        return None

    adjusted_start = find_nearest_free_position(start, character_size, furniture_rects, grid, 
                                               scaled_grid_size, offset_x, offset_y, rows, cols)
    if adjusted_start != start:
        print(f"Adjusted start position from {start} to {adjusted_start}")
        start = adjusted_start

    path = [start]
    current = start
    max_steps = rows * cols

    for _ in range(max_steps):
        if current == goal:
            return path
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_x, next_y = current[0] + dx, current[1] + dy
            next_pos = [next_x, next_y]
            if (0 <= next_x < len(grid) and 0 <= next_y < len(grid[0]) and 
                grid[next_x][next_y] != 1 and 
                not check_furniture_collision(next_pos, character_size, furniture_rects, 
                                             scaled_grid_size, offset_x, offset_y)):
                neighbors.append(next_pos)
        if not neighbors:
            print("Steepest Hill Climbing: No valid neighbors!")
            return None
        # Chọn neighbor tốt nhất trong tất cả các neighbor
        best_neighbor = min(neighbors, key=lambda pos: heuristic(pos, goal))
        if heuristic(best_neighbor, goal) >= heuristic(current, goal):
            print("Steepest Hill Climbing: Stuck at local minimum!")
            return None
        current = best_neighbor
        path.append(current)
    
    print("Steepest Hill Climbing: No path found within max steps!")
    return None

# Stochastic Hill Climbing
def stochastic_hill_climbing(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols):
    if start is None or goal is None:
        print("Error: Start or goal position is None!")
        return None

    adjusted_start = find_nearest_free_position(start, character_size, furniture_rects, grid, 
                                               scaled_grid_size, offset_x, offset_y, rows, cols)
    if adjusted_start != start:
        print(f"Adjusted start position from {start} to {adjusted_start}")
        start = adjusted_start

    path = [start]
    current = start
    max_steps = rows * cols

    for _ in range(max_steps):
        if current == goal:
            return path
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_x, next_y = current[0] + dx, current[1] + dy
            next_pos = [next_x, next_y]
            if (0 <= next_x < len(grid) and 0 <= next_y < len(grid[0]) and 
                grid[next_x][next_y] != 1 and 
                not check_furniture_collision(next_pos, character_size, furniture_rects, 
                                             scaled_grid_size, offset_x, offset_y)):
                neighbors.append(next_pos)
        if not neighbors:
            print("Stochastic Hill Climbing: No valid neighbors!")
            return None
        # Chọn ngẫu nhiên một neighbor tốt hơn (hoặc bằng) current
        better_neighbors = [n for n in neighbors if heuristic(n, goal) <= heuristic(current, goal)]
        if better_neighbors:
            current = random.choice(better_neighbors)
        else:
            current = random.choice(neighbors)  # Chọn ngẫu nhiên để tránh kẹt
        path.append(current)
    
    print("Stochastic Hill Climbing: No path found within max steps!")
    return None

# Simulated Annealing
def simulated_annealing(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols):
    if start is None or goal is None:
        print("Error: Start or goal position is None!")
        return None

    adjusted_start = find_nearest_free_position(start, character_size, furniture_rects, grid, 
                                               scaled_grid_size, offset_x, offset_y, rows, cols)
    if adjusted_start != start:
        print(f"Adjusted start position from {start} to {adjusted_start}")
        start = adjusted_start

    path = [start]
    current = start
    temperature = 1000.0
    cooling_rate = 0.995
    max_steps = rows * cols

    for _ in range(max_steps):
        if current == goal:
            return path
        temperature *= cooling_rate
        if temperature < 0.1:
            break
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_x, next_y = current[0] + dx, current[1] + dy
            next_pos = [next_x, next_y]
            if (0 <= next_x < len(grid) and 0 <= next_y < len(grid[0]) and 
                grid[next_x][next_y] != 1 and 
                not check_furniture_collision(next_pos, character_size, furniture_rects, 
                                             scaled_grid_size, offset_x, offset_y)):
                neighbors.append(next_pos)
        if not neighbors:
            print("Simulated Annealing: No valid neighbors!")
            return None
        next_pos = random.choice(neighbors)
        delta = heuristic(next_pos, goal) - heuristic(current, goal)
        if delta <= 0 or random.random() < math.exp(-delta / temperature):
            current = next_pos
            path.append(current)
    
    print("Simulated Annealing: No path found within max steps!")
    return None

# Beam Search
def beam_search(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols, beam_width=3):
    if start is None or goal is None:
        print("Error: Start or goal position is None!")
        return None

    adjusted_start = find_nearest_free_position(start, character_size, furniture_rects, grid, 
                                               scaled_grid_size, offset_x, offset_y, rows, cols)
    if adjusted_start != start:
        print(f"Adjusted start position from {start} to {adjusted_start}")
        start = adjusted_start

    beams = [[start]]
    visited = {tuple(start)}

    while beams:
        new_beams = []
        for path in beams:
            x, y = path[-1]
            if [x, y] == goal:
                return path
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                next_x, next_y = x + dx, y + dy
                next_pos = [next_x, next_y]
                if (0 <= next_x < len(grid) and 0 <= next_y < len(grid[0]) and 
                    grid[next_x][next_y] != 1 and 
                    not check_furniture_collision(next_pos, character_size, furniture_rects, 
                                                 scaled_grid_size, offset_x, offset_y) and 
                    tuple(next_pos) not in visited):
                    visited.add(tuple(next_pos))
                    new_beams.append(path + [next_pos])
        # Sắp xếp các đường đi theo heuristic và giữ lại beam_width đường tốt nhất
        new_beams.sort(key=lambda path: heuristic(path[-1], goal))
        beams = new_beams[:beam_width]
        if not beams:
            break
    
    print("Beam Search: No path found!")
    return None

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
                path = a_star(master_pos, new_waypoint, map_grid, character_size, furniture_rects, 
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