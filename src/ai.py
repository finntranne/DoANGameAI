import heapq
import random
import math
import time
from collections import deque
from config import *
from utils import check_furniture_collision, find_nearest_free_position

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

def dfs(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols):
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

    stack = [[start]]
    visited = {tuple(start)}

    while stack:
        path = stack.pop()
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
                stack.append(path + [next_pos])
                expanded_nodes += 1
    
    end_time = time.time()
    execution_time = end_time - start_time
    print("DFS: No path found!")
    return None, expanded_nodes, execution_time

def greedy_best_first_search(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols):
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

    pq = [(heuristic(start, goal), [start])]
    visited = {tuple(start)}

    while pq:
        _, path = heapq.heappop(pq)
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
                priority = heuristic(next_pos, goal)
                heapq.heappush(pq, (priority, path + [next_pos]))
                expanded_nodes += 1
    
    end_time = time.time()
    execution_time = end_time - start_time
    print("Greedy Best-First Search: No path found!")
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

def uniform_cost_search(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols):
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

    pq = [(0, [start])]
    visited = {tuple(start): 0}

    while pq:
        cost, path = heapq.heappop(pq)
        x, y = path[-1]

        if [x, y] == goal:
            end_time = time.time()
            execution_time = end_time - start_time
            return path, expanded_nodes, execution_time

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
                expanded_nodes += 1
    
    end_time = time.time()
    execution_time = end_time - start_time
    print("Uniform Cost Search: No path found!")
    return None, expanded_nodes, execution_time

def iddfs(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols):
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

    def dls(path, depth, visited):
        nonlocal expanded_nodes
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
                expanded_nodes += 1
                result = dls(path + [next_pos], depth - 1, visited)
                if result:
                    return result
                visited.remove(tuple(next_pos))
        return None

    depth = 1
    max_depth = rows * cols
    while depth <= max_depth:
        visited = {tuple(start)}
        result = dls([start], depth, visited)
        if result:
            end_time = time.time()
            execution_time = end_time - start_time
            return result, expanded_nodes, execution_time
        depth += 1
    
    end_time = time.time()
    execution_time = end_time - start_time
    print("IDDFS: No path found!")
    return None, expanded_nodes, execution_time

def ida_star(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols):
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

    def search(path, g, threshold, visited):
        nonlocal expanded_nodes
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
                expanded_nodes += 1
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
            end_time = time.time()
            execution_time = end_time - start_time
            return path, expanded_nodes, execution_time
        if new_threshold == float('inf'):
            end_time = time.time()
            execution_time = end_time - start_time
            print("IDA* Search: No path found!")
            return None, expanded_nodes, execution_time
        threshold = new_threshold

def simple_hill_climbing(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols):
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

    path = [start]
    current = start
    max_steps = rows * cols

    for _ in range(max_steps):
        if current == goal:
            end_time = time.time()
            execution_time = end_time - start_time
            return path, expanded_nodes, execution_time
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_x, next_y = current[0] + dx, current[1] + dy
            next_pos = [next_x, next_y]
            if (0 <= next_x < len(grid) and 0 <= next_y < len(grid[0]) and 
                grid[next_x][next_y] != 1 and 
                not check_furniture_collision(next_pos, character_size, furniture_rects, 
                                             scaled_grid_size, offset_x, offset_y)):
                neighbors.append(next_pos)
                expanded_nodes += 1
        if not neighbors:
            end_time = time.time()
            execution_time = end_time - start_time
            print("Simple Hill Climbing: No valid neighbors!")
            return None, expanded_nodes, execution_time
        best_neighbor = min(neighbors, key=lambda pos: heuristic(pos, goal))
        current = best_neighbor
        path.append(current)
    
    end_time = time.time()
    execution_time = end_time - start_time
    print("Simple Hill Climbing: No path found within max steps!")
    return None, expanded_nodes, execution_time

