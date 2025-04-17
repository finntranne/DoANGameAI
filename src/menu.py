import pygame
import time
from config import *

# Khởi tạo pygame.mixer để xử lý âm thanh
pygame.mixer.init()

class TextBox:
    def __init__(self, x, y, width, height, default_value="1"):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font("assets/fonts/PressStart2P.ttf", 24)
        self.button_color = (70, 70, 70)
        self.border_color = (200, 200, 200)
        self.border_color_hovered = (255, 255, 0)
        self.border_color_active = (0, 255, 0)
        self.text_color = (255, 255, 255)
        self.shadow_color = (30, 30, 30)
        self.hovered = False
        self.active = False
        self.text = default_value

    def draw(self, screen):
        if self.active:
            border_color = self.border_color_active
        elif self.hovered:
            border_color = self.border_color_hovered
        else:
            border_color = self.border_color

        shadow_rect = self.rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        pygame.draw.rect(screen, self.shadow_color, shadow_rect, border_radius=5)

        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=5)
        inner_rect = self.rect.inflate(-4, -4)
        pygame.draw.rect(screen, self.button_color, inner_rect, border_radius=5)

        display_text = f"{self.text}" if not self.active else f"{self.text}_"
        text_surface = self.font.render(display_text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def check_click(self, mouse_pos):
        self.active = self.rect.collidepoint(mouse_pos)
        return None

    def handle_event(self, event):
        if not self.active:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
            elif event.unicode.isdigit():
                if self.text == "0":
                    self.text = event.unicode
                else:
                    self.text += event.unicode

class Button:
    def __init__(self, x, y, width, height, normal_image_path, pressed_image_path, action=None, sound_path=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.normal_image = pygame.image.load(normal_image_path)
        self.pressed_image = pygame.image.load(pressed_image_path)
        self.normal_image = pygame.transform.scale(self.normal_image, (width, height))
        self.pressed_image = pygame.transform.scale(self.pressed_image, (width, height))
        self.is_pressed = False
        self.hovered = False
        self.action = action
        self.sound = pygame.mixer.Sound(sound_path) if sound_path else None
        self.sound_enabled = True

    def draw(self, screen):
        scale = 1.1 if self.hovered else 1.0
        current_image = self.pressed_image if self.is_pressed else self.normal_image
        scaled_image = pygame.transform.scale(current_image, 
                                            (int(self.rect.width * scale), int(self.rect.height * scale)))
        scaled_rect = scaled_image.get_rect(center=self.rect.center)
        screen.blit(scaled_image, scaled_rect)

    def check_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def check_click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.check_click(event.pos):
                self.is_pressed = True
                if self.sound and self.sound_enabled:
                    self.sound.play()
                return self.action
        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_pressed = False
        return None

class Menu:
    def __init__(self, ai_algorithms, maps, background_image="assets/images/menu_background.png"):
        self.ai_algorithms = ai_algorithms
        self.maps = maps
        self.ai_list = list(ai_algorithms.keys())
        self.map_list = list(maps.keys())
        self.selected_ai_index = 0
        self.selected_map_index = 0
        self.selected_ai = self.ai_list[self.selected_ai_index]
        self.selected_map = self.map_list[self.selected_map_index]
        self.num_runs = 1
        self.elements = []
        self.buttons = []
        self.font = pygame.font.Font("assets/fonts/PressStart2P.ttf", 20)
        self.title_font = pygame.font.Font("assets/fonts/PressStart2P.ttf", 40)
        self.text_color = (255, 255, 255)
        self.transitioning = False
        self.setup_elements()
        try:
            self.background = pygame.image.load(background_image)
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except pygame.error as e:
            print(f"Error loading background image: {e}")
            self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.background.fill((0, 0, 0))
        self.load_map_previews()

    def load_map_previews(self):
        self.map_previews = {}
        preview_width = 300
        preview_height = 200
        for map_name in self.map_list:
            try:
                preview = pygame.image.load(f"assets/images/{map_name.lower().replace(' ', '_')}_preview.png")
                preview = pygame.transform.scale(preview, (preview_width, preview_height))
                self.map_previews[map_name] = preview
            except pygame.error as e:
                print(f"Error loading preview for {map_name}: {e}")
                preview = pygame.Surface((preview_width, preview_height))
                preview.fill((50, 50, 50))
                self.map_previews[map_name] = preview

    def setup_elements(self):
        element_width = 100
        element_height = 50
        start_x = (SCREEN_WIDTH - element_width) // 2 - 300
        start_y = 230

        runs_textbox = TextBox(
            start_x,
            start_y,
            element_width,
            element_height,
            "1"
        )
        self.elements.append(runs_textbox)

        button_play_width = 300
        button_play_height = 200
        button_play_x = SCREEN_WIDTH // 2 + 160
        button_play_y = SCREEN_HEIGHT - 280
        play_button = Button(
            button_play_x,
            button_play_y,
            button_play_width,
            button_play_height,
            "assets/images/PlayBtn.png",
            "assets/images/PlayClick.png",
            action="play",
            sound_path="assets/sounds/Menu2.wav"
        )
        self.buttons.append(play_button)

        button_arrow_left_width = 40
        button_arrow_left_height = 40
        button_arrow_left_x = SCREEN_WIDTH // 2 + 200
        button_arrow_left_y = 170
        arrow_left_button = Button(
            button_arrow_left_x,
            button_arrow_left_y,
            button_arrow_left_width,
            button_arrow_left_height,
            "assets/images/ArrowLeftBtn.png",
            "assets/images/ArrowLeftClick.png",
            action="change_map_left",
            sound_path="assets/sounds/Menu1.wav"
        )
        self.buttons.append(arrow_left_button)

        button_arrow_right_width = 40
        button_arrow_right_height = 40
        button_arrow_right_x = SCREEN_WIDTH // 2 + 360
        button_arrow_right_y = 170
        arrow_right_button = Button(
            button_arrow_right_x,
            button_arrow_right_y,
            button_arrow_right_width,
            button_arrow_right_height,
            "assets/images/ArrowRightBtn.png",
            "assets/images/ArrowRightClick.png",
            action="change_map_right",
            sound_path="assets/sounds/Menu1.wav"
        )
        self.buttons.append(arrow_right_button)

        button_ai_left_width = 40
        button_ai_left_height = 40
        button_ai_left_x = SCREEN_WIDTH // 2 - 320
        button_ai_left_y = SCREEN_HEIGHT - 40
        ai_left_button = Button(
            button_ai_left_x,
            button_ai_left_y,
            button_ai_left_width,
            button_ai_left_height,
            "assets/images/ArrowLeftBtn.png",
            "assets/images/ArrowLeftClick.png",
            action="change_ai_left",
            sound_path="assets/sounds/Menu1.wav"
        )
        self.buttons.append(ai_left_button)

        button_ai_right_width = 40
        button_ai_right_height = 40
        button_ai_right_x = SCREEN_WIDTH // 2 + 250
        button_ai_right_y = SCREEN_HEIGHT - 40
        ai_right_button = Button(
            button_ai_right_x,
            button_ai_right_y,
            button_ai_right_width,
            button_ai_right_height,
            "assets/images/ArrowRightBtn.png",
            "assets/images/ArrowRightClick.png",
            action="change_ai_right",
            sound_path="assets/sounds/Menu1.wav"
        )
        self.buttons.append(ai_right_button)

    def change_ai(self, direction):
        if direction == "left":
            self.selected_ai_index = (self.selected_ai_index - 1) % len(self.ai_list)
        elif direction == "right":
            self.selected_ai_index = (self.selected_ai_index + 1) % len(self.ai_list)
        self.selected_ai = self.ai_list[self.selected_ai_index]
        print(f"Selected AI: {self.selected_ai}")

    def change_map(self, direction):
        if direction == "left":
            self.selected_map_index = (self.selected_map_index - 1) % len(self.map_list)
        elif direction == "right":
            self.selected_map_index = (self.selected_map_index + 1) % len(self.map_list)
        self.selected_map = self.map_list[self.selected_map_index]
        print(f"Selected Map: {self.selected_map}")

    def get_difficulty(self):
        map_number = self.selected_map_index + 1
        if 1 <= map_number <= 3:
            return "Easy"
        elif 4 <= map_number <= 6:
            return "Normal"
        elif 7 <= map_number <= 9:
            return "Hard"
        return "Unknown"

    def transition_to_game(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(0)

        transition_duration = 1000
        start_time = pygame.time.get_ticks()

        while True:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - start_time

            alpha = min(255, (elapsed_time / transition_duration) * 255)
            overlay.set_alpha(int(alpha))

            self.draw(screen)
            screen.blit(overlay, (0, 0))
            pygame.display.flip()

            if elapsed_time >= transition_duration:
                break

            pygame.time.wait(10)

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        for element in self.elements:
            element.check_hover(mouse_pos)
            element.draw(screen)

        for button in self.buttons:
            button.check_hover(mouse_pos)
            button.draw(screen)

        map_label = self.font.render(f"{self.selected_map}", True, self.text_color)
        map_label_rect = map_label.get_rect(center=(SCREEN_WIDTH // 2 + 300, 190))
        screen.blit(map_label, map_label_rect)

        count_label = self.font.render(f"Runs", True, self.text_color)
        count_label_rect = count_label.get_rect(center=(SCREEN_WIDTH // 2 - 300, 200))
        screen.blit(count_label, count_label_rect)

        preview = self.map_previews[self.selected_map]
        preview_rect = preview.get_rect(center=(SCREEN_WIDTH // 2 + 300, SCREEN_HEIGHT // 2 - 70))
        screen.blit(preview, preview_rect)

        rectCoverPreview = pygame.Rect(preview_rect.x, preview_rect.y, preview_rect.width, preview_rect.height)
        pygame.draw.rect(screen, (255, 255, 255), rectCoverPreview, 2)

        difficulty = self.get_difficulty()
        difficulty_label = self.font.render(f"Difficulty: {difficulty}", True, self.text_color)
        difficulty_label_rect = difficulty_label.get_rect(center=(SCREEN_WIDTH // 2 + 300, 450))
        screen.blit(difficulty_label, difficulty_label_rect)

        ai_text = self.font.render(f"{self.selected_ai}", True, self.text_color)
        left_button_x = SCREEN_WIDTH // 2 - 300
        right_button_x = SCREEN_WIDTH // 2 + 250
        ai_center_x = (left_button_x + right_button_x) // 2
        ai_rect = ai_text.get_rect(center=(ai_center_x, SCREEN_HEIGHT - 20))
        screen.blit(ai_text, ai_rect)

    def handle_event(self, event, screen):
        if self.transitioning:
            return None

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for element in self.elements:
                element.check_click(mouse_pos)

        for element in self.elements:
            if hasattr(element, 'handle_event'):
                element.handle_event(event)

        for button in self.buttons:
            result = button.handle_event(event)
            if result:
                if result == "play":
                    try:
                        self.num_runs = int(self.elements[0].text)
                    except ValueError:
                        self.num_runs = 1
                    self.transitioning = True
                    self.transition_to_game(screen)
                    self.transitioning = False
                    return {
                        "algorithm": self.selected_ai,
                        "num_runs": self.num_runs,
                        "map": self.selected_map
                    }
                elif result == "change_map_left":
                    self.change_map("left")
                elif result == "change_map_right":
                    self.change_map("right")
                elif result == "change_ai_left":
                    self.change_ai("left")
                elif result == "change_ai_right":
                    self.change_ai("right")

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.change_map("left")
            elif event.key == pygame.K_RIGHT:
                self.change_map("right")
        return None

class OptionMenu:
    def __init__(self, sound_enabled=True):
        self.buttons = []
        self.sound_enabled = sound_enabled
        self.font = pygame.font.Font("assets/fonts/PressStart2P.ttf", 80)
        self.text_color = (255, 255, 255)
        self.was_opened_by_quit = False
        self.setup_elements()

        # Tạo nền mờ cho menu tạm dừng
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.overlay.fill((0, 0, 0))
        self.overlay.set_alpha(200)

    def setup_elements(self):
        button_width = 150
        button_height = 150
        button_spacing = 300
        start_y = (SCREEN_HEIGHT - (button_height * 3 + button_spacing * 2)) // 2

        # Nút Home (quay lại menu chính)
        home_button = Button(
            (SCREEN_WIDTH - button_width) // 2 - button_spacing,
            start_y + button_height + button_spacing,
            button_width,
            button_height,
            "assets/images/HomeBtn.png",
            "assets/images/HomeClick.png",
            action="home",
            sound_path="assets/sounds/Menu1.wav"
        )
        self.buttons.append(home_button)

        # Nút Sound On/Off (bật/tắt âm thanh)
        sound_button = Button(
            (SCREEN_WIDTH - button_width) // 2 + button_spacing,
            start_y + button_height + button_spacing,
            button_width,
            button_height,
            "assets/images/SoundOnBtn.png" if self.sound_enabled else "assets/images/SoundOffBtn.png",
            "assets/images/SoundOnClick.png" if self.sound_enabled else "assets/images/SoundOffClick.png",
            action="toggle_sound",
            sound_path="assets/sounds/Menu1.wav"
        )
        self.buttons.append(sound_button)

        # Nút Repeat (tiếp tục chơi)
        repeat_button = Button(
            (SCREEN_WIDTH - button_width) // 2,
            start_y + button_height + button_spacing,
            button_width,
            button_height,
            "assets/images/RepeatBtn.png",
            "assets/images/RepeatClick.png",
            action="repeat",
            sound_path="assets/sounds/Menu1.wav"
        )
        self.buttons.append(repeat_button)

    def update_sound_button(self):
        sound_button = self.buttons[1]
        sound_button.normal_image = pygame.image.load(
            "assets/images/SoundOnBtn.png" if self.sound_enabled else "assets/images/SoundOffBtn.png"
        )
        sound_button.pressed_image = pygame.image.load(
            "assets/images/SoundOnClick.png" if self.sound_enabled else "assets/images/SoundOffClick.png"
        )
        sound_button.normal_image = pygame.transform.scale(sound_button.normal_image, (300, 100))
        sound_button.pressed_image = pygame.transform.scale(sound_button.pressed_image, (300, 100))

        for button in self.buttons:
            button.sound_enabled = self.sound_enabled

    def draw(self, screen):
        screen.blit(self.overlay, (0, 0))
        title = self.font.render("Options", True, self.text_color)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title, title_rect)

        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.check_hover(mouse_pos)
            button.draw(screen)

    def handle_event(self, event):
        for button in self.buttons:
            result = button.handle_event(event)
            if result:
                if result == "home":
                    # Luôn trả về "home" để quay lại menu chính, dù mở từ Quit hay ESC
                    return "home"
                elif result == "toggle_sound":
                    self.sound_enabled = not self.sound_enabled
                    self.update_sound_button()
                    return "toggle_sound"
                elif result == "repeat":
                    self.was_opened_by_quit = False
                    return "repeat"
        return None