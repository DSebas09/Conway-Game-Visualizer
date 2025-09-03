from app.game_of_life import GameOfLife


def test_still_block():
    game = GameOfLife(4,4)
    game.grid = [
        [0,0,0,0],
        [0,1,1,0],
        [0,1,1,0],
        [0,0,0,0]
    ]
    new_grid = game.step()
    assert new_grid == game.grid  # It shouldn't change with this pattern.

def test_blinker():
    game = GameOfLife(5,5)
    game.grid = [
        [0,0,0,0,0],
        [0,0,1,0,0],
        [0,0,1,0,0],
        [0,0,1,0,0],
        [0,0,0,0,0]
    ]
    new_grid = game.step()

    expected = [
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,1,1,1,0],
        [0,0,0,0,0],
        [0,0,0,0,0]
    ]
    assert new_grid == expected


# TODO: Add more tests in the future
