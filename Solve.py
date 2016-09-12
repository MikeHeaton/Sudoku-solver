"""
Written by Mike Heaton, 14/3/16.
Solve.py

Usage: from command line, run
> python solve.py sudokugrid.txt

Solve.py: takes as a parameter a sudoku grid, and outputs the solved grid to
the screen (along with some workings). The sudoku grid is a .txt file
with the precise format:

XXXXXXXXX
[...9 rows total...]
XXXXXXXXX

where the 0's are numbers 1-9 for filled spaces, or 0 for blanks. Note there
is no error catching, so this format must be followed! If there isn't a valid
solution, the program will terminate when it runs out of options in the agenda.

This uses a Best First Search to make guesses as to good moves to make, and
will always find a solution (if it exists) because it keeps a full agenda of
grids seen so far and so can backtrack as far as it likes.

The heuristic used is (# of empty spaces after the next guess; possibilities
in the next guess) in lexicographic ordering. This means it prioritises depth
first (by taking more complete grids first) but at each step will pick the\
least risky guess. That follows how I solve Sudokus myself, so that's nice.

Complexity is, I guess, something like O(n*9^n) where n is the number of
empty spaces? (As each evalution of a grid has to cycle through each empty
space to compare it, and there are up to 9 branches at each step.)
But that's not a great bound, because steps will have fewer than 9 branches
apiece, even in the most extreme cases.
"""

import sys
import time
import random


class Sudokugrid():

    def __init__(self, grid=[[0 for i in range(0, 9)] for j in range(0, 9)]):
        # Grid is a 9x9 array holding the game state.
        self._grid = grid

    def __repr__(self):
        gridstring = ''
        for j in range(0, 9):
            gridstring = gridstring + str(self._grid[j]) + "\n"
        return gridstring

    def querysquare(self, x, y):
        # Returns the set of possibilities for the queried square,
        # based on existing values.
        if self._grid[x][y] != 0:
            return {self._grid[x][y]}

        possibilities = {1, 2, 3, 4, 5, 6, 7, 8, 9}
        for i in range(0, 9):
            # Search row and column, delete any posssibilities you find.
            possibilities.discard(self._grid[x][i])
            possibilities.discard(self._grid[i][y])

        # Search the local 3x3 cell, delete any possibilities you find.
        for cell in self.sub_box(x, y):
            possibilities.discard(self.val(*cell))

        return list(possibilities)

    def copy(self, othergrid):
        # Sets the grid to a copy of the given grid. Used by the "expand"
        # function to make variants of existing grids as different
        # python objects.
        for i in range(0, 9):
            for j in range(0, 9):
                self._grid[i][j] = othergrid.val(i, j)
        return 0

    def randomise(self, i, j):
        # Sets square (i,j) to a random nonzero value, subject to already
        # existing rules
        possiblevals = self.querysquare(i, j)
        if possiblevals == []:
            self.set(i, j, 0)
            return 0
        else:
            selection = random.choice(self.querysquare(i, j))
            self.set(i, j, selection)
            return selection

    def set(self, x, y, n):
        # Sets square (x,y) to value n.
        self._grid[x][y] = n
        return n

    def val(self, x, y):
        # Grabs the value of (x,y) without touching _grid.
        return self._grid[x][y]

    def sub_box(self, x, y):
        # Returns the coordinates of the box that (x,y) is in, as a list.
        # Explicit declarations are faster than list comprehensions!
        TL = [(0, 0), (1, 0), (2, 0),
              (0, 1), (1, 1), (2, 1),
              (0, 2), (1, 2), (2, 2)]
        TM = [(3, 0), (4, 0), (5, 0),
              (3, 1), (4, 1), (5, 1),
              (3, 2), (4, 2), (5, 2)]
        TR = [(6, 0), (7, 0), (8, 0),
              (6, 1), (7, 1), (8, 1),
              (6, 2), (7, 2), (8, 2)]
        ML = [(0, 3), (1, 3), (2, 3),
              (0, 4), (1, 4), (2, 4),
              (0, 5), (1, 5), (2, 5)]
        MM = [(3, 3), (4, 3), (5, 3),
              (3, 4), (4, 4), (5, 4),
              (3, 5), (4, 5), (5, 5)]
        MR = [(6, 3), (7, 3), (8, 3),
              (6, 4), (7, 4), (8, 4),
              (6, 5), (7, 5), (8, 5)]
        BL = [(0, 6), (1, 6), (2, 6),
              (0, 7), (1, 7), (2, 7),
              (0, 8), (1, 8), (2, 8)]
        BM = [(3, 6), (4, 6), (5, 6),
              (3, 7), (4, 7), (5, 7),
              (3, 8), (4, 8), (5, 8)]
        BR = [(6, 6), (7, 6), (8, 6),
              (6, 7), (7, 7), (8, 7),
              (6, 8), (7, 8), (8, 8)]

        for box in [TL, TM, TR, ML, MM, MR, BL, BM, BR]:
            if (x, y) in box:
                    return box

    def readintogrid(self, fname):
        f = open(fname, 'r')

        for i in range(0, 9):
            newline = f.readline()
            for j in range(0, 9):
                self.set(i, j, int(newline[j]))


