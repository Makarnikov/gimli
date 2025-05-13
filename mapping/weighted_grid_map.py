# weighted_grid_map.py

import numpy as np
from object_detection.danger_scores import get_danger_score
import os
import sys

# Bu satırlar gimli/ klasörünü sys.path'e ekler
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class WeightedGridMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width), dtype=float)

    def update_danger_zone(self, x, y, label):
        score = get_danger_score(label)
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] += score * 10
            self.grid[y][x] = min(self.grid[y][x], 100.0)

    def get_cost(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return float("inf")

    def print_grid(self):
        print(np.round(self.grid, 2))


if __name__ == "__main__":
    grid = WeightedGridMap(width=10, height=10)
    grid.update_danger_zone(3, 4, "knife")
    grid.update_danger_zone(5, 6, "toy")
    grid.print_grid()
