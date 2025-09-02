import random


class GameOfLife:
    def __init__(self, height=30, width=50):
        self.height = height
        self.width = width
        self.grid = [[0]*width for _ in range(height)]

    def randomize(self):
        new_grid = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                cell = random.randint(0, 1)
                row.append(cell)
            new_grid.append(row)
        self.grid = new_grid

    def step(self):
        # We create a new, empty grid.
        # This is so we can create the next step's state without affecting the current state.
        new_grid = []
        for y in range(self.height):
            new_row = []
            for x in range(self.width):
                new_row.append(0)
            new_grid.append(new_row)

        # We loop through each cell of the original grid
        for y in range(self.height):
            for x in range(self.width):
                # So now we are in the current cell
                # Count living neighbors
                neighbors = 0
                for i in [-1, 0, 1]:
                    for j in [-1, 0, 1]:
                        if i == 0 and j == 0:
                            # We do not count the current cell, since we only want the neighbors
                            # i = 0 and j = 0 would leave us in the same cell as the current loop
                            continue
                        # Use % to apply a “circular” border
                        neighbor_y = (y + i) % self.height
                        neighbor_x = (x + j) % self.width
                        # We want the sum of how many neighbors there are
                        neighbors += self.grid[neighbor_y][neighbor_x]

                # We apply Conway's rules
                if self.grid[y][x] == 1:  # Living cell
                    if neighbors == 2 or neighbors == 3:
                        new_grid[y][x] = 1  # Survive
                    else:
                        new_grid[y][x] = 0  # Dies
                else:  # Dead Cell
                    if neighbors == 3:
                        new_grid[y][x] = 1  # Born
                    else:
                        new_grid[y][x] = 0  # No change

        self.grid = new_grid
        return self.grid


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