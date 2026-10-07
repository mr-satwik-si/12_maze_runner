import pygame
import time
import json
import os

from game.maze import generate_maze, find_shortest_path, CELL
from game.player import Player


FPS = 60

# Maze settings
COLS = 15
ROWS = 13

WIDTH = COLS * CELL
HEIGHT = ROWS * CELL + 60


# Colors
BG_COLOR = (240, 235, 220)
WALL_COLOR = (40, 40, 60)

EXIT_COLOR = (80, 200, 80)

PATH_COLOR = (255, 215, 0)
PATH_BORDER_COLOR = (220, 160, 0)

HUD_COLOR = (30, 30, 50)
TEXT_COLOR = (220, 220, 220)

# Fog of War
FOG_COLOR = (0, 0, 0, 230)
FOG_RADIUS_CELLS = 3
FOG_RADIUS = FOG_RADIUS_CELLS * CELL

# Leaderboard
LEADERBOARD_FILE = "leaderboard.json"
MAX_LEADERBOARD_ENTRIES = 5


class GameEngine:

    def __init__(self):

        pygame.init()

        self.screen = pygame.display.set_mode(
            (WIDTH, HEIGHT)
        )

        pygame.display.set_caption(
            "Maze Runner"
        )

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont(
            "monospace",
            20
        )

        self.big_font = pygame.font.SysFont(
            "monospace",
            36,
            bold=True
        )

        self.leaderboard_font = pygame.font.SysFont(
            "monospace",
            22
        )

        # Load existing leaderboard
        self.leaderboard = self.load_leaderboard()

        self.reset()

    # ==================================================
    # LEADERBOARD
    # ==================================================

    def load_leaderboard(self):

        if not os.path.exists(LEADERBOARD_FILE):
            return []

        try:

            with open(
                LEADERBOARD_FILE,
                "r"
            ) as file:

                data = json.load(file)

            # Make sure it is a list
            if not isinstance(data, list):
                return []

            # Keep only valid numbers
            valid_times = []

            for value in data:

                try:
                    valid_times.append(float(value))
                except (ValueError, TypeError):
                    pass

            valid_times.sort()

            return valid_times[:MAX_LEADERBOARD_ENTRIES]

        except (json.JSONDecodeError, OSError):

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

        # Add new completion time
        self.leaderboard.append(
            round(completion_time, 2)
        )

        # Sort fastest first
        self.leaderboard.sort()

        # Keep only top 5
        self.leaderboard = self.leaderboard[
            :MAX_LEADERBOARD_ENTRIES
        ]

        # Save permanently
        self.save_leaderboard()

    # ==================================================
    # RESET / NEW MAZE
    # ==================================================

    def reset(self):

        # Generate a fresh maze
        self.walls = generate_maze(
            COLS,
            ROWS
        )

        # Player starts at top-left
        self.player = Player(
            0,
            0
        )

        # Exit at bottom-right
        self.exit_rect = pygame.Rect(
            (COLS - 1) * CELL + 6,
            (ROWS - 1) * CELL + 6,
            CELL - 12,
            CELL - 12
        )

        # Timer
        self.start_time = time.time()
        self.elapsed = 0

        # Game state
        self.won = False

        # Make sure the score is saved only once
        self.score_saved = False

        # ==================================================
        # TASK 1 - BFS
        # ==================================================

        self.show_hint = False
        self.shortest_path = []

    # ==================================================
    # EVENTS
    # ==================================================

    def handle_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:

                # ------------------------------------------
                # R = New Maze
                # ------------------------------------------

                if event.key == pygame.K_r:

                    self.reset()

                # ------------------------------------------
                # H = BFS Hint
                # ------------------------------------------

                elif event.key == pygame.K_h:

                    self.show_hint = not self.show_hint

                    if self.show_hint:

                        self.shortest_path = find_shortest_path(
                            self.walls,
                            ROWS,
                            COLS
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

        # Player movement
        keys = pygame.key.get_pressed()

        self.player.move(
            keys,
            self.walls,
            ROWS,
            COLS
        )

        # Update timer
        self.elapsed = (
            time.time() - self.start_time
        )

        # Check if player reached exit
        if self.player.rect.colliderect(
            self.exit_rect
        ):

            self.won = True

            # Save completion time only once
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

        for row in range(ROWS):

            for col in range(COLS):

                x = col * CELL
                y = row * CELL

                cell_walls = self.walls[row][col]

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
    # TASK 1 - BFS PATH
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
                WIDTH,
                ROWS * CELL
            ),
            pygame.SRCALPHA
        )

        # Cover entire maze with darkness
        fog.fill(
            FOG_COLOR
        )

        # Player's center
        player_center = self.player.rect.center

        # Reveal circular area around player
        pygame.draw.circle(
            fog,
            (0, 0, 0, 0),
            player_center,
            FOG_RADIUS
        )

        # Draw fog over maze
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
            (255, 215, 0)
        )

        self.screen.blit(
            title,
            (
                WIDTH // 2
                - title.get_width() // 2,
                70
            )
        )

        # Show top 5 scores
        for index, score in enumerate(
            self.leaderboard
        ):

            text = self.leaderboard_font.render(
                f"{index + 1}.  {score:.2f} seconds",
                True,
                TEXT_COLOR
            )

            self.screen.blit(
                text,
                (
                    WIDTH // 2
                    - text.get_width() // 2,
                    130 + index * 35
                )
            )

        # If no scores
        if not self.leaderboard:

            text = self.leaderboard_font.render(
                "No scores yet",
                True,
                TEXT_COLOR
            )

            self.screen.blit(
                text,
                (
                    WIDTH // 2
                    - text.get_width() // 2,
                    140
                )
            )

    # ==================================================
    # DRAW
    # ==================================================

    def draw(self):

        # Background
        self.screen.fill(
            BG_COLOR
        )

        # ----------------------------------------------
        # Maze
        # ----------------------------------------------

        self.draw_maze()

        # ----------------------------------------------
        # BFS
        # ----------------------------------------------

        self.draw_shortest_path()

        # ----------------------------------------------
        # Exit
        # ----------------------------------------------

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

        # ----------------------------------------------
        # Fog
        # ----------------------------------------------

        self.draw_fog_of_war()

        # ----------------------------------------------
        # Player
        # ----------------------------------------------

        self.player.draw(
            self.screen
        )

        # ----------------------------------------------
        # HUD
        # ----------------------------------------------

        hud_y = ROWS * CELL

        pygame.draw.rect(
            self.screen,
            HUD_COLOR,
            (
                0,
                hud_y,
                WIDTH,
                60
            )
        )

        hint_status = (
            "ON"
            if self.show_hint
            else "OFF"
        )

        hud_text = self.font.render(
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

        # ----------------------------------------------
        # TASK 3 - WIN SCREEN
        # ----------------------------------------------

        if self.won:

            # Dark overlay
            overlay = pygame.Surface(
                (
                    WIDTH,
                    ROWS * CELL
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

            # Completion message
            win_text = self.big_font.render(
                f"Solved in {self.elapsed:.2f}s!",
                True,
                (80, 240, 80)
            )

            self.screen.blit(
                win_text,
                (
                    WIDTH // 2
                    - win_text.get_width() // 2,
                    15
                )
            )

            # Leaderboard
            self.draw_leaderboard()

            # Restart message
            restart_text = self.font.render(
                "Press R for a new maze",
                True,
                TEXT_COLOR
            )

            self.screen.blit(
                restart_text,
                (
                    WIDTH // 2
                    - restart_text.get_width() // 2,
                    HEIGHT - 40
                )
            )

        pygame.display.flip()

    # ==================================================
    # MAIN LOOP
    # ==================================================

    def run(self):

        running = True

        while running:

            running = self.handle_events()

            self.update()

            self.draw()

            self.clock.tick(FPS)

        pygame.quit()
