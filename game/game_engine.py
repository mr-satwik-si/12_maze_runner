import pygame
import time

from game.maze import generate_maze, find_shortest_path
from game.player import Player


FPS = 60

# Maze settings
COLS = 15
ROWS = 13

CELL = 40

WIDTH = COLS * CELL
HEIGHT = ROWS * CELL + 60


# Colors
BG_COLOR = (240, 235, 220)
WALL_COLOR = (40, 40, 60)

EXIT_COLOR = (80, 200, 80)

PLAYER_COLOR = (50, 100, 220)

PATH_COLOR = (255, 215, 0)
PATH_BORDER_COLOR = (220, 160, 0)

HUD_COLOR = (30, 30, 50)
TEXT_COLOR = (220, 220, 220)


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

        self.reset()

    # --------------------------------------------------
    # Generate / Reset Maze
    # --------------------------------------------------

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

        # --------------------------------------------------
        # Task 1 - BFS Hint
        # --------------------------------------------------

        self.show_hint = False

        self.shortest_path = []

    # --------------------------------------------------
    # Event Handling
    # --------------------------------------------------

    def handle_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:

                # ------------------------------------------
                # R = Generate new maze
                # ------------------------------------------

                if event.key == pygame.K_r:

                    self.reset()

                # ------------------------------------------
                # H = Toggle BFS shortest path
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

    # --------------------------------------------------
    # Update
    # --------------------------------------------------

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

        # Check exit
        if self.player.rect.colliderect(
            self.exit_rect
        ):

            self.won = True

    # --------------------------------------------------
    # Draw Maze
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Draw BFS Shortest Path
    # --------------------------------------------------

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

            # Main path cell
            pygame.draw.rect(
                self.screen,
                PATH_COLOR,
                path_rect,
                border_radius=5
            )

            # Border
            pygame.draw.rect(
                self.screen,
                PATH_BORDER_COLOR,
                path_rect,
                width=2,
                border_radius=5
            )

    # --------------------------------------------------
    # Draw
    # --------------------------------------------------

    def draw(self):

        # Background
        self.screen.fill(
            BG_COLOR
        )

        # Maze
        self.draw_maze()

        # BFS path
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

        # Player
        self.player.draw(
            self.screen
        )

        # --------------------------------------------------
        # HUD
        # --------------------------------------------------

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

        hint_status = "ON" if self.show_hint else "OFF"

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

        # --------------------------------------------------
        # Win Screen
        # --------------------------------------------------

        if self.won:

            overlay = pygame.Surface(
                (
                    WIDTH,
                    ROWS * CELL
                ),
                pygame.SRCALPHA
            )

            overlay.fill(
                (0, 0, 0, 140)
            )

            self.screen.blit(
                overlay,
                (0, 0)
            )

            win_text = self.big_font.render(
                f"Solved in {self.elapsed:.1f}s!",
                True,
                (80, 240, 80)
            )

            restart_text = self.font.render(
                "Press R for a new maze",
                True,
                TEXT_COLOR
            )

            self.screen.blit(
                win_text,
                (
                    WIDTH // 2
                    - win_text.get_width() // 2,
                    ROWS * CELL // 2 - 30
                )
            )

            self.screen.blit(
                restart_text,
                (
                    WIDTH // 2
                    - restart_text.get_width() // 2,
                    ROWS * CELL // 2 + 20
                )
            )

        pygame.display.flip()

    # --------------------------------------------------
    # Main Game Loop
    # --------------------------------------------------

    def run(self):

        running = True

        while running:

            running = self.handle_events()

            self.update()

            self.draw()

            self.clock.tick(FPS)

        pygame.quit()
