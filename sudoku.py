from enum import Enum
import random
from itertools import product


class Difficulty(Enum):
    EASY = 0
    MEDIUM = 1
    HARD = 2


class Variable:
    """A Sudoku variable is a position (`line`, `column`) on the board.

    It has a `value` and a `domain` of available values it can take."""

    def __init__(self, line, column):
        self.line, self.column = line, column
        self.domain = set([i for i in range(1, 10)])
        self.value = None

    def __str__(self):
        return f'Variable({self.line + 1, self.column + 1}), value: {self.value}'


class Sudoku:
    def __init__(self, difficulty=Difficulty.MEDIUM):
        self.build_initial_board(difficulty)

    def is_consistent(self):
        """According to the course, the board is consistent if it respects all constraints"""
        for variable in self.variables:
            if variable.value is None:
                continue
            neighbours = self.get_variable_neighbours(variable)
            # if my constraint
            if any(neighbour.value == variable.value for neighbour in neighbours):
                self.print_board()
                print(
                    f'Not consistent on position ({variable.line + 1}, {variable.column + 1})')
                return False
        return True

    def is_complete(self):
        return all(variable.value is not None for variable in self.variables)

    def print_board(self):
        for i in range(0, 9):
            for j in range(0, 9):
                print(self.board[i][j], end=' ')
                if j % 3 == 2:
                    print('|', end=' ')
            if i % 3 == 2:
                print('')
                print('- ' * 12)
            else:
                print('')
        print('\n')

    def solve(self):
        assert self.is_consistent(), "Board is not consistent!"

        if self.is_complete() is True:
            return True

        # pick a variable that doesn't have a value assigned
        # the list below will contain REFERENCES (pointers) to elements from self.variables, which is what I want
        unassigned_variables = [
            var for var in self.variables if var.value is None]

        # another optimization: choose the first variable with the least possible values
        unassigned_variables.sort(key=lambda x: len(x.domain))
        random_var = unassigned_variables[0]
        # random_var = random.choice(unassigned_variables)

        # trying to give it each value
        possible_values = list(random_var.domain)
        for value in possible_values:
            random_var.value = value
            self.board[random_var.line][random_var.column] = value
            random_var.domain.discard(value)
            self.forward_checking(random_var, value_added=value)
            res = self.solve()

            if res is True:
                # I managed to fill up the whole board!!!
                return True

            self.forward_checking(random_var, value_removed=value)
            random_var.value = None
            self.board[random_var.line][random_var.column] = 0
            random_var.domain.add(value)

        return False

    def forward_checking(self, variable: Variable, value_added=None, value_removed=None):
        """
        We suppose that `variable` was just updated. So we must update the domain for the rest of variables

        If `value_added is not None`, then our `variable` has been updated to take on that value.
        So for all the 'neigbours' of `variable`, we update their domains and exclude `value_added`

        if `value_removed is not None`, then our `variable` was unassigned and its neighbours can now take the `value_removed`
        """
        neighbours = self.get_variable_neighbours(variable)

        if value_added is not None:
            # variable.value = value_added
            # variable.domain.discard(value_added)
            # Put the value on the board, yo!
            # self.board[variable.line][variable.column] = value_added
            for neighbour in neighbours:
                neighbour.domain.discard(value_added)
        elif value_removed is not None:
            # variable.value = None
            # variable.domain.add(value_removed)
            # Remove the value from the board, yo!
            # self.board[variable.line][variable.column] = 0
            for neighbour in neighbours:
                neighbour.domain.add(value_removed)

        # TODO
        # if any of the neighbours doesn't have a choice left, that sucks, yo

        return True

    def get_variable_neighbours(self, variable: Variable):
        """A neighbour is a position that is on the same line, column or mini-square as my given `variable`"""
        neighbours = []
        variable_square = self.get_variable_square(variable)
        for neighbour in self.variables:
            if neighbour is variable:
                continue
            neighbour_square = self.get_variable_square(neighbour)
            if neighbour.line == variable.line or neighbour.column == variable.column or neighbour_square == variable_square:
                neighbours.append(neighbour)
        return neighbours

    def get_variable_square(self, variable: Variable):
        """Returns the mini-square for this variable

        The first mini-square (top left, 3x3) is number 0. The next one (top center, 3x3) is number 1 and so on."""
        return (variable.line // 3) * 3 + (variable.column // 3)

    def build_initial_board(self, difficulty):
        self.board = [None] * 9
        for i in range(0, 9):
            self.board[i] = [0 for _ in range(0, 9)]
        # list(product(...)) will generate tuples: (0, 0), (0, 1), ..., (0, 8), (1, 0), ..., (1, 8), ..., (8, 8)
        # which are positions on the board
        self.variables = [Variable(pos[0], pos[1])
                          for pos in list(product([i for i in range(0, 9)], repeat=2))]

        i = 0
        with open('board.txt', 'r') as f:
            for line in f:
                numbers = line.split(' ')
                numbers = [int(x) for x in numbers]
                self.board[i] = numbers
                i += 1
                if i == 9:
                    break

        self.variables = []
        for i in range(0, 9):
            for j in range(0, 9):
                var = Variable(i, j)
                var.value = self.board[i][j] if self.board[i][j] > 0 else None
                self.variables.append(var)

        # update variable domains
        for var in self.variables:
            neighbours = self.get_variable_neighbours(var)
            for neighbour in neighbours:
                var.domain.discard(neighbour.value)
            var.domain.discard(var.value)
        return

        # this is a list with indexes for variables that don't have a value assigned
        unassigned_variables = [i for i in range(0, len(self.variables))]

        if difficulty == Difficulty.EASY:
            no_of_completed_cells = 50
        elif difficulty == Difficulty.MEDIUM:
            no_of_completed_cells = 30
        else:
            no_of_completed_cells = 20

        i = 0
        while (i < no_of_completed_cells):
            assert self.is_consistent(), "Initial board is not consistent!"
            # pick a random unassigned variable
            choice = random.choice(unassigned_variables)
            random_var = self.variables[choice]
            # Choose a random value to assign to this value
            value_assigned = random.choice(tuple(random_var.domain))

            # If, by assigning this value to my random_var I get neighbours that will have no more choices
            # Then things suck, don't they? So don't make this assignment
            neighbours = self.get_variable_neighbours(random_var)
            # If there's any neighbour whose only choice left is this value_assigned
            # then clearly that neighbour wouldn't be able to get any other value
            yes = False
            for neighbour in neighbours:
                if len(neighbour.domain) == 1 and neighbour.value is None and value_assigned in neighbour.domain:
                    yes = True
                    break
            if yes is True:
                continue
            # if any(len(tuple(neighbour.domain)) == 1 and value_assigned in neighbour and neighbour.value is None for neighbour in neighbours):
            #     continue

            random_var.value = value_assigned
            random_var.domain.discard(value_assigned)
            unassigned_variables.remove(choice)
            self.forward_checking(random_var, value_added=value_assigned)
            i += 1

        # Put the values on the board, yo!
        for i in range(0, len(self.variables)):
            if self.variables[i].value is not None:
                self.board[self.variables[i].line][self.variables[i]
                                                   .column] = self.variables[i].value
