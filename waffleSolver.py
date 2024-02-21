from words import words, weird
from time import time
import re
import sys

words.extend(weird)

class WaffleSolver():
	def __init__(self, grid, size):
		self.possibleSolutions = []
		self.validSolutions = []

		if size == "daily":
			self.conversions = {
				(2, 0): ((0, 0), (1, 0), (3, 0), (4, 0), (2, 1), (2, 2), (2, 3), (2, 4)),
				(0, 2): ((0, 0), (0, 1), (1, 2), (2, 2), (3, 2), (4, 2), (0, 3), (0, 4)),
				(4, 2): ((4, 0), (4, 1), (0, 2), (1, 2), (2, 2), (3, 2), (4, 3), (4, 4)),
				(2, 4): ((2, 0), (2, 1), (2, 2), (2, 3), (0, 4), (1, 4), (3, 4), (4, 4))
					}

		self.board = Board(grid)
		self.getPossibleWordsLists()  # gets a self.possibleWordsLists variable for optimization

		self.allSwaps = []  # [[((swapIndex1), (swapIndex2)), ... ], ... ]
		self.swaps = []
		self.nextSwaps = {}  # {simpleGrid: ((swapIndex1), (swapIndex2)), ... 

		self.failed = False


	def getPossibleWordsLists(self):
		self.possibleWordsLists = []
		for word in range(6):
			self.possibleWordsLists.append(self.board.getPossibleWords(word, words, True))


	def specialMin(self, allPossibleWords):
		started = False
		for x, row in enumerate(allPossibleWords):
			if not row:
				continue  # already solved this row

			if not started:
				minValue = (len(row), x)
				started = True

			else:
				if (newValue := len(row)) < minValue[0]:
					minValue = (newValue, x)

		return minValue[1]


	def partialSolve(self, board):
		# find the minimum of the directions left of the words
		# if there are no words:
		# return False
		# make a copy of the board
		# input the word
		# if there are no directions left:
		# return board
		# recurse

		allPossibleWords = []

		for word in range(6):
			if board.solvedDirections[word]:
				allPossibleWords.append(0)
				continue  # already inputted the word

			possibleWords = board.getPossibleWords(word, self.possibleWordsLists[word])

			if not len(possibleWords):
				return False  # no solutions

			allPossibleWords.append(possibleWords)

		nextWord = self.specialMin(allPossibleWords)

		board.solvedDirections[nextWord] = True

		for possibleWord in allPossibleWords[nextWord]:
			testBoard = board.copy()
			testBoard.inputWord(possibleWord, nextWord)

			if all(testBoard.solvedDirections):
				self.possibleSolutions.append(testBoard)

			else:  # continue the recursion
				self.partialSolve(testBoard)


	def findValidSolutions(self):
		self.partialSolve(self.board)

		# finds the yellows at intersections and what indexes could possibly have that character at the end

		intersectionYellows = {}

		for intersection in [(2, 0), (0, 2), (4, 2), (2, 4)]:
			letterInfo = self.board.grid[intersection[1]][intersection[0]]
			if letterInfo[1] != 1:
				continue

			intersectionYellows[intersection] = (letterInfo[0], [])
			for gridSpot in self.conversions[intersection]:
				if self.board.grid[gridSpot[1]][gridSpot[0]][1] < 2:
					intersectionYellows[intersection][1].append(gridSpot)

		for solution in self.possibleSolutions:
			for yellow, yellowInfo in intersectionYellows.items():
				letter, spots = yellowInfo

				if letter not in [solution.grid[spot[1]][spot[0]][0] for spot in spots]:
					break

			else:
				self.validSolutions.append(solution)


	def getSwapsPartial(self, board, swaps = []):
		# deals with a self.swaps dictionary
		# another recursive strategy

		# for each letter in the board:
		# create a copy of the board for each possible swap
		# find the solution for the board copies

		swapped = False
		for y, row in enumerate(board.grid):
			if swapped:
				break

			for x, letterInfo in enumerate(row):
				if letterInfo[1] > 1:
					continue

				# swap the letters in the testBoard

				finalLetter = self.solution.grid[y][x][0]

				spots = board.findAll(finalLetter)
				for n, spot in enumerate(spots):

					testBoard = board.copy()
					testSwaps = swaps.copy()

					testSwaps.append(((x, y), (spot)))

					if letterInfo[0] == self.solution.grid[spot[1]][spot[0]][0]:
						testBoard.grid[spot[1]][spot[0]] = (letterInfo[0], 2)

					else:
						testBoard.grid[spot[1]][spot[0]] = (letterInfo[0], 0)  # might not be accurate, but that does not matter

					testBoard.grid[y][x] = (finalLetter, 2)

					self.getSwapsPartial(testBoard, testSwaps)

				swapped = True
				break

		if not swapped:
			self.allSwaps.append(swaps)


	def getSwaps(self):
		self.getSwapsPartial(self.board)

		self.swaps = min(self.allSwaps, key = lambda x: len(x))

		# create a dictionary of {simpleGrid: nextSwap ... }

		testBoard = self.board.copy()
		for swap in self.swaps:
			self.nextSwaps[testBoard.getSimpleGrid()] = swap
			testBoard.grid[swap[0][1]][swap[0][0]], testBoard.grid[swap[1][1]][swap[1][0]] = testBoard.grid[swap[1][1]][swap[1][0]], testBoard.grid[swap[0][1]][swap[0][0]]


	def solve(self, printSolve = False):
		if printSolve:
			self.board.printGrid()

		self.findValidSolutions()

		if len(self.validSolutions) > 1:
			if printSolve:
				print("Failed, found multiple solutions")
			self.failed = "Error: Multiple Solutions"
			return

		if not len(self.validSolutions):
			if printSolve:
				print("Failed, found no solutions")
			self.failed = "Error: No Solutions"
			return

		self.solution = self.validSolutions[0]
		self.getSwaps()

		if len(self.swaps) != 10:
			if printSolve:
				print(f"Failed, solution takes {len(self.swaps)} swaps")
			self.failed = "Error: More than 10 swaps"

		if printSolve:
			print("Solution:")
			self.solution.printGrid()
			print(f"The solution takes {len(self.swaps)} swaps")
			for grid, swap in self.nextSwaps.items():
				self.printSimpleGrid(grid)
				print(swap)
			self.solution.printGrid()


	def printSimpleGrid(self, simpleGrid):
		print()
		for row in simpleGrid:
			for char in row:
				print(char.upper(), end = " ")
			print()
		print()