def expand(grid):
    # Takes as input a sudoku grid. Cycles through the empty spaces and picks
    # a most promising option to expand. The "most promising option" is the
    # square with the fewest numbers which could fit in there. Returns a list
    # of all the pairs [Newgrid, cost], where Newgrid is the grid formed by
    # guessing a number in the square. If the candidate is a finished grid,
    # returns 0.

    mincost = 10
    minx = [10]
    miny = [10]
    zerocount = 0

    for i in range(0, 9):
        for j in range(0, 9):
            # if we've arrived in a place where there's no
            # options for a space in the grid, then the search will note that
            # the cost is 0 and will pick that one, but this will result in no
            # further grid placements because the "options" set will be empty.
            # That means the algorithm naturally stops searching that path
            # once a dead end is reached, without any explicit code!

            if grid.val(i, j) == 0:
                zerocount += 1
                if len(grid.querysquare(i, j)) < mincost:
                    mincost = len(grid.querysquare(i, j))
                    minx = [i]
                    miny = [j]

                if len(grid.querysquare(i, j)) == mincost:
                    minx.append(i)
                    miny.append(i)

    # If zerocount is 0 the grid is full, so we're done.
    if zerocount == 0:
        return [0]

    # Choose one of the best options (random to improve average performance)
    chosen_index = random.choice(range(0, len(minx)))
    chosen_x = minx[chosen_index]
    chosen_y = miny[chosen_index]
    options = grid.querysquare(chosen_x, chosen_y)

    # To return a value: create a new copy grid for each option and pass
    # that back to the function, along with the path cost for that choice.
    # This is a kind of janky way to do it - isn't there a nicer way to pass
    # by value? (Research suggests no there isn't!)

    newgrids = []
    for choice in options:
        newgrids.append((Sudokugrid([[0 for i in range(0, 9)] for j in range(0, 9)]),
                        mincost, zerocount-1))
        newgrids[-1][0].copy(grid)
        newgrids[-1][0].set(chosen_x, chosen_y, choice)

    return newgrids


def optimisestep(agenda):
    # Takes as input an agenda of possible states to evaluate. Picks a most
    # promising one, expands it, and returns the new agenda.

    if agenda == []:
        # print "Empty agenda ==> No solution found."
        return ["Nope"]

    mincost = 10
    leastzeroes = 1000
    bestcandidates = None
    for candidate in agenda:
        # Cycle through candidates in the agenda to find the best one.
        # Could also be done using an argmin() function.
        if candidate[2] < leastzeroes:  # If it's closer to completion,
            mincost = candidate[1]      # prioritise it.
            leastzeroes = candidate[2]
            bestcandidates = [candidate]
        elif candidate[2] == leastzeroes and candidate[1] < mincost:
            mincost = candidate[1]        # If it's just as close to completion
            bestcandidates = [candidate]  # but has better guess, take it
        elif candidate[2] == leastzeroes and candidate[1] == mincost:
            bestcandidates.append(candidate)

    # Out of the equally good candidates,
    # pick a random one for better av performance.
    chosencandidate = random.choice(bestcandidates)
    agenda.remove(chosencandidate)
    fin = expand(chosencandidate[0])

    if len(fin) != 0:
        if fin[0] == 0:
            return ["done!", chosencandidate]

    fin.extend(agenda)
    return fin


def readintogrid(fname):
    f = open(fname, 'r')

    newgrid = Sudokugrid([[1 for i in range(0, 9)] for j in range(0, 9)])

    for i in range(0, 9):
        newline = f.readline()
        for j in range(0, 9):
            newgrid.set(i, j, int(newline[j]))

    return newgrid


# ------MAIN FUNCTION------#
def solvesudoku(test):
    print("--- Now solving new grid ---")
    print(test)

    start_time = time.time()

    # Initial check: is it a legal grid? Abort if not.
    # Note that after this initial step, the algorithm restricts to legal
    # steps only and so won't return an incorrect solution. But without this
    # initial check, it's possible that the program will think it's done when
    # the solution is illegal because the initial position was illegal.

    illegal = 0
    for x in range(0, 9):
        for y in range(0, 9):
            if test.val(x, y) != 0:
                for k in range(0, 9):
                    # Search row and column; any matches you find,
                    # fail and break.
                    if test.val(k, y) == test.val(x, y) and k != x:
                        illegal = 1
                        break

                    if test.val(x, k) == test.val(x, y) and k != y:
                        illegal = 1
                        break

                # Search box; any matches you find, fail and break.
                for (i, j) in test.sub_box(x, y):
                    if test.val(i, j) == test.val(x, y) and (i, j) != (x, y):
                        illegal = 1
                        break

            # If the square is overdetermined, fail and break.
            # After the initial step this isn't needed, but it's a necessary
            # check at the beginning.
            if test.querysquare(x, y) == []:
                illegal = 1
                break

    if illegal == 1:
        print("Illegal grid.")
        return -1

    numberofsteps = 1

    agenda = optimisestep([(test, 1, 100)])

    # Keep running optimisestep, to manage the next iteration of the agenda,
    # until we reach a solution, or until we run out of agenda which breaks
    # the loop.
    while agenda[0] != "done!":
        numberofsteps += 1
        agenda = optimisestep(agenda)
        if agenda == []:
            break

    # Print results
    if agenda == []:
        print("No solution. Finished in ", (time.time() - start_time),
              " seconds and ", numberofsteps, "steps.")
        return -1
    elif agenda[0] == "done!":
        # print "\nFinished!\n"
        print(agenda[1][0])
        print("Finished in ", (time.time() - start_time), " seconds and ",
              numberofsteps, "steps.")
        return numberofsteps
    else:
        print("Error: script terminated without either a complete grid, ",
              "or concluding the puzzle is impossible.")
        return -1


newgrid = Sudokugrid()
newgrid.readintogrid("easy1.txt")
solvesudoku(newgrid)
"""
if __name__ == '__main__':
    newgrid = Sudokugrid()
    newgrid.readintogrid(sys.argv[1])
    solvesudoku(newgrid)
"""