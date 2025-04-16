# File: run_menu.py
import pygame
import sys
from menu import Menu

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 780
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Thief's Escape - Menu Test")

AI_ALGORITHMS = {
    "A*": None,
    "Greedy Best-First": None,
    "Random Walk": None
}

MAPS = {
    "Map 1": "map1.tmx",
    "Map 2": "map2.tmx",
    "Map 3": "map3.tmx",
    "Map 4": "map4.tmx",
    "Map 5": "map5.tmx",
    "Map 6": "map6.tmx",
    "Map 7": "map7.tmx",
    "Map 8": "map8.tmx",
    "Map 9": "map9.tmx"
}

menu = Menu(AI_ALGORITHMS, MAPS, background_image="assets/images/menu_background.png")

clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Truyền tham số screen vào handle_event
        result = menu.handle_event(event, screen)
        if result == "play":
            print("Play button pressed!")
            print(f"Selected AI: {menu.selected_ai}")
            print(f"Selected Map: {menu.selected_map}")
            print(f"Number of runs: {menu.num_runs}")

    menu.draw(screen)
    pygame.display.flip()
    clock.tick(60)