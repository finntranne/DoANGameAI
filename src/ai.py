import heapq
import random
import math
import time
from collections import deque
from config import *
from utils import check_furniture_collision, find_nearest_free_position
from collections import defaultdict
from map_loader import check_trap_collision
import sys
import os
import pickle
import numpy as np
import hashlib
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

def bfs(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols, traps=None):
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

def a_star(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols, traps=None):
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
            next_x, next_y = x + dx, y + dy
            next_pos = [next_x, next_y]
            
            # Kiểm tra chi phí bẫy
            trap_type = check_trap_collision(next_pos, character_size, traps, scaled_grid_size, offset_x, offset_y)
            trap_cost = TRAP_COSTS.get(trap_type, 0) if trap_type else 0
            move_cost = 1 + trap_cost  # Chi phí cơ bản là 1, cộng thêm chi phí bẫy nếu có
            
            new_cost = cost + move_cost
            
            if (0 <= next_x < len(grid) and 0 <= next_y < len(grid[0]) and 
                grid[next_x][next_y] != 1 and 
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

def beam_search(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols, traps=None, beam_width= 400):
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

    def improved_heuristic(pos):
        manhattan_dist = abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
        trap_penalty = 0
        if traps:
            for trap in traps:
                trap_pos = trap["pos"]
                trap_type = trap["type"]
                dist_to_trap = abs(pos[0] - trap_pos[0]) + abs(pos[1] - trap_pos[1])
                if dist_to_trap == 0:  # Ô chứa bẫy
                    trap_penalty += TRAP_COSTS.get(trap_type, 0) * 1000  # Phạt cực lớn
                elif dist_to_trap < 5:  # Ô gần bẫy
                    penalty = TRAP_COSTS.get(trap_type, 0) * 100 / (dist_to_trap + 1)
                    trap_penalty += penalty
        return manhattan_dist + trap_penalty

    beam = [(improved_heuristic(start), 0, [start])]
    visited = {tuple(start): 0}

    while beam:
        next_beam = []
        for _ in range(min(len(beam), beam_width)):
            if not beam:
                break
            _, cost, path = heapq.heappop(beam)
            x, y = path[-1]

            if [x, y] == goal:
                end_time = time.time()
                execution_time = end_time - start_time
                print(f"Beam Search found path: {path}")
                return path, expanded_nodes, execution_time

            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                next_x, next_y = x + dx, y + dy
                next_pos = [next_x, next_y]
                
                trap_type = check_trap_collision(next_pos, character_size, traps, scaled_grid_size, offset_x, offset_y)
                trap_cost = TRAP_COSTS.get(trap_type, 0) if trap_type else 0
                move_cost = 1 + trap_cost * 1000  # Tăng chi phí bẫy

                if (0 <= next_x < len(grid) and 0 <= next_y < len(grid[0]) and 
                    grid[next_x][next_y] != 1 and 
                    not check_furniture_collision(next_pos, character_size, furniture_rects, 
                                                 scaled_grid_size, offset_x, offset_y) and 
                    not trap_type and  # Loại bỏ ô có bẫy
                    (tuple(next_pos) not in visited or (cost + move_cost) < visited[tuple(next_pos)])):
                    if trap_type:
                        print(f"Warning: Beam Search considered trap at {next_pos}, type={trap_type}, move_cost={move_cost}")
                    visited[tuple(next_pos)] = cost + move_cost
                    new_path = path + [next_pos]
                    score = cost + move_cost + improved_heuristic(next_pos)
                    heapq.heappush(next_beam, (score, cost + move_cost, new_path))
                    expanded_nodes += 1

        beam = next_beam

    end_time = time.time()
    execution_time = end_time - start_time
    print("Beam Search: No path found!")
    return None, expanded_nodes, execution_time


def master_patrol(master_pos, waypoints, map_grid, rows, cols, character_size, furniture_rects, 
                  scaled_grid_size, offset_x, offset_y, traps=None):
    if not waypoints:
        attempts = 0
        max_attempts = 10
        while attempts < max_attempts:
            new_waypoint = [random.randint(1, rows-2), random.randint(1, cols-2)]
            if (map_grid[new_waypoint[0]][new_waypoint[1]] == 0 and 
                not check_furniture_collision(new_waypoint, character_size, furniture_rects, 
                                             scaled_grid_size, offset_x, offset_y)):
                path, _, _ = a_star(master_pos, new_waypoint, map_grid, character_size, furniture_rects, 
                                    scaled_grid_size, offset_x, offset_y, rows, cols, traps)
                if path:
                    waypoints.append(new_waypoint)
                    break
            attempts += 1
        if attempts >= max_attempts:
            print("Warning: Could not find a reachable waypoint!")
            return None
    return a_star(master_pos, waypoints[0], map_grid, character_size, furniture_rects, 
                  scaled_grid_size, offset_x, offset_y, rows, cols, traps)

def master_chase(master_pos, thief_pos, map_grid, character_size, furniture_rects, 
                 scaled_grid_size, offset_x, offset_y, rows, cols, traps=None):
    return a_star(master_pos, thief_pos, map_grid, character_size, furniture_rects, 
                  scaled_grid_size, offset_x, offset_y, rows, cols, traps)

def q_learning(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols, traps=None, episodes=100, alpha=0.5, gamma=0.9, epsilon=0.1, map_identifier="default", train_additional=True, additional_episodes=10):
    """
    Sử dụng Q-Learning để tìm đường đi cho nhân vật trộm, tối ưu hóa tránh bẫy.
    Đánh giá chất lượng Q-table để quyết định có huấn luyện bổ sung hay không.
    
    Args:
        train_additional: Có cho phép huấn luyện bổ sung khi Q-table đã tồn tại hay không
        additional_episodes: Số episode bổ sung nếu train_additional=True
    """
    if traps is None:
        traps = []
    if start is None or goal is None:
        print("Error: Start or goal position is None!")
        return None, 0, 0

    adjusted_start = find_nearest_free_position(start, character_size, furniture_rects, grid, 
                                               scaled_grid_size, offset_x, offset_y, rows, cols)
    if adjusted_start is None:
        print("Error: Cannot find a valid starting position!")
        return None, 0, 0
    if adjusted_start != start:
        print(f"Adjusted start position from {start} to {adjusted_start}")
        start = adjusted_start

    start_time = time.time()
    expanded_nodes = 0

    print("Step 1: Checking path feasibility with BFS")
    path, _, _ = bfs(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols)
    print(f"BFS result: {'Path found' if path else 'No path'}")
    if not path:
        print("Q-Learning: No feasible path exists!")
        return None, 0, time.time() - start_time

    # Đảm bảo map_identifier tạo file Q-table riêng, ví dụ map4 -> q_table_map4.pkl
    if map_identifier == "default":
        # Tạo định danh duy nhất dựa trên cấu hình bản đồ
        map_data = f"{rows}x{cols}_{str(grid)}_{str(furniture_rects)}_{str(traps)}"
        map_identifier = hashlib.md5(map_data.encode()).hexdigest()[:8]
        print(f"Generated unique map_identifier: {map_identifier}")
    else:
        print(f"Using provided map_identifier: {map_identifier}")

    q_table_file = os.path.join(os.path.dirname(__file__), f"q_table_{map_identifier}.pkl")
    print(f"Step 3: Checking for existing Q-table at {q_table_file}")
    q_table = {}
    train_new = False

    if os.path.exists(q_table_file):
        try:
            with open(q_table_file, 'rb') as f:
                q_table = pickle.load(f)
            print(f"Loaded pre-trained Q-table from: {os.path.abspath(q_table_file)}")
        except Exception as e:
            print(f"Error loading Q-table: {e}. Starting new training.")
            train_new = True
    else:
        train_new = True

    if train_new:
        print("Step 4: Initializing new Q-table")
        for i in range(rows):
            for j in range(cols):
                state = (i, j)
                q_table[state] = np.zeros(4)  # 4 actions: right, down, left, up
    else:
        print("Step 4: Using existing Q-table")

    actions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up

    print("Step 4.2: Precomputing collision and grid caches")
    collision_cache = {}
    grid_cache = {}
    trap_positions = [(trap['pos'][0], trap['pos'][1]) for trap in traps]
    near_trap_positions = set()
    for trap_x, trap_y in trap_positions:
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                near_x, near_y = trap_x + dx, trap_y + dy
                if 0 <= near_x < rows and 0 <= near_y < cols and (near_x, near_y) not in trap_positions:
                    near_trap_positions.add((near_x, near_y))
    for i in range(rows):
        for j in range(cols):
            pos = [i, j]
            pos_key = tuple(pos)
            grid_cache[pos_key] = (0 <= i < len(grid) and 0 <= j < len(grid[0]) and grid[i][j] != 1)
            if grid_cache[pos_key]:
                collision_cache[pos_key] = check_furniture_collision(pos, character_size, furniture_rects, 
                                                                    scaled_grid_size, offset_x, offset_y)

    def get_valid_actions(state):
        x, y = state
        if not (0 <= x < rows and 0 <= y < cols):
            print(f"State {state} is out of bounds! (rows={rows}, cols={cols})")
            return []
        valid = []
        for i, (dx, dy) in enumerate(actions):
            next_x, next_y = x + dx, y + dy
            next_pos = [next_x, next_y]
            pos_key = tuple(next_pos)
            if not grid_cache.get(pos_key, False):
                continue
            if collision_cache.get(pos_key, True):
                continue
            valid.append(i)
        return valid

    def is_near_trap(pos):
        return pos in near_trap_positions

    def evaluate_q_table():
        """Đánh giá chất lượng Q-table bằng cách thử tạo đường đi."""
        temp_path = [start]
        current = start
        visited = {tuple(start)}
        max_steps = 2 * (abs(start[0] - goal[0]) + abs(start[1] - goal[1]))
        
        for _ in range(max_steps):
            if current == goal:
                # Kiểm tra xem đường đi có va bẫy không
                if not any(tuple(p) in trap_positions for p in temp_path):
                    print("Q-table evaluation: Valid path found, no traps")
                    return True
                else:
                    print("Q-table evaluation: Path hits traps")
                    return False

            state = tuple(current)
            valid_actions = get_valid_actions(state)
            if not valid_actions:
                print("Q-table evaluation: No valid actions")
                return False

            q_values = [q_table[state][i] if i in valid_actions and tuple([current[0] + actions[i][0], current[1] + actions[i][1]]) not in visited else -float('inf') for i in range(len(actions))]
            action = np.argmax(q_values)

            dx, dy = actions[action]
            next_x, next_y = current[0] + dx, current[1] + dy
            if not (0 <= next_x < rows and 0 <= next_y < cols):
                print("Q-table evaluation: Out of bounds")
                return False

            next_pos = [next_x, next_y]
            if tuple(next_pos) in trap_positions:
                print("Q-table evaluation: Trap detected")
                return False
            if tuple(next_pos) in visited:
                print("Q-table evaluation: Cycle detected")
                return False

            visited.add(tuple(next_pos))
            temp_path.append(next_pos)
            current = next_pos

        print("Q-table evaluation: No path found within max steps")
        return False

    # Đánh giá chất lượng Q-table nếu đã tồn tại
    if not train_new and train_additional:
        print("Step 4.3: Evaluating Q-table quality")
        if evaluate_q_table():
            print("Q-table is valid, skipping additional training")
            train_additional = False
        else:
            print("Q-table needs improvement, proceeding with additional training")

    if train_new or train_additional:
        print("Step 5: Starting Q-table training")
        training_episodes = episodes * 2 if train_new else additional_episodes
        try:
            for episode in range(training_episodes):
                initial_epsilon = epsilon
                current = start
                step_count = 0
                visited = {tuple(start)}
                near_trap = False
                while current != goal:
                    step_count += 1
                    if step_count > 100:
                        print("Training stopped: Too many steps in episode")
                        break
                    state = tuple(current)
                    valid_actions = get_valid_actions(state)
                    if not valid_actions:
                        print("No valid actions during training")
                        break

                    near_trap = is_near_trap(state)
                    epsilon = initial_epsilon * 0.99 if not near_trap else initial_epsilon * 0.995

                    if random.random() < epsilon:
                        action = random.choice(valid_actions)
                    else:
                        q_values = [q_table[state][i] if i in valid_actions and tuple([current[0] + actions[i][0], current[1] + actions[i][1]]) not in visited else -float('inf') for i in range(len(actions))]
                        action = np.argmax(q_values)

                    dx, dy = actions[action]
                    next_x, next_y = current[0] + dx, current[1] + dy
                    next_state = (next_x, next_y)
                    if next_state in visited:
                        reward = -10000
                        q_table[state][action] += alpha * (reward + gamma * max(q_table[next_state]) - q_table[state][action])
                        print("Cycle detected during training")
                        break
                    visited.add(next_state)
                    expanded_nodes += 1

                    if [next_x, next_y] == goal:
                        reward = 50000
                    elif (next_x, next_y) in trap_positions:
                        reward = -40000
                    elif is_near_trap((next_x, next_y)):
                        reward = 150
                    elif grid_cache.get(tuple([next_x, next_y]), False) and not collision_cache.get(tuple([next_x, next_y]), True):
                        reward = -10
                    else:
                        reward = -10

                    future_q = max(q_table[next_state]) if get_valid_actions(next_state) else 0
                    q_table[state][action] += alpha * (reward + gamma * future_q - q_table[state][action])

                    current = [next_x, next_y]
                    if [next_x, next_y] == goal:
                        break
        except Exception as e:
            print(f"Error during Q-table training: {e}")
    else:
        print("Step 5: Skipping training, using existing Q-table")

    print(f"Step 6: Saving Q-table to {os.path.abspath(q_table_file)}")
    try:
        q_table_dir = os.path.dirname(q_table_file)
        if q_table_dir:
            os.makedirs(q_table_dir, exist_ok=True)
        with open(q_table_file, 'wb') as f:
            pickle.dump(q_table, f)
        print(f"Successfully saved Q-table to: {os.path.abspath(q_table_file)}")
    except Exception as e:
        print(f"Failed to save Q-table: {e}")

    print("Step 7: Extracting path")
    path = [start]
    current = start
    visited = {tuple(start)}
    max_steps = 2 * (abs(start[0] - goal[0]) + abs(start[1] - goal[1]))

    if start == goal:
        end_time = time.time()
        execution_time = end_time - start_time
        return [], expanded_nodes, execution_time

    for _ in range(max_steps):
        if current == goal:
            end_time = time.time()
            execution_time = end_time - start_time
            return path, expanded_nodes, execution_time

        state = tuple(current)
        valid_actions = get_valid_actions(state)
        if not valid_actions:
            print("Q-Learning: No valid actions available! Falling back to A*")
            path, _, _ = bfs(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols)
            if path:
                return path, expanded_nodes, time.time() - start_time
            else:
                print("Error: A* also failed to find a path. Check environment setup (grid, obstacles, traps).")
                return None, expanded_nodes, time.time() - start_time

        q_values = [q_table[state][i] if i in valid_actions and tuple([current[0] + actions[i][0], current[1] + actions[i][1]]) not in visited else -float('inf') for i in range(len(actions))]
        action = np.argmax(q_values)

        dx, dy = actions[action]
        next_x, next_y = current[0] + dx, current[1] + dy
        if not (0 <= next_x < rows and 0 <= next_y < cols):
            print(f"Next position {next_x, next_y} is out of bounds! Falling back to A*")
            path, _, _ = bfs(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols)
            if path:
                return path, expanded_nodes, time.time() - start_time
            else:
                print("Error: A* also failed to find a path. Check environment setup (grid, obstacles, traps).")
                return None, expanded_nodes, time.time() - start_time

        next_pos = [next_x, next_y]
        if tuple(next_pos) in trap_positions:
            print(f"Q-Learning: Trap detected at {next_pos}! Falling back to A*")
            path, _, _ = bfs(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols)
            if path:
                return path, expanded_nodes, time.time() - start_time
            else:
                print("Error: A* also failed to find a path. Check environment setup (grid, obstacles, traps).")
                return None, expanded_nodes, time.time() - start_time

        if tuple(next_pos) in visited:
            print("Q-Learning: Cycle detected! Falling back to A*")
            path, _, _ = bfs(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols)
            if path:
                return path, expanded_nodes, time.time() - start_time
            else:
                print("Error: A* also failed to find a path. Check environment setup (grid, obstacles, traps).")
                return None, expanded_nodes, time.time() - start_time

        visited.add(tuple(next_pos))
        path.append(next_pos)
        current = next_pos

    print("Q-Learning: No path found within max steps! Falling back to A*")
    path, _, _ = bfs(start, goal, grid, character_size, furniture_rects, scaled_grid_size, offset_x, offset_y, rows, cols)
    if path:
        return path, expanded_nodes, time.time() - start_time
    else:
        print("Error: A* also failed to find a path. Check environment setup (grid, obstacles, traps).")
    return None, expanded_nodes, time.time() - start_time

def partial_observe(thief_pos, exit_pos, map_grid, character_size, furniture_rects, 
                    scaled_grid_size, offset_x, offset_y, rows, cols,
                    items, map_thief, queue_visited, visited, traps=None):

    if thief_pos is None or exit_pos is None:
        print("Error: Start or goal position is None!")
        return None, 0, 0

    adjusted_start = find_nearest_free_position(thief_pos, character_size, furniture_rects, map_grid, 
                                                scaled_grid_size, offset_x, offset_y, rows, cols)
    if adjusted_start != thief_pos:
        print(f"Adjusted start position from {thief_pos} to {adjusted_start}")
        thief_pos = adjusted_start

    # Tạo một tập để kiểm tra tồn tại nhanh hơn
    queue_set = set([tuple(pos[1]) for pos in queue_visited])  # pos là (-priority, [x, y])

    for pos in create_thief_vision_zone(thief_pos, "", rows, cols):
        x, y = pos[0], pos[1]
        map_thief[x][y] = map_grid[x][y]
        if (map_grid[x][y] == 0 and 
            (x, y) not in queue_set and 
            [x, y] not in visited and 
            [x, y] != exit_pos):
            
            priority = x + y
            heapq.heappush(queue_visited, (-priority, [x, y]))
            queue_set.add((x, y))

    for pos_item in items:
        if map_thief[pos_item[0]][pos_item[1]] == 0:
            path, expanded_nodes, execution_time = a_star(
                thief_pos, pos_item, map_thief, character_size, furniture_rects, 
                scaled_grid_size, offset_x, offset_y, rows, cols, traps)
            return map_thief, path, expanded_nodes, execution_time, queue_visited, visited

    if queue_visited:
        _, current_pos = queue_visited[0]
        if thief_pos == current_pos:
            visited.append(current_pos)
            heapq.heappop(queue_visited)

    if queue_visited:
        _, target = queue_visited[0]
        path, expanded_nodes, execution_time = a_star(
            thief_pos, target, map_thief, character_size, furniture_rects, 
            scaled_grid_size, offset_x, offset_y, rows, cols, traps)

        if path is None:
            visited.append(target)
            heapq.heappop(queue_visited)

        return map_thief, path, expanded_nodes, execution_time, queue_visited, visited

    # Nếu không còn gì trong hàng đợi
    return map_thief, [], 0, 0, queue_visited, visited

