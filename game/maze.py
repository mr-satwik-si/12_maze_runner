import random
from collections import deque


# Size of each maze cell in pixels
CELL = 40


def generate_maze(cols, rows):
    """Generate a maze using recursive backtracking."""

    # Each cell has four walls:
    # [North, South, East, West]
    walls = [
        [[True, True, True, True] for _ in range(cols)]
        for _ in range(rows)
    ]

    visited = [
        [False for _ in range(cols)]
        for _ in range(rows)
    ]

    def get_neighbors(row, col):

        directions = [
            (-1, 0, 0, 1),  # North
            (1, 0, 1, 0),   # South
            (0, 1, 2, 3),   # East
            (0, -1, 3, 2)   # West
        ]

        neighbors = []

        for dr, dc, wall, opposite_wall in directions:

            nr = row + dr
            nc = col + dc

            if (
                0 <= nr < rows
                and 0 <= nc < cols
                and not visited[nr][nc]
            ):
                neighbors.append(
                    (nr, nc, wall, opposite_wall)
                )

        return neighbors

    # Start from top-left cell
    stack = [(0, 0)]
    visited[0][0] = True

    while stack:

        row, col = stack[-1]

        neighbors = get_neighbors(row, col)

        if neighbors:

            nr, nc, wall, opposite_wall = random.choice(
                neighbors
            )

            # Remove wall between current and next cell
            walls[row][col][wall] = False
            walls[nr][nc][opposite_wall] = False

            visited[nr][nc] = True

            stack.append((nr, nc))

        else:

            stack.pop()

    return walls


def find_shortest_path(walls, rows, cols):
    """
    Find the shortest path from (0, 0)
    to (rows - 1, cols - 1) using BFS.
    """

    start = (0, 0)
    goal = (rows - 1, cols - 1)

    queue = deque()

    queue.append(start)

    # Remember how each cell was reached
    parent = {
        start: None
    }

    # Directions:
    # dr, dc, wall index
    directions = [
        (-1, 0, 0),  # North
        (1, 0, 1),   # South
        (0, 1, 2),   # East
        (0, -1, 3)   # West
    ]

    while queue:

        row, col = queue.popleft()

        # Goal reached
        if (row, col) == goal:
            break

        for dr, dc, wall_index in directions:

            nr = row + dr
            nc = col + dc

            # Outside maze
            if not (
                0 <= nr < rows
                and 0 <= nc < cols
            ):
                continue

            # Wall blocks movement
            if walls[row][col][wall_index]:
                continue

            next_cell = (nr, nc)

            # Already visited
            if next_cell in parent:
                continue

            parent[next_cell] = (row, col)

            queue.append(next_cell)

    # No path
    if goal not in parent:
        return []

    # Reconstruct path
    path = []

    current = goal

    while current is not None:

        path.append(current)

        current = parent[current]

    # Reverse:
    # goal -> start
    # becomes
    # start -> goal
    path.reverse()

    return path
