"""
Written by Mike Heaton, 14/3/16.
Solve.py

Solve.py: takes as a parameter a sudoku grid, and outputs the solved grid to the screen (along with some neat workings).
The sudoku grid is a .txt file with the precise format:

000000000
[...9 rows total...]
000000000

where the 0's are numbers 1-9 for filled spaces, or 0 for blanks.
Note there is no error catching, so this format must be followed!
If there isn't a valid solution, the program will terminate when it runs out of options in the agenda. Unfortunately this could take a long time,
if for example it's fed "110000000/000000000/000..." because the agenda multiplies super fast and doesn't fail until the very end.

This uses a Best First Search to make guesses as to good moves to make, but will always find a solution (if exists) 
because it keeps a full agenda of grids seen so far and so can backtrack as far as it likes. 

The heuristic used is (# of empty spaces after the next guess, possibilities in the next guess) in lexicographic ordering.
This means it prioritises depth first (by taking more complete grids first) but at each step will pick the least risky guess.
That's in line with how I solve Sudokus myself, so that's nice.

Complexity is, I guess, something like O(n*9^n) where n is the number of empty spaces? (As each evalution of a grid has to cycle through each empty space
to compare it, and there are up to 9 branches at each step.) But that's not a great bound, because steps will have fewer than 9 branches apiece, even in 
the most extreme cases.

Potential to explore: what's the 'hardest to solve' grid? Could I find that out in another search, say by genetic algorithming a sudoku grid and using
the heuristic as the number of steps that this thing takes to solve it? That sounds kinda fun, potential subject of a blog post called "THE HARDEST SUDOKU".

Thought on the algorithm: in a tie break for which square to guess on, it just picks the topleftmost node. That's kinda dumb. Could we look ahead 
and pick one which leads to some guessless options? That's kinda what I do when guessing in human sudoku.
"""
import sys 
import time
import random


class Sudokugrid():

	def __init__(self, grid):
		#Grid is a 9x9 array holding the game state.
		self._grid = grid
		
	def __repr__(self):
		gridstring = ''
		for j in range(0,9):
			gridstring = gridstring + str(self._grid[j]) + "\n"
		return gridstring
		
	def querysquare(self,x,y):
		#Returns the set of possibilities for the queried square, based on existing values.
		if self._grid[x][y] != 0:
			return {self._grid[x][y]}
			
		
		possibilities = {1,2,3,4,5,6,7,8,9}
		for i in range(0,9):
			#Search row and column, delete any possibilities you find here.
			possibilities.discard(self._grid[x][i])
			possibilities.discard(self._grid[i][y])
			
		#Search the local 3x3 cell, delete any possibilities you find here.
		for cell in self.sub_box(x,y):
			possibilities.discard(self.val(*cell))
			
		return list(possibilities)
		
	def copy(self, othergrid):
		#Sets the grid to a copy of the given grid. Used by the "expand" function to make variants of existing grids as different python objects.
		for i in range(0,9):
			for j in range(0,9):
				self._grid[i][j] = othergrid.val(i,j)
		return 0
		
	def randomise(self, i, j):
		#Sets square (i,j) to a random nonzero value, subject to already existing rules
		possiblevals = self.querysquare(i,j)
		if possiblevals == []:
			self.set(i,j,0)
			return 0
		else:
			selection = random.choice(self.querysquare(i,j))
			self.set(i,j,selection)
			return selection
			
	def set(self,x,y,n):
		#Sets square (x,y) to value n.
		self._grid[x][y] = n
		return n

	def val(self,x,y):
		#Grabs the value of (x,y) without touching _grid.
		return self._grid[x][y]
		
	def sub_box(self,x,y):
		#Returns the coordinates of the box that (x,y) is in, as a list.
		for p in [0,3,6]:
			for q in [0,3,6]:
				if (x,y) in [(m,n) for m in [p,p+1,p+2] for n in [q,q+1,q+2]]:
					return [(m,n) for m in [p,p+1,p+2] for n in [q,q+1,q+2]]
			

def expand(grid):
	#Takes as input a sudoku grid. Cycles through the empty spaces and picks the most promising option to expand. 
	#Returns a list of all the pairs [Newgrid, cost] for that promising option.
	#If the candidate is finished, returns 0.
	mincost = 10
	minx = 10
	miny = 10
	zerocount = 0
	
	for i in range(0,9):
		for j in range(0,9):
			if grid.val(i,j) == 0:
			#We only consider blank spaces for update. This has a neat consequence: if we've arrived in a place where there's no options for a certain grid, then the 
			#search will note that the cost is 0 and will pick that one, but this will result in no further grid placements because the "options" set will be empty.
			#That means the algorithm naturally stops searching that path once a dead end is reached, without any explicit code!
			
			#23/3/16: turns out this doesn't happen if there's an overdetermined space in the initial grid, obvious really. Included as an initial check in the main function.
				zerocount += 1
				if len(grid.querysquare(i,j)) < mincost:
					mincost = len(grid.querysquare(i,j))
					minx = i
					miny = j
	
	#If zerocount is 0, the grid is full, so we're done.	
	if zerocount == 0:
		return [0]

	options = grid.querysquare(minx,miny)

	#Create a new copy grid for each option and pass that back to the function, along with the path cost for that choice. 
	#This is a kind of janky way to do it - isn't there a nicer way to pass by value? (Research suggests no there isn't!)
		
	t = []
	for choice in options:
		t.append((Sudokugrid([[0 for i in range(0,9)] for j in range(0,9)]),mincost,zerocount-1))
		t[-1][0].copy(grid)
		t[-1][0].set(minx,miny,choice)
				
	return t
			
