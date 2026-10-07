import pygame
import time
import json
import os

from game.maze import generate_maze, find_shortest_path, CELL
from game.player import Player


FPS = 60

# --------------------------------------------------
# Difficulty settings
# --------------------------------------------------

DIFFICULTIES = {
    "Easy": (10, 8),
    "Medium": (15, 13),
    "Hard": (20, 18)
}


# --------------------------------------------------
# Colors
# --------------------------------------------------

BG_COLOR = (240, 235, 220)
WALL_COLOR = (40, 40, 60)

EXIT_COLOR = (80, 200, 80)

PATH_COLOR = (255, 215, 0)
PATH_BORDER_COLOR = (220, 160, 0)

HUD_COLOR = (30, 30, 50)
TEXT_COLOR = (220, 220, 220)

FOG_COLOR = (0, 0, 0, 230)

BUTTON_COLOR = (70, 100, 180)
BUTTON_HOVER_COLOR = (90, 130, 220)
BUTTON_TEXT_COLOR = (255, 255, 255)

# Fog radius
FOG_RADIUS_CELLS = 3


# --------------------------------------------------
# Leaderboard
# --------------------------------------------------

LEADERBOARD_FILE = "leaderboard.json"
MAX_LEADERBOARD_ENTRIES = 5


class GameEngine:

    def __init__(self):

        pygame.init()

        # Fonts
        self.font = pygame.font.SysFont(
            "monospace",
            20
        )

        self.big_font = pygame.font.SysFont(
            "monospace",
            36,
            bold=True
        )

        self.title_font = pygame.font.SysFont(
            "monospace",
            42,
            bold=True
        )

        self.leaderboard_font = pygame.font.SysFont(
            "monospace",
            22
        )

        # Load leaderboard
        self.leaderboard = self.load_leaderboard()

        # Difficulty screen
        self.difficulty_screen = True
        self.difficulty = None

        # Game state
        self.walls = None
        self.player = None
        self.exit_rect = None

        self.cols = 0
        self.rows = 0
        self.width = 0
        self.height = 0

        self.start_time = 0
        self.elapsed = 0

        self.won = False
        self.score_saved = False

        # BFS
        self.show_hint = False
        self.shortest_path = []

        # Create initial screen
        self.screen = pygame.display.set_mode(
            (800, 600)
        )

        pygame.display.set_caption(
            "Maze Runner"
        )

        self.clock = pygame.time.Clock()

    # ==================================================
    # LEADERBOARD
    # ==================================================

    def load_leaderboard(self):

        if not os.path.exists(
            LEADERBOARD_FILE
        ):
            return []

        try:

            with open(
                LEADERBOARD_FILE,
                "r"
            ) as file:

                data = json.load(file)

            if not isinstance(data, list):
                return []

            valid_times = []

            for value in data:

                try:
                    valid_times.append(
                        float(value)
                    )
                except (ValueError, TypeError):
                    pass

            valid_times.sort()

            return valid_times[
                :MAX_LEADERBOARD_ENTRIES
            ]

        except (
            json.JSONDecodeError,
            OSError
        ):

            return []

    def save_leaderboard(self):

        try:

            with open(
                LEADERBOARD_FILE,
                "w"
            ) as file:

                json.dump(
                    self.leaderboard,
                    file,
                    indent=4
                )

        except OSError:

            pass

    def add_score(self, completion_time):

        self.leaderboard.append(
            round(
                completion_time,
                2
            )
        )

        self.leaderboard.sort()

        self.leaderboard = self.leaderboard[
            :MAX_LEADERBOARD_ENTRIES
        ]

        self.save_leaderboard()

    # ==================================================
    # START SELECTED DIFFICULTY
    # ==================================================

    def start_game(self, difficulty):

        self.difficulty = difficulty

        self.cols, self.rows = DIFFICULTIES[
            difficulty
        ]

        self.width = self.cols * CELL
        self.height = self.rows * CELL + 60

        # Resize window according to maze size
        self.screen = pygame.display.set_mode(
            (
                self.width,
                self.height
            )
        )

        pygame.display.set_caption(
            f"Maze Runner - {difficulty}"
        )

        self.difficulty_screen = False

        self.reset()

    # ==================================================
    # RESET / NEW MAZE
    # ==================================================

    def reset(self):

        # Generate fresh maze
        self.walls = generate_maze(
            self.cols,
            self.rows
        )

        # Player starts at top-left
        self.player = Player(
            0,
            0
        )

        # Exit at bottom-right
        self.exit_rect = pygame.Rect(
            (self.cols - 1) * CELL + 6,
            (self.rows - 1) * CELL + 6,
            CELL - 12,
            CELL - 12
        )

        # Timer
        self.start_time = time.time()
        self.elapsed = 0

        # Game state
        self.won = False
        self.score_saved = False

        # BFS
        self.show_hint = False
        self.shortest_path = []

    # ==================================================
    # DIFFICULTY SCREEN
    # ==================================================

    def draw_difficulty_screen(self):

        self.screen.fill(
            BG_COLOR
        )

        # Title
        title = self.title_font.render(
            "MAZE RUNNER",
            True,
            WALL_COLOR
        )

        self.screen.blit(
            title,
            (
                self.screen.get_width() // 2
                - title.get_width() // 2,
                70
            )
        )

        subtitle = self.font.render(
            "Select Difficulty",
            True,
            WALL_COLOR
        )

        self.screen.blit(
            subtitle,
            (
                self.screen.get_width() // 2
                - subtitle.get_width() // 2,
                130
            )
        )

        # Buttons
        button_width = 300
        button_height = 60

        start_y = 200
        gap = 85

        self.difficulty_buttons = {}

        for index, difficulty in enumerate(
            DIFFICULTIES
        ):

            rect = pygame.Rect(
                self.screen.get_width() // 2
                - button_width // 2,

                start_y + index * gap,

                button_width,
                button_height
            )

            self.difficulty_buttons[
                difficulty
            ] = rect

            mouse_pos = pygame.mouse.get_pos()

            if rect.collidepoint(
                mouse_pos
            ):

                color = BUTTON_HOVER_COLOR

            else:

                color = BUTTON_COLOR

            pygame.draw.rect(
                self.screen,
                color,
                rect,
                border_radius=8
            )

            button_text = self.font.render(
                f"{difficulty}  "
                f"{DIFFICULTIES[difficulty][0]}x"
                f"{DIFFICULTIES[difficulty][1]}",
                True,
                BUTTON_TEXT_COLOR
            )

            self.screen.blit(
                button_text,
                (
                    rect.centerx
                    - button_text.get_width() // 2,

                    rect.centery
                    - button_text.get_height() // 2
                )
            )

        pygame.display.flip()

    # ==================================================
    # DIFFICULTY SCREEN EVENTS
    # ==================================================

    def handle_difficulty_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:

                    for difficulty, rect in (
                        self.difficulty_buttons.items()
                    ):

                        if rect.collidepoint(
                            event.pos
                        ):

                            self.start_game(
                                difficulty
                            )

                            break

        return True

    # ==================================================
    # GAME EVENTS
    # ==================================================

    def handle_game_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:

                # New maze
                if event.key == pygame.K_r:

                    self.reset()

                # BFS hint
                elif event.key == pygame.K_h:

                    self.show_hint = not self.show_hint

                    if self.show_hint:

                        self.shortest_path = (
                            find_shortest_path(
                                self.walls,
                                self.rows,
                                self.cols
                            )
                        )

                    else:

                        self.shortest_path = []

        return True

    # ==================================================
    # UPDATE
    # ==================================================

    def update(self):

        if self.won:
            return

        keys = pygame.key.get_pressed()

        self.player.move(
            keys,
            self.walls,
            self.rows,
            self.cols
        )

        self.elapsed = (
            time.time()
            - self.start_time
        )

        # Check exit
        if self.player.rect.colliderect(
            self.exit_rect
        ):

            self.won = True

            if not self.score_saved:

                self.add_score(
                    self.elapsed
                )

                self.score_saved = True

    # ==================================================
    # DRAW MAZE
    # ==================================================

    def draw_maze(self):

        wall_width = 3

        for row in range(
            self.rows
        ):

            for col in range(
                self.cols
            ):

                x = col * CELL
                y = row * CELL

                cell_walls = self.walls[
                    row
                ][
                    col
                ]

                # North
                if cell_walls[0]:

                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x, y),
                        (x + CELL, y),
                        wall_width
                    )

                # South
                if cell_walls[1]:

                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x, y + CELL),
                        (x + CELL, y + CELL),
                        wall_width
                    )

                # East
                if cell_walls[2]:

                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x + CELL, y),
                        (x + CELL, y + CELL),
                        wall_width
                    )

                # West
                if cell_walls[3]:

                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x, y),
                        (x, y + CELL),
                        wall_width
                    )

    # ==================================================
    # TASK 1 - BFS
    # ==================================================

    def draw_shortest_path(self):

        if not self.show_hint:
            return

        if not self.shortest_path:
            return

        for row, col in self.shortest_path:

            x = col * CELL
            y = row * CELL

            path_rect = pygame.Rect(
                x + 7,
                y + 7,
                CELL - 14,
                CELL - 14
            )

            pygame.draw.rect(
                self.screen,
                PATH_COLOR,
                path_rect,
                border_radius=5
            )

            pygame.draw.rect(
                self.screen,
                PATH_BORDER_COLOR,
                path_rect,
                width=2,
                border_radius=5
            )

    # ==================================================
    # TASK 2 - FOG OF WAR
    # ==================================================

    def draw_fog_of_war(self):

        fog = pygame.Surface(
            (
                self.width,
                self.rows * CELL
            ),
            pygame.SRCALPHA
        )

        fog.fill(
            FOG_COLOR
        )

        player_center = self.player.rect.center

        pygame.draw.circle(
            fog,
            (0, 0, 0, 0),
            player_center,
            FOG_RADIUS_CELLS * CELL
        )

        self.screen.blit(
            fog,
            (0, 0)
        )

    # ==================================================
    # TASK 3 - LEADERBOARD
    # ==================================================

    def draw_leaderboard(self):

        title = self.big_font.render(
            "LEADERBOARD",
            True,
            PATH_COLOR
        )

        self.screen.blit(
            title,
            (
                self.width // 2
                - title.get_width() // 2,
                70
            )
        )

        for index, score in enumerate(
            self.leaderboard
        ):

            text = self.leaderboard_font.render(
                f"{index + 1}.  "
                f"{score:.2f} seconds",
                True,
                TEXT_COLOR
            )

            self.screen.blit(
                text,
                (
                    self.width // 2
                    - text.get_width() // 2,
                    130 + index * 35
                )
            )

        if not self.leaderboard:

            text = self.leaderboard_font.render(
                "No scores yet",
                True,
                TEXT_COLOR
            )

            self.screen.blit(
                text,
                (
                    self.width // 2
                    - text.get_width() // 2,
                    140
                )
            )

    # ==================================================
    # DRAW GAME
    # ==================================================

    def draw_game(self):

        self.screen.fill(
            BG_COLOR
        )

        # Maze
        self.draw_maze()

        # BFS
        self.draw_shortest_path()

        # Exit
        pygame.draw.rect(
            self.screen,
            EXIT_COLOR,
            self.exit_rect,
            border_radius=5
        )

        exit_text = self.font.render(
            "EXIT",
            True,
            (20, 80, 20)
        )

        self.screen.blit(
            exit_text,
            (
                self.exit_rect.x + 2,
                self.exit_rect.y + 6
            )
        )

        # Fog
        self.draw_fog_of_war()

        # Player
        self.player.draw(
            self.screen
        )

        # HUD
        hud_y = self.rows * CELL

        pygame.draw.rect(
            self.screen,
            HUD_COLOR,
            (
                0,
                hud_y,
                self.width,
                60
            )
        )

        hint_status = (
            "ON"
            if self.show_hint
            else "OFF"
        )

        hud_text = self.font.render(
            f"{self.difficulty}    "
            f"Time: {self.elapsed:.1f}s    "
            f"H: Hint {hint_status}    "
            f"R: New Maze",
            True,
            TEXT_COLOR
        )

        self.screen.blit(
            hud_text,
            (
                10,
                hud_y + 20
            )
        )

        # Win screen
        if self.won:

            overlay = pygame.Surface(
                (
                    self.width,
                    self.rows * CELL
                ),
                pygame.SRCALPHA
            )

            overlay.fill(
                (0, 0, 0, 220)
            )

            self.screen.blit(
                overlay,
                (0, 0)
            )

            win_text = self.big_font.render(
                f"Solved in "
                f"{self.elapsed:.2f}s!",
                True,
                (80, 240, 80)
            )

            self.screen.blit(
                win_text,
                (
                    self.width // 2
                    - win_text.get_width() // 2,
                    15
                )
            )

            self.draw_leaderboard()

            restart_text = self.font.render(
                "Press R for a new maze",
                True,
                TEXT_COLOR
            )

            self.screen.blit(
                restart_text,
                (
                    self.width // 2
                    - restart_text.get_width() // 2,
                    self.height - 40
                )
            )

        pygame.display.flip()

    # ==================================================
    # MAIN LOOP
    # ==================================================

    def run(self):

        running = True

        while running:

            if self.difficulty_screen:

                running = (
                    self.handle_difficulty_events()
                )

                if running and self.difficulty_screen:

                    self.draw_difficulty_screen()

            else:

                running = (
                    self.handle_game_events()
                )

                if running:

                    self.update()

                    self.draw_game()

                    self.clock.tick(FPS)

        pygame.quit()
