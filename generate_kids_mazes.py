#!/usr/bin/env python3
"""
generate_kids_mazes.py

Generates 6 kid-friendly mazes (2 easy, 2 medium, 2 hard) and their solution images.
All output images are written to the /mazes_output folder in the repository root.
"""
from __future__ import annotations

import os
import random
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from PIL import Image, ImageDraw

Cell = Tuple[int, int]


@dataclass
class Maze:
    width: int
    height: int
    cells: Dict[Cell, Dict[str, bool]]

    @classmethod
    def create(cls, width: int, height: int) -> "Maze":
        # Initialize all walls present for every cell
        cells = {}
        for x in range(width):
            for y in range(height):
                cells[(x, y)] = {"N": True, "S": True, "E": True, "W": True}
        m = cls(width=width, height=height, cells=cells)
        m._generate()
        return m

    def _generate(self) -> None:
        # Iterative recursive backtracker
        start = (0, 0)
        stack: List[Cell] = [start]
        visited = {start}
        while stack:
            current = stack[-1]
            neighbors = []
            x, y = current
            cand = [((x, y - 1), "N", "S"), ((x, y + 1), "S", "N"),
                    ((x + 1, y), "E", "W"), ((x - 1, y), "W", "E")]
            for (nx, ny), dir_from_cur, dir_from_nb in cand:
                if 0 <= nx < self.width and 0 <= ny < self.height and (nx, ny) not in visited:
                    neighbors.append(((nx, ny), dir_from_cur, dir_from_nb))
            if neighbors:
                (nx, ny), dcur, dnb = random.choice(neighbors)
                # Knock down walls between current and neighbor
                self.cells[current][dcur] = False
                self.cells[(nx, ny)][dnb] = False
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()

    def neighbors_open(self, cell: Cell) -> List[Cell]:
        x, y = cell
        res: List[Cell] = []
        if not self.cells[cell]["N"] and y - 1 >= 0:
            res.append((x, y - 1))
        if not self.cells[cell]["S"] and y + 1 < self.height:
            res.append((x, y + 1))
        if not self.cells[cell]["E"] and x + 1 < self.width:
            res.append((x + 1, y))
        if not self.cells[cell]["W"] and x - 1 >= 0:
            res.append((x - 1, y))
        return res

    def solve_bfs(self, start: Cell = (0, 0), goal: Optional[Cell] = None) -> List[Cell]:
        if goal is None:
            goal = (self.width - 1, self.height - 1)
        queue = deque([start])
        came_from: Dict[Cell, Optional[Cell]] = {start: None}
        while queue:
            cur = queue.popleft()
            if cur == goal:
                break
            for nb in self.neighbors_open(cur):
                if nb not in came_from:
                    came_from[nb] = cur
                    queue.append(nb)
        # Reconstruct path
        path: List[Cell] = []
        cur: Optional[Cell] = goal
        while cur is not None:
            path.append(cur)
            cur = came_from.get(cur)
        path.reverse()
        return path