def steepest_hill_climbing(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols):
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

    path = [start]
    current = start
    max_steps = rows * cols

    for _ in range(max_steps):
        if current == goal:
            end_time = time.time()
            execution_time = end_time - start_time
            return path, expanded_nodes, execution_time
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_x, next_y = current[0] + dx, current[1] + dy
            next_pos = [next_x, next_y]
            if (0 <= next_x < len(grid) and 0 <= next_y < len(grid[0]) and 
                grid[next_x][next_y] != 1 and 
                not check_furniture_collision(next_pos, character_size, furniture_rects, 
                                             scaled_grid_size, offset_x, offset_y)):
                neighbors.append(next_pos)
                expanded_nodes += 1
        if not neighbors:
            end_time = time.time()
            execution_time = end_time - start_time
            print("Steepest Hill Climbing: No valid neighbors!")
            return None, expanded_nodes, execution_time
        best_neighbor = min(neighbors, key=lambda pos: heuristic(pos, goal))
        if heuristic(best_neighbor, goal) >= heuristic(current, goal):
            end_time = time.time()
            execution_time = end_time - start_time
            print("Steepest Hill Climbing: Stuck at local minimum!")
            return None, expanded_nodes, execution_time
        current = best_neighbor
        path.append(current)
    
    end_time = time.time()
    execution_time = end_time - start_time
    print("Steepest Hill Climbing: No path found within max steps!")
    return None, expanded_nodes, execution_time

def stochastic_hill_climbing(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols):
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

    path = [start]
    current = start
    max_steps = rows * cols

    for _ in range(max_steps):
        if current == goal:
            end_time = time.time()
            execution_time = end_time - start_time
            return path, expanded_nodes, execution_time
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_x, next_y = current[0] + dx, current[1] + dy
            next_pos = [next_x, next_y]
            if (0 <= next_x < len(grid) and 0 <= next_y < len(grid[0]) and 
                grid[next_x][next_y] != 1 and 
                not check_furniture_collision(next_pos, character_size, furniture_rects, 
                                             scaled_grid_size, offset_x, offset_y)):
                neighbors.append(next_pos)
                expanded_nodes += 1
        if not neighbors:
            end_time = time.time()
            execution_time = end_time - start_time
            print("Stochastic Hill Climbing: No valid neighbors!")
            return None, expanded_nodes, execution_time
        better_neighbors = [n for n in neighbors if heuristic(n, goal) <= heuristic(current, goal)]
        if better_neighbors:
            current = random.choice(better_neighbors)
        else:
            current = random.choice(neighbors)
        path.append(current)
    
    end_time = time.time()
    execution_time = end_time - start_time
    print("Stochastic Hill Climbing: No path found within max steps!")
    return None, expanded_nodes, execution_time

def simulated_annealing(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols):
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

    path = [start]
    current = start
    temperature = 1000.0
    cooling_rate = 0.995
    max_steps = rows * cols

    for _ in range(max_steps):
        if current == goal:
            end_time = time.time()
            execution_time = end_time - start_time
            return path, expanded_nodes, execution_time
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
                expanded_nodes += 1
        if not neighbors:
            end_time = time.time()
            execution_time = end_time - start_time
            print("Simulated Annealing: No valid neighbors!")
            return None, expanded_nodes, execution_time
        next_pos = random.choice(neighbors)
        delta = heuristic(next_pos, goal) - heuristic(current, goal)
        if delta <= 0 or random.random() < math.exp(-delta / temperature):
            current = next_pos
            path.append(current)
    
    end_time = time.time()
    execution_time = end_time - start_time
    print("Simulated Annealing: No path found within max steps!")
    return None, expanded_nodes, execution_time

def beam_search(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols, beam_width=3):
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

    beams = [[start]]
    visited = {tuple(start)}

    while beams:
        new_beams = []
        for path in beams:
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
                    new_beams.append(path + [next_pos])
                    expanded_nodes += 1
        new_beams.sort(key=lambda path: heuristic(path[-1], goal))
        beams = new_beams[:beam_width]
        if not beams:
            break
    
    end_time = time.time()
    execution_time = end_time - start_time
    print("Beam Search: No path found!")
    return None, expanded_nodes, execution_time

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