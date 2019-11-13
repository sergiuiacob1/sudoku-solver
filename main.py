__doc__ = "Solves Sudoku using fancy strategies"

from sudoku import Sudoku, Difficulty

if __name__ == '__main__':
    sudoku = Sudoku(difficulty=Difficulty.EASY)
    sudoku.print_board()
    if sudoku.is_consistent() is False:
        raise Exception('Sudoku board is not consistent!')
    sudoku.solve()
    assert sudoku.is_complete() and sudoku.is_consistent(), "Aoleo buba"
    sudoku.print_board()