class Board():
	def __init__(self, grid, directions = False):
		self.grid = grid

		if directions:
			self.solvedDirections = directions
		else:
			self.solvedDirections = [False for _ in range(6)]

		self.getUnusedLetters()


	def getUnusedLetters(self):
		self.unusedLetters = []
		for row in self.grid:
			for letterInfo in row:
				if letterInfo[1] < 2:
					self.unusedLetters.append(letterInfo[0])


	def getGridLine(self, wordIndex):
		if wordIndex < 3:
			gridLine = self.grid[wordIndex * 2]
		else:
			gridLine = [row[(wordIndex - 3) * 2] for row in self.grid]

		return gridLine


	def findAll(self, letter):
		spots = []
		for y, row in enumerate(self.grid):
			for x, letterInfo in enumerate(row):
				if letterInfo[1] > 1:
					continue

				if letterInfo[0] == letter:
					spots.append((x, y))

		return spots


	def specialFind(self, letter):
		for y, row in enumerate(self.grid):
			for x, letterInfo in enumerate(row):
				if letterInfo[1] > 1:
					continue

				if letterInfo[0] == letter:
					return (x, y)


	def getPossibleWords(self, wordIndex, possibleWordsList, firstTime = False):
		gridLine = self.getGridLine(wordIndex)

		pattern = ""
		otherLetters = "".join(set(self.unusedLetters))
		addedSpots = []
		for x, letterInfo in enumerate(gridLine):
			if letterInfo[1] == 2:
				pattern += letterInfo[0]
			else:
				addedSpots.append(x)
				pattern += f"[{otherLetters}]"

		testWords = [word for word in possibleWordsList if re.search(pattern, word)]
		finalWords = []

		for word in testWords:
			addedLetters = [word[x] for x in addedSpots]

			# check if the regex found words using more of a letter than it should have

			for char in addedLetters:
				if addedLetters.count(char) > self.unusedLetters.count(char):
					break

			else:
				finalWords.append(word)

		if not firstTime:
			return finalWords

		return self.firstTimeWordsFilter(finalWords, gridLine, addedSpots)


	def firstTimeWordsFilter(self, testWords, gridLine, addedSpots):
		# check if the word accounts for the original yellows and grays in the word

		# this code only needs to run the first time this function is called: when the grid is gathering the better lists of possible words
		# since the better lists will already guarantee that the yellows are correct

		# AKA: handles all the edge cases

		finalWords = []
		grays = {}
		allYellows = {}  # includes the intersection yellows for the purpose of determining what type of gray the grays are
		yellows = {}  # includes only yellows relevant to the word

		for x, letterInfo in enumerate(gridLine):
			if letterInfo[1] > 1:
				continue

			if letterInfo[1] == 0:
				if letterInfo[0] in grays:
					grays[letterInfo[0]].append(x)
				else:
					grays[letterInfo[0]] = [x]
				continue

			if letterInfo[0] in allYellows:
				allYellows[letterInfo[0]].append(x)
			else:
				allYellows[letterInfo[0]] = [x]

			if x in [0, 2, 4]:  # it is at an intersection of two words
				continue

			# add it to the yellows dict

			if letterInfo[0] in yellows:
				yellows[letterInfo[0]].append(x)
			else:
				yellows[letterInfo[0]] = [x]

		for word in testWords:
			stop = False

			addedLetters = [word[x] for x in addedSpots]

			for gray, spots in grays.items():
				if gray in allYellows:  # the letter could be in the added letters of the word word, just not at that spot
										# you can assume that there is no more than the len(allYellows[letter]) of the letter,
										# because if there was, the letter would be yellow

					if len(allYellows[gray]) < addedLetters.count(gray):
						stop = True
						break

					for spot in spots:
						if word[spot] == gray:
							stop = True
							break

					if stop:
						break

				else:  # the letter cannot be in the added letters of the word
					if gray in addedLetters:
						stop = True
						break

			if stop:
				continue


			# make sure the new letter is not in the same index of any of the yellows
			for yellow, yellowIndexes in allYellows.items():
				for index in yellowIndexes:
					if word[index] == yellow:
						stop = True
						break

			if stop:
				continue

			for yellow, yellowIndexes in yellows.items():
				if yellow in grays:  # there is an exact number of yellows, since there is a gray as well
					if len(allYellows[yellow]) != addedLetters.count(yellow):
						stop = True
						break

				if len(yellows[yellow]) > addedLetters.count(yellow):  # why not len(allYellows[yellow]) > addedLetters.count(yellow)
					stop = True
					break  # the yellow was not added / not enough yellows were added


			if not stop:
				finalWords.append(word)

		return finalWords


	def inputWord(self, word, wordIndex):
		# input the word into the (nextWord) row in the grid and return a grid object

		gridLine = self.getGridLine(wordIndex)

		for n, letterInfo in enumerate(gridLine):
			if letterInfo[1] == 2:
				continue

			letter = word[n]
			x, y = self.specialFind(letter)
			if wordIndex < 3:
				self.grid[2 * wordIndex][n], self.grid[y][x] = self.grid[y][x], self.grid[2 * wordIndex][n]
				self.grid[2 * wordIndex][n] = (self.grid[2 * wordIndex][n][0], 2)
			else:
				self.grid[n][2 * (wordIndex - 3)], self.grid[y][x] = self.grid[y][x], self.grid[n][2 * (wordIndex - 3)]
				self.grid[n][2 * (wordIndex - 3)] = (self.grid[n][2 * (wordIndex - 3)][0], 2)

		self.getUnusedLetters()


	def getSimpleGrid(self):
		# returns a grid of just characters, no info about color
		simpleGrid = []
		for row in self.grid:
			simpleGrid.append(tuple([letterInfo[0] for letterInfo in row]))

		return tuple(simpleGrid)


	def copy(self):
		return Board([row[:] for row in self.grid], self.solvedDirections.copy())


	def printGrid(self):
		print()
		for row in self.grid:
			for letter in row:
				print(letter[0].upper(), end = " ")
			print()
		print()

if __name__ == "__main__":
	sys.path.append('./Waffle Web Scraping')
	from waffleDailyScraping import getGridFromDaily
	
	try:
		todaysGrid = getGridFromDaily()

		solver = WaffleSolver(todaysGrid, "daily")
		solver.solve(True)
	except:
		print("Failed to connect")



















