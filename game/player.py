import pygame
from game.maze import CELL


SPEED = 3

# Thickness of the actual collision wall.
# This matches the wall thickness used when drawing the maze.
WALL_THICKNESS = 3


class Player:

    def __init__(self, r, c):

        self.r = r
        self.c = c

        # Start at the center of the cell
        x = c * CELL + CELL // 2
        y = r * CELL + CELL // 2

        # Player is a 20x20 circle
        self.rect = pygame.Rect(
            x - 10,
            y - 10,
            20,
            20
        )

        self.color = (60, 120, 220)

    # ==================================================
    # PLAYER MOVEMENT
    # ==================================================

    def move(self, keys, walls, rows, cols):

        dx = 0
        dy = 0

        # Horizontal movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -SPEED

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = SPEED

        # Vertical movement
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -SPEED

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = SPEED

        # ----------------------------------------------
        # Move horizontally
        # ----------------------------------------------

        if dx != 0:

            new_rect = self.rect.move(
                dx,
                0
            )

            if not self._hits_wall(
                new_rect,
                walls,
                rows,
                cols
            ):

                self.rect = new_rect

        # ----------------------------------------------
        # Move vertically
        # ----------------------------------------------

        if dy != 0:

            new_rect = self.rect.move(
                0,
                dy
            )

            if not self._hits_wall(
                new_rect,
                walls,
                rows,
                cols
            ):

                self.rect = new_rect

    # ==================================================
    # WALL COLLISION
    # ==================================================

    def _hits_wall(
        self,
        rect,
        walls,
        rows,
        cols
    ):
        """
        Check whether the player's new rectangle
        physically intersects a maze wall.

        walls[row][col]:

        [North, South, East, West]
        [   0,     1,    2,    3]
        """

        # --------------------------------------------------
        # Outside maze boundary
        # --------------------------------------------------

        if rect.left < 0:
            return True

        if rect.top < 0:
            return True

        if rect.right > cols * CELL:
            return True

        if rect.bottom > rows * CELL:
            return True

        # --------------------------------------------------
        # Check every maze cell that could overlap player
        # --------------------------------------------------

        start_col = max(
            0,
            rect.left // CELL
        )

        end_col = min(
            cols - 1,
            (rect.right - 1) // CELL
        )

        start_row = max(
            0,
            rect.top // CELL
        )

        end_row = min(
            rows - 1,
            (rect.bottom - 1) // CELL
        )

        for row in range(
            start_row,
            end_row + 1
        ):

            for col in range(
                start_col,
                end_col + 1
            ):

                cell_x = col * CELL
                cell_y = row * CELL

                cell_walls = walls[row][col]

                # ==========================================
                # NORTH WALL
                # ==========================================

                if cell_walls[0]:

                    wall_rect = pygame.Rect(
                        cell_x,
                        cell_y - WALL_THICKNESS // 2,
                        CELL,
                        WALL_THICKNESS
                    )

                    if rect.colliderect(
                        wall_rect
                    ):

                        return True

                # ==========================================
                # SOUTH WALL
                # ==========================================

                if cell_walls[1]:

                    wall_rect = pygame.Rect(
                        cell_x,
                        cell_y + CELL
                        - WALL_THICKNESS // 2,
                        CELL,
                        WALL_THICKNESS
                    )

                    if rect.colliderect(
                        wall_rect
                    ):

                        return True

                # ==========================================
                # EAST WALL
                # ==========================================

                if cell_walls[2]:

                    wall_rect = pygame.Rect(
                        cell_x + CELL
                        - WALL_THICKNESS // 2,
                        cell_y,
                        WALL_THICKNESS,
                        CELL
                    )

                    if rect.colliderect(
                        wall_rect
                    ):

                        return True

                # ==========================================
                # WEST WALL
                # ==========================================

                if cell_walls[3]:

                    wall_rect = pygame.Rect(
                        cell_x
                        - WALL_THICKNESS // 2,
                        cell_y,
                        WALL_THICKNESS,
                        CELL
                    )

                    if rect.colliderect(
                        wall_rect
                    ):

                        return True

        return False

    # ==================================================
    # DRAW PLAYER
    # ==================================================

    def draw(self, screen):

        pygame.draw.ellipse(
            screen,
            self.color,
            self.rect
        )
