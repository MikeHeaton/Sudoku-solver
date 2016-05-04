# Sudoku-solver
A little sudoku solver. The project in progress is to use it to judge how "difficult" a sudoku is, and to evolve THE HARDEST EVER SUDOKU.

Included are solve.py, a program for solving a sudoku;
sudokusearch.py, which uses a beam search with mutation to search the sudoku space looking for the hardest sudoku puzzle
and a number of txt files containing example sudoku grids to try solve.py on. Of particular interest is "superhard2.txt", which is the hardest one I've found so far and beats the internet's standard "hardest sudoku ever" which is "superhard1.txt". But solve.py currently isn't equipped with the full sudoku solving toolkit, meaning it might not corresond to a truly more difficult puzzle.

Files:
____________________solve.py____________________
Takes as a parameter a sudoku grid, and returns the solved grid.
The sudoku grid is a .txt file with the precise format:
"
XXXXXXXXX
[...9 rows total...]
XXXXXXXXX
"
where the X's are numbers 1-9 for filled spaces, or 0 for blanks.
Note there is no error catching, so this format must be followed!
If there isn't a valid solution, the program will terminate when it runs out of options in the agenda. 

Usage: > solve.py grid.txt

This uses a Best First Search to make guesses as to good moves to make, and will always find a solution (if exists) 
because it keeps a full agenda of grids seen so far and so can backtrack as far as it likes. 

The heuristic used is (# of empty spaces after the next guess; possibilities in the next guess) in lexicographic ordering.
This means it prioritises depth first (by taking more complete grids first) but at each step will pick the least risky guess.
That's in line with how I solve Sudokus myself, so that's nice.

Complexity is, I guess, something like O(n*9^n) where n is the number of empty spaces? (As each evalution of a grid has to cycle through each empty space to compare it, and there are up to 9 branches at each step.) But that's not a great bound, because steps will have fewer than 9 branches apiece, even in the most extreme cases.

Thoughts on the algorithm: 1) in a tie break for which square to guess on, it just picks the topleftmost node. That's kinda dumb. Could we look ahead and pick one which leads to some guessless options? That's kinda what I do when guessing in human sudoku.

2) I want to use this solver as a measure of how hard a sudoku is to solve, for the algorithm in the next part. So the algorithm needs to follow how a human would solve a sudoku in order to give a satisfying result. At the moment, it implements "find numbers for a space" method really well. But "find spaces for a number" is just as important a sudoku solving tool, and there are others open to good solvers besides. Is it worth researching how pros do sudoku and coding in each of those tricks, so that the algorithm more closely aligns with human difficulty?

____________________sudokusearch.py____________________
An experiment to search the space of possible sudoku puzzles, searching for a sudoku which solve.py finds the hardest ever to solve.
Method:
> Generate some random starters
> At each step, rate the candidates (using sudokusolve algo)
> Mutate the best few winners, by adding or subtracting some entries.

To do:
When I write the solver, there's the implicit assumption that a solution exists. Therefore when we find a dead end we just back up again and ifnd another way, and before too long we will find a way. But I've found a grid whereby it's obvious to me that there's no solution, but the algorithm doesn't seem to be finding it (it might just be stuck in a loop).
How come I can see it? It's because I'm using "place for a number" logic _as well as_ number for a place logic. (See comments in solve.py.) Can I encode this in solve.py as a check? Seems like it'll be necessary if I'm looking for human-difficult sudokus!!!

Here's a sudoku to use to check if the problem is fixed:
000000000
100000000
900000000
000000007
001500002
000000000
056000000
000080401
094000568
This one seemed to get the algorithm stuck in a loop.
