
from astar import AStar
from structs import Tile, TileContent
import sys
import math


class AStarSolver(AStar):

    def __init__(self, grid):
        self.grid = grid
        self.width = len(self.grid[0])
        self.height = len(self.grid)

    def heuristic_cost_estimate(self, n1, n2):
        """computes the 'direct' distance between two (x,y) tuples"""
        (x1, y1) = n1
        (x2, y2) = n2
        return math.hypot(x2 - x1, y2 - y1)

    def distance_between(self, n1, n2):
        """this method always returns 1, as two 'neighbors' are always adajcent"""
        return 1

    def neighbors(self, node):
        """ for a given coordinate in the maze, returns up to 4 adjacent(north,east,south,west)
            nodes that can be reached (=any adjacent coordinate that is an empty tile)
        """
        x, y = node
        nb = [(nx, ny) for nx, ny in [(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)] if 0 <= nx < self.width and 0 <= ny < self.height and self.grid[nx][ny].Content == TileContent.Empty]
        print('Neighbors: {}'.format(nb))
        return nb


if __name__ == "__main__":
    # create fake empty grid
    types = [TileContent.Empty for i in range(8)]
    for i in range(2):
        types.append(TileContent.Wall)

    def get_type():
       from random import randint
       return types[randint(0,9)]

    grid = [[Tile(get_type(), i, j) for i in range(20)] for j in range(20)]

    for i in range(20):
        line = ""
        for j in range(20):
            line += " "
            line += str(grid[i][j].Content)
        print(line)

    w = len(grid[0])
    h = len(grid)

    start = (1, 1)  # we choose to start at the upper left corner
    goal = (w - 2, h - 2)  # we want to reach the lower right corner

    # let's solve it
    foundPath = list(AStarSolver(grid).astar(start, goal))

    # print the solution
    if foundPath:
        print(list(foundPath))
    else:
        print('No solution')

