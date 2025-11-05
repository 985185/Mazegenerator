#!/usr/bin/env python3
import sys
sys.path.append('/workspaces/Mazegenerator')

from src.maze_manager import MazeManager

# Create a simple maze to test the markers
manager = MazeManager()
maze = manager.add_maze(5, 5)  # Small maze for quick testing
manager.solve_maze(maze.id, "DepthFirstBacktracker")
manager.set_filename("test_maze")
manager.show_maze(maze.id)
print("Maze generated with visual markers - check test_maze_generation.png")