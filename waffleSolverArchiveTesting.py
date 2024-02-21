from waffleSolver import WaffleSolver
from allGrids import allGrids
import time

startTime = time.time()
failedGrids = []
for x, grid in enumerate(allGrids):
	if not (x + 1) % 100:
		print(f"Reached grid {x + 1} / {len(allGrids)}")

	solver = WaffleSolver(grid, "daily")
	solver.solve(False)

	if solver.failed:
		failedGrids.append(x)
		print(f"Failed grid {x + 1}, {solver.failed}")

totalTime = time.time() - startTime
print()
print(f"Took {round(totalTime, 3)} seconds to solve {len(allGrids)} Waffles")
print(f"Average solve time: {round(totalTime / len(allGrids), 3)} seconds")
print(f"Solved {len(allGrids) - len(failedGrids)} / {len(allGrids)}")
print(f"Solve rate: {round(100 * (len(allGrids) - len(failedGrids)) / len(allGrids), 3)} %")


# if True:
# 	failedGrids = [11, 37, 63, 73, 80, 82, 83, 84, 86, 92, 106, 118, 121, 133, 395]  # add 1 for actual name

# 	for x in failedGrids:
# 		print(x + 1)
# 		failedGrid = allGrids[x]

# 		solver = WaffleSolver(failedGrid, "daily")
# 		solver.solve(True)

# 		for s in solver.validSolutions:
# 			s.printGrid()


# Current Fails: 12, 38, 64, 74, 81, 83, 84, 85, 87, 93, 107, 119, 122, 134, 396 - (Subtract 1 for index in allGrids list)
# All of them create 2 solutions with very similar results (ie: adobe instead of abode)













