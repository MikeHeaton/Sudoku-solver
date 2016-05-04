"""
___Genetic Algorithm___
An experiment to search the space of possible sudoku puzzles, searching for a sudoku which solve.py finds the hardest ever to solve.


Method:

> Generate some random starters

> At each step, rate the candidates (using sudokusolve algo)

> Mutate the best few winners a number of times, by adding or subtracting some entries.
> Repeat
"""

import Solve
import random 

def search_hardest_sudoku(beamwidth, statestoexpand, expectedstartingvalues, maxgenerations, expectedmutations):
	#Generate =beamwidth random starting sudokus in a list sudokubeam
	
	random.seed()
	sudokubeam = range(0,beamwidth)

	for n in range(0,beamwidth):
		sudokubeam[n] = Solve.Sudokugrid([ [0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0]] )
		
		for i in range(0,9):
			for j in range(0,9):
				t = random.random()
				if t < float(expectedstartingvalues) / 81.0:	
					sudokubeam[n].randomise(i,j)
				
	print sudokubeam
	
	#Do while numgenerations < maxgenerations:
	for numgenerations in range(0,maxgenerations):

	#Mutate each of the =beamwidth sudokus into =nummutations other ones, collect them into list mutatedsudokus
		mutatedsudokus = []
		mutatedsudokuscores = []
		for originalgrid in sudokubeam:
			for i in range(0,statestoexpand):
				mutatedsudokus.append(mutate_sudoku(originalgrid,expectedmutations))
				mutatedsudokuscores.append(Solve.solvesudoku(mutatedsudokus[-1]))
			
		sudokubeam = []
		
		
		for i in range(1,beamwidth):
			maxvalue = max(mutatedsudokuscores)
			if i == 1:
				storemax = max(mutatedsudokuscores)
			t = random.choice([i for i, j in enumerate(mutatedsudokuscores) if j == maxvalue])
			sudokubeam.append(mutatedsudokus[t])
			mutatedsudokuscores.pop(t)
			mutatedsudokus.pop(t)
			
		print "----------------------------------------Generation ", numgenerations, " finished----------------------------------------"
		#ignore = raw_input()
		print "Current leader, with score of ", storemax, " is:"
		print sudokubeam[0]
		#print "Printing full beam:"
		ignore = raw_input()
		print sudokubeam
		print "Continuing..."
		#ignore = raw_input()
		
	beamscores = [Solve.solvesudoku(a) for a in sudokubeam]
	winningscore = max(beamscores)
	winners = [i for i,j in enumerate(beamscores) if j == winningscore]

	return (winners[0], storemax)
		
def mutate_sudoku(mutee, expectedmutations):
	mutant = Solve.Sudokugrid([[1 for i in range(0,9)] for j in range(0,9)])
	mutant.copy(mutee)
	
	for i in range(0,9):
		for j in range(0,9):
			p = random.random()
			if p < float(expectedmutations) / 81.0:
				#Flip from a number to 0, or vice versa. NOTE: is this the best way to do it? Or should we allow from a number to a different number?
				if mutant.val(i,j) == 0:
					mutant.randomise(i,j)
				else:
					mutant.set(i,j,0)
		
	return mutant
	


#search_hardest_sudoku(beamwidth, statestoexpand, expectedstartingvalues, maxgenerations, expectedmutations):
hardestsudoku = search_hardest_sudoku(10, 20, 10, 10, 3)
print "The winner is:\n",hardestsudoku[0]
print "with a score of ",hardestsudoku[1],"."


"""
NOTE: These sudokus aren't necessarily uniquely solvable :( can I modify the algorithm to check for unique solveness? Perhaps but I don't want to brute 
force every solution because that is A) messy and B) longgggg
24/3/16: apparently brute force is the only way. So probably discard that assumption.

---Thoughts 24/3/16---
When I write the solver, there's the implicit assumption that a solution exists. Therefore when we find a dead end we just back up again and ifnd another way,
and before too long (presumably) we will find a way.
But I've found a grid whereby it's obvious to me that there's no solution, but the algorithm doesn't seem to be finding it (it might just be stuck in a loop).
How come I can see it? It's because I'm using "place for a number" logic _as well as_ number for a place logic.
Can I encode this as a check? Seems like it'll be necessary if I'm looking for human-difficult sudokus!!!

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
"""