def optimisestep(agenda):
	#Takes as input an agenda of possible states to evaluate. Picks the most promising one, expands it, and returns the new agenda.
	
	if agenda == []:
		#print "Empty agenda ==> No solution found."
		return ["Nope"]
		
	mincost = 10
	leastzeroes = 1000
	bestcandidate = None
	for candidate in agenda:
		if candidate[2] < leastzeroes: 									#If it's closer to completion, prioritise it
			mincost = candidate[1]
			leastzeroes = candidate[2]
			bestcandidate = candidate
		elif candidate[2] == leastzeroes and candidate[1] < mincost: 	#If it's just as close to completion but has a better guess, prioritise it
			mincost = candidate[1]
			bestcandidate = candidate
		
	agenda.remove(bestcandidate)
	fin = expand(bestcandidate[0])
		
	if len(fin) != 0:
		if fin[0] == 0:
			return ["done!", bestcandidate]
	
	fin.extend(agenda)  #Appends fin to the front of the agenda, so that new boxes are prioritised over old ones in case of a tie.
						#This seems to give a performance bonus, because it helps the algorithm run depth-first.
						#Might be equal to the other way round since adding prioritisation by number of empty squares, but it's not worth testing.
	return fin
		
def readintogrid(fname):
	f = open(fname,'r')
	
	newgrid = Sudokugrid([[1 for i in range(0,9)] for j in range(0,9)])
	
	for i in range(0,9):
		newline = f.readline()
		for j in range(0,9):
			newgrid.set(i,j,int(newline[j]))

	return newgrid

#------MAIN FUNCTION------#
def solvesudoku(test):
	print "--- Now solving new grid ---"
	print test

	start_time = time.time()

	#Initial check: is it a legal grid? Abort if not.
	#Note that after this initial step, the algorithm restricts to legal steps only and so won't return an incorrect solution. 
	#But without this initial check, it's possible that the program will think it's done when the solution is illegal 
	#because the initial position was illegal.
	
	illegal = 0
	for x in range(0,9):
		for y in range(0,9):
			if test.val(x,y) != 0:
				for k in range(0,9):
					#Search row and column; any matches you find, fail and break.
					if test.val(k,y) == test.val(x,y) and k != x:
						illegal = 1
						break
					
					if test.val(x,k) == test.val(x,y) and k != y:
						illegal = 1
						break	
						
				#Search box; any matches you find, fail and break.				
				for (i,j) in test.sub_box(x,y):
					if test.val(i,j) == test.val(x,y) and (i,j) != (x,y):
						illegal = 1
						break
			
			#If the square is overdetermined, fail and break. After the initial step this isn't needed, but it's a necessary check at the beginning.
			if test.querysquare(x,y) == []:
				illegal = 1
				break

	if illegal == 1:
		print "Illegal grid."
		return -1	
	
	
	numberofsteps = 1
	
	agenda = optimisestep([(test,1,100)])

	#Keep running optimisestep, to manage the next iteration of the agenda, until we reach a solution, or until we run out of agenda which breaks the loop.
	while agenda[0] != "done!":	
		numberofsteps += 1
		agenda = optimisestep(agenda)
		if agenda == []:
			break

	#Print results
	if agenda == []:
		print "No solution. Finished in ",(time.time() - start_time)," seconds and ", numberofsteps, "steps."
		return -1
	elif agenda[0] == "done!":
		#print "\nFinished!\n"
		print agenda[1][0]
		print "Finished in ",(time.time() - start_time)," seconds and ", numberofsteps, "steps."
		return numberofsteps
	else:
		print "Error: script terminated without either a complete grid, or concluding the puzzle is impossible."
		return -1


"""
Thoughts on the algorithm: at the moment, it's going to expand the least guessy option at each agenda. That means though that it will happily go back and expand options less
far along the path if they're less guessy. Is that an OK thing?
	Answer 14.3.16: well, it makes it take sodding ages for the empty grid. Maybe if I moved new leaves to the front of the agenda?
	Omg that's way faster!
	But it still doesn't like the empty grid. 
	
	What's going on here? When it has partially filled rows, it sees that the rest of the row is "easier" to fill and so will do that. 
	Let's try going depth first, by prioritising more filled grids. That's more in line with how I solve sudoku myself anyway.
	BEAUTIFUL now that works. I think I'm done here. 
	Let's write some comments.

"""