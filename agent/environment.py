# agent/environment.py

"""
Módulo que define el entorno (Environment) para el robot aspiradora.
"""

import random
from typing import List, Tuple, Dict, Optional

EMPTY = "EMPTY"
WALL = "WALL"
DIRT = "DIRT"
BASE = "BASE"


class Environment:
    def __init__(
        self,
        rows: int = 8,
        cols: int = 8,
        obstacle_prob: float = 0.1,
        dirt_prob: float = 0.2,
    ) -> None:

        self.rows = rows
        self.cols = cols
        self.obstacle_prob = obstacle_prob
        self.dirt_prob = dirt_prob

        self.grid: List[List[str]] = []
        self.robot_row: int = 0
        self.robot_col: int = 0
        self.base_position: Tuple[int, int] = (0, 0)

        self.generate_random_map()

    # ------------------------------------------------------------------ MAPA

    def generate_random_map(self) -> None:
        self.grid = [[EMPTY for _ in range(self.cols)] for _ in range(self.rows)]

        # borde como pared
        for r in range(self.rows):
            for c in range(self.cols):
                if r == 0 or r == self.rows - 1 or c == 0 or c == self.cols - 1:
                    self.grid[r][c] = WALL

        # internos
        for r in range(1, self.rows - 1):
            for c in range(1, self.cols - 1):
                if random.random() < self.obstacle_prob:
                    self.grid[r][c] = WALL
                elif random.random() < self.dirt_prob:
                    self.grid[r][c] = DIRT
                else:
                    self.grid[r][c] = EMPTY

        # base
        self.base_position = self._get_random_free_cell()
        br, bc = self.base_position
        self.grid[br][bc] = BASE

        # robot
        self.robot_row, self.robot_col = self._get_random_free_cell(
            forbidden={self.base_position}
        )

    def _get_random_free_cell(
        self, forbidden: Optional[set] = None
    ) -> Tuple[int, int]:

        if forbidden is None:
            forbidden = set()

        free_cells = []
        for r in range(1, self.rows - 1):
            for c in range(1, self.cols - 1):
                if self.grid[r][c] != WALL and (r, c) not in forbidden:
                    free_cells.append((r, c))

        if not free_cells:
            return self.rows // 2, self.cols // 2

        return random.choice(free_cells)

    # -------------------------------------------------------------- CONSULTAS

    def is_inside(self, row: int, col: int) -> bool:
        return 0 <= row < self.rows and 0 <= col < self.cols

    def get_cell(self, row: int, col: int) -> str:
        if not self.is_inside(row, col):
            return WALL
        return self.grid[row][col]

    def is_obstacle(self, row: int, col: int) -> bool:
        """Solo las paredes son obstáculo físico."""
        return self.get_cell(row, col) == WALL

    def is_dirty(self, row: int, col: int) -> bool:
        return self.get_cell(row, col) == DIRT

    def is_base(self, row: int, col: int) -> bool:
        return self.get_cell(row, col) == BASE

    # ---------------------------------------------------------- SENSADO RELATIVO

    def sense_obstacles(self, orientation: str) -> Dict[str, bool]:
        row, col = self.robot_row, self.robot_col

        front_r, front_c = self._get_neighbor(row, col, orientation, "front")
        left_r, left_c = self._get_neighbor(row, col, orientation, "left")
        right_r, right_c = self._get_neighbor(row, col, orientation, "right")

        return {
            "front": self.is_obstacle(front_r, front_c),
            "left": self.is_obstacle(left_r, left_c),
            "right": self.is_obstacle(right_r, right_c),
        }

    def get_relative_cell_type(
        self, orientation: str, relative_direction: str
    ) -> str:
        """
        Devuelve el tipo de celda (EMPTY/WALL/DIRT/BASE) que hay
        frente/izquierda/derecha del robot según la orientación.
        """
        r, c = self.robot_row, self.robot_col
        nr, nc = self._get_neighbor(r, c, orientation, relative_direction)
        return self.get_cell(nr, nc)

    def _get_neighbor(
        self,
        row: int,
        col: int,
        orientation: str,
        relative_direction: str,
    ) -> Tuple[int, int]:

        directions = ["N", "E", "S", "W"]
        if orientation not in directions:
            return row, col

        idx = directions.index(orientation)

        if relative_direction == "front":
            dir_idx = idx
        elif relative_direction == "left":
            dir_idx = (idx - 1) % 4
        elif relative_direction == "right":
            dir_idx = (idx + 1) % 4
        else:
            dir_idx = idx

        dir_abs = directions[dir_idx]

        if dir_abs == "N":
            return row - 1, col
        if dir_abs == "S":
            return row + 1, col
        if dir_abs == "E":
            return row, col + 1
        if dir_abs == "W":
            return row, col - 1
        return row, col

    # -------------------------------------------------------- ACCIONES ENTORNO

    def clean_current_cell(self) -> None:
        r, c = self.robot_row, self.robot_col
        if self.grid[r][c] == DIRT:
            self.grid[r][c] = EMPTY

    def move_robot_forward(self, orientation: str) -> None:
        new_r, new_c = self._get_neighbor(self.robot_row, self.robot_col, orientation, "front")
        if not self.is_obstacle(new_r, new_c):
            self.robot_row, self.robot_col = new_r, new_c

    def set_robot_position(self, row: int, col: int) -> None:
        if not self.is_obstacle(row, col):
            self.robot_row = row
            self.robot_col = col

    def get_robot_position(self) -> Tuple[int, int]:
        return self.robot_row, self.robot_col

    def is_robot_on_base(self) -> bool:
        return (self.robot_row, self.robot_col) == self.base_position

    # ---------------------------------------------------------- ESTADÍSTICAS

    def count_dirty_cells(self) -> int:
        return sum(row.count(DIRT) for row in self.grid)

    def to_dict(self) -> Dict:
        return {
            "rows": self.rows,
            "cols": self.cols,
            "grid": self.grid,
            "robot_position": (self.robot_row, self.robot_col),
            "base_position": self.base_position,
            "dirty_cells": self.count_dirty_cells(),
        }
