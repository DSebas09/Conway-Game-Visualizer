import random


class GameOfLife:
    def __init__(self, height=30, width=50, wrap=True):
        self.height = height
        self.width = width
        self.wrap = wrap
        self.grid = [[0]*width for _ in range(height)]

    def randomize(self, prob: float = 0.5) -> None:
        for row in range(self.height):
            grid_row = self.grid[row]
            for col in range(self.width):
                grid_row[col] = 1 if random.random() < prob else 0

    def _get_cell(self, row, col):
        if self.wrap:
            return self.grid[row % self.height][col % self.width]

        if 0 <= row < self.height and 0 <= col < self.width:
            return self.grid[row][col]

        return 0

    def _set_cell(self, row, col, val):
        if self.wrap:
            self.grid[row % self.height][col % self.width] = val
        elif 0 <= row < self.height and 0 <= col < self.width:
            self.grid[row][col] = val

    @staticmethod
    def _apply_conway_rules(grid: list[list[int]]) -> list[list[int]]:
        rows = len(grid)
        cols = len(grid[0]) if rows else 0

        # We create a new, empty grid.
        # This is so we can create the next step's state without affecting the current state.
        new_grid = [[0] * cols for _ in range(rows)]

        # Offset of the 8 neighbors
        neighbor_offsets = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1),
        ]

        # We loop through each cell of the original grid
        for row in range(rows):
            for col in range(cols):
                neighbors = 0
                for row_offset, col_offset in neighbor_offsets:
                    neighbor_row, neighbor_col = row + row_offset, col + col_offset
                    if 0 <= neighbor_row < rows and 0 <= neighbor_col < cols:
                        neighbors += grid[neighbor_row][neighbor_col]

                # We apply Conway's rules
                if grid[row][col] == 1:  # Living cell
                    new_grid[row][col] = 1 if (neighbors == 2 or neighbors == 3) else 0
                else:  # Dead Cell
                    new_grid[row][col] = 1 if neighbors == 3 else 0

        return new_grid

    def _extract_subgrid(self, min_row, max_row, min_col, max_col):
        rows = max_row - min_row
        cols = max_col - min_col
        sub_grid = [[0] * cols for _ in range(rows)]
        for row in range(rows):
            for col in range(cols):
                sub_grid[row][col] = self._get_cell(min_row + row, min_col + col)
        return sub_grid

    def step(self, viewport_x, viewport_y, visible_rows, visible_cols, margin=1):
        # Compute region bounds. The region includes not only the viewport,
        # but also a 1-cell "border" around it (by default). This gives us enough context to calculate the neighbors.
        min_row = viewport_y - margin
        min_col = viewport_x - margin
        max_row = viewport_y + visible_rows + margin
        max_col = viewport_x + visible_cols + margin

        # Extract the region that we are interested in rendering
        subgrid = self._extract_subgrid(min_row, max_row, min_col, max_col)

        # Now apply Conway's rules for that region
        new_subgrid = self._apply_conway_rules(subgrid)

        # Only cells within the viewport are written back to the world.
        # The margin is ignored because it only served as a context for calculating neighbors
        rows_sub = len(subgrid)
        cols_sub = len(subgrid[0])
        for row in range(rows_sub):
            viewport_row = min_row + row
            for col in range(cols_sub):
                if margin <= row < rows_sub - margin and margin <= col < cols_sub - margin:
                    viewport_col = min_col + col
                    self._set_cell(viewport_row, viewport_col, new_subgrid[row][col])

        # return only the clean viewport, ready to render on the frontend
        visible = []
        for row in range(margin, rows_sub - margin):
            visible.append(new_subgrid[row][margin:cols_sub - margin])
        return visible


def print_grid(grid):
    for row in grid:
        print("".join("O" if cell else " " for cell in row))
    print("\n" + "-"*len(grid[0]))


# To debug it in a simple way
if __name__ == "__main__":
    # variables to change the size of the board (modifiable for different tests)
    grid_height = 5  # rows
    grid_width = 10  # columns

    game = GameOfLife(grid_height, grid_width)
    game.randomize()
    print("Initial state:")
    print_grid(game.grid)

    game.step()
    print("Después de un paso:")
    for step in range(5):
        print(f"Step {step + 1}:")
        print_grid(game.grid)
        game.step()