def draw_maze(maze: Maze, cell_px: int = 30, wall_px: int = 2) -> Image.Image:
    img_w = maze.width * cell_px + wall_px
    img_h = maze.height * cell_px + wall_px
    img = Image.new("RGB", (img_w, img_h), "white")
    draw = ImageDraw.Draw(img)

    # Draw walls
    for x in range(maze.width):
        for y in range(maze.height):
            cx = x * cell_px
            cy = y * cell_px
            cell = (x, y)
            if maze.cells[cell]["N"]:
                draw.line([(cx, cy), (cx + cell_px, cy)], fill="black", width=wall_px)
            if maze.cells[cell]["S"]:
                draw.line([(cx, cy + cell_px), (cx + cell_px, cy + cell_px)], fill="black", width=wall_px)
            if maze.cells[cell]["W"]:
                draw.line([(cx, cy), (cx, cy + cell_px)], fill="black", width=wall_px)
            if maze.cells[cell]["E"]:
                draw.line([(cx + cell_px, cy), (cx + cell_px, cy + cell_px)], fill="black", width=wall_px)
    
    # Add start marker (green dot at top-left)
    start_x, start_y = cell_px // 2, cell_px // 2
    radius = max(4, cell_px // 6)
    draw.ellipse([(start_x - radius, start_y - radius), (start_x + radius, start_y + radius)], 
                 fill="green", outline="black", width=2)
    
    # Add end marker (red star at bottom-right)
    end_x = (maze.width - 1) * cell_px + cell_px // 2
    end_y = (maze.height - 1) * cell_px + cell_px // 2
    draw.ellipse([(end_x - radius, end_y - radius), (end_x + radius, end_y + radius)], 
                 fill="red", outline="black", width=2)
    
    return img


def draw_solution_on_maze(base_img: Image.Image, maze: Maze, path: List[Cell], cell_px: int = 30,
                          wall_px: int = 2) -> Image.Image:
    img = base_img.copy()
    draw = ImageDraw.Draw(img)

    # Draw path as a thick blue line through centers
    centers = []
    for x, y in path:
        cx = x * cell_px + cell_px // 2
        cy = y * cell_px + cell_px // 2
        centers.append((cx, cy))
    if len(centers) >= 2:
        draw.line(centers, fill="blue", width=max(3, cell_px // 6))
    # Draw start and end markers
    if centers:
        r = max(4, cell_px // 6)
        draw.ellipse([(centers[0][0] - r, centers[0][1] - r), (centers[0][0] + r, centers[0][1] + r)],
                     fill="green", outline=None)
        draw.ellipse([(centers[-1][0] - r, centers[-1][1] - r), (centers[-1][0] + r, centers[-1][1] + r)],
                     fill="red", outline=None)
    return img


def ensure_output_dir(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def generate_and_save(output_dir: str) -> None:
    ensure_output_dir(output_dir)

    specs = [
        ("easy", 10, 10, 40),   # 2 easy mazes: 10x10, larger cells for clarity
        ("easy", 10, 10, 40),
        ("medium", 20, 20, 28),  # 2 medium: 20x20
        ("medium", 20, 20, 28),
        ("hard", 30, 30, 18),   # 2 hard: 30x30, smaller cells
        ("hard", 30, 30, 18),
    ]

    counters = {"easy": 0, "medium": 0, "hard": 0}
    for difficulty, w, h, cell_px in specs:
        counters[difficulty] += 1
        idx = counters[difficulty]
        maze = Maze.create(w, h)
        base_img = draw_maze(maze, cell_px=cell_px, wall_px=max(2, cell_px // 20))
        path = maze.solve_bfs()
        sol_img = draw_solution_on_maze(base_img, maze, path, cell_px=cell_px)

        maze_name = f"maze_{difficulty}_{idx}.png"
        sol_name = f"maze_{difficulty}_{idx}_solution.png"
        base_path = os.path.join(output_dir, maze_name)
        sol_path = os.path.join(output_dir, sol_name)
        base_img.save(base_path, format="PNG")
        sol_img.save(sol_path, format="PNG")
        # Keep this short and kid-friendly: ensure images are viewable
        # No console extraneous output


def main() -> None:
    repo_root = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(repo_root, "mazes_output")
    generate_and_save(output_dir)


if __name__ == "__main__":
    main()


    # --- add this helper near the top of your script ---
from PIL import Image, ImageDraw, ImageFont

def _load_font(px=28):
    # Try a clean sans font if Codespaces has it; fall back to PIL default
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", px)
    except:
        return ImageFont.load_default()

def label_start_finish(png_path, put_finish=True):
    """Write START (top-left) and FINISH (bottom-right) inside the border."""
    img = Image.open(png_path).convert("RGB")
    w, h = img.size
    draw = ImageDraw.Draw(img)
    font = _load_font(px=max(24, int(min(w, h) * 0.035)))  # scale with image size

    # Positions with a bit of padding from edges
    pad = int(min(w, h) * 0.025)
    start_xy  = (pad, pad)  # near top-left
    # place finish a little above/right of bottom-right corner
    finish_xy = (w - pad - 6*font.size//2, h - pad - font.size - 2)

    # Text outline for print clarity
    def draw_label(xy, text):
        x, y = xy
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)]:
            draw.text((x+dx, y+dy), text, font=font, fill=(255,255,255))
        draw.text((x, y), text, font=font, fill=(0,0,0))

    draw_label(start_xy, "START")
    if put_finish:
        draw_label(finish_xy, "FINISH")

    img.save(png_path, dpi=(300,300))
