from queue import Queue, PriorityQueue
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any
import time

@dataclass(order=True)
class PrioritizedItem:
    priority: int
    item: Any=field(compare=False)

# helps find the inital starting position of the empty tile
def find_zero_index(puzzle):
    for r in range(len(puzzle)):
        for c in range(len(puzzle[r])):
            if puzzle[r][c] == 0:
                return (r, c)

# Prints puzzle state to terminal
def print_puzzle(puzzle):
    # b = '----------------'
    border = '----------------' * len(puzzle[0])
    print('\n'+border)
    for i in puzzle:
        print('|',end="\t")
        for j in i:
            if j == 0:
                print(" ",end="\t|\t")
            else:
                print(j,end="\t|\t")
        print('\n'+border)
    print()

# Node class for storing puzzle state, row and column for empty, weight and heuristic type, and parent node
class Node:
    def __init__(self,puzzle,r,c,w=0,h=0, parent="init"):
        self.puzzle = puzzle
        self.r = r
        self.c = c
        self.w = w
        self.h = h
        self.parent = parent
        # Misplaced Tiles
        if h == 1:
            self.f = self.w + self.misplaced()
        if h == 2:
            self.f = self.w + self.manhatten()
    
    # Calculates Heuristic for Misplaced Tiles
    def misplaced(self):
        puzzle = [i for j in self.puzzle for i in j]
        h = 0
        for i in range(1,len(puzzle)):
            if i != puzzle[i-1]:
                h+=1
        # if puzzle[-1] != 0:
        #     h+=1
        return h
    
    def manhatten(self):
        row_size = len(self.puzzle)
        col_size = len(self.puzzle[0])
        # heuristic cost
        h = 0
        for i in range(row_size):
            for j in range(col_size):
                val = self.puzzle[i][j]
                if val != 0:
                    actual_r = (val-1)//row_size
                    actual_c = (val-1)%col_size

                    h += (abs(i-actual_r) + abs(j-actual_c))
        
        return h

    # Generates string for current node state
    def gen_token(self):
        token = ''
        for i in self.puzzle:
            for j in i:
                token += str(j)
        
        return token
    
    # Checks if the puzzle is in complete state
    def check_goal(self):
        # Collapses puzzle from 2D to 1D
        puzzle = [i for j in self.puzzle for i in j]

        if puzzle[0] == 0:
            return False

        for i in range(1, len(puzzle)-1):
            if puzzle[i] < puzzle[i-1]:
                return False
        
        return True
    
    def make_moves(self):
        new_states = []
        # slide empty left
        if self.c > 0:
            new_puzzle = deepcopy(self.puzzle)
            new_puzzle[self.r][self.c],new_puzzle[self.r][self.c-1] = new_puzzle[self.r][self.c-1],new_puzzle[self.r][self.c]
            new_states.append(Node(new_puzzle,self.r,self.c-1,self.w+1,h=self.h,parent=self))
        #slide empty right
        if self.c < len(self.puzzle[0]) - 1:
            new_puzzle = deepcopy(self.puzzle)
            new_puzzle[self.r][self.c],new_puzzle[self.r][self.c+1] = new_puzzle[self.r][self.c+1],new_puzzle[self.r][self.c]
            new_states.append(Node(new_puzzle,self.r,self.c+1,self.w+1,h=self.h,parent=self))
        #slide empty up
        if self.r > 0:
            new_puzzle = deepcopy(self.puzzle)
            new_puzzle[self.r][self.c],new_puzzle[self.r-1][self.c] = new_puzzle[self.r-1][self.c],new_puzzle[self.r][self.c]
            new_states.append(Node(new_puzzle,self.r-1,self.c,self.w+1,h=self.h,parent=self))
        #slide empty down
        if self.r < len(self.puzzle) - 1:
            new_puzzle = deepcopy(self.puzzle)
            new_puzzle[self.r][self.c],new_puzzle[self.r+1][self.c] = new_puzzle[self.r+1][self.c],new_puzzle[self.r][self.c]
            new_states.append(Node(new_puzzle,self.r+1,self.c,self.w+1,h=self.h,parent=self))

        return new_states
        
def uniform_cost(init_node):
    nodes = Queue()
    nodes.put(init_node)
    repeats = set()
    repeats.add(init_node.gen_token())

    # checking
    max_q = 1
    expanded = 0

    while not nodes.empty():
        node = nodes.get()
        expanded += 1

        if node.check_goal():
            print(f"Max Queue: {max_q}\nExpanded Nodes: {expanded}")
            return node
        
        new_nodes = node.make_moves()
        for new_node in new_nodes:
            if new_node.gen_token() not in repeats:
                nodes.put(new_node)
                repeats.add(new_node.gen_token())

        if nodes.qsize() > max_q:
            max_q = nodes.qsize()

    print('No Solution')
    return None

def A_Star(init_node):
    nodes = PriorityQueue()
    nodes.put(PrioritizedItem(init_node.f,init_node))
    repeats = set()
    repeats.add(init_node.gen_token())

    # checking
    max_q = 1
    expanded = 0

    while nodes:
        node = nodes.get().item
        expanded += 1

        if node.check_goal():
            print(f"Max Queue: {max_q}\nExpanded Nodes: {expanded}")
            return node
        
        new_nodes = node.make_moves()
        for new_node in new_nodes:
            if new_node.gen_token() not in repeats:
                nodes.put(PrioritizedItem(new_node.f,new_node))
                repeats.add(new_node.gen_token())     
        
        if nodes.qsize() > max_q:
            max_q = nodes.qsize()

    print('No Solution')
    return None       

    
if __name__ == '__main__':
    print('Welcome to Sliding Puzzle Solver!\nPlease enter the puzzle state row-by-row.\nUse a zero to represent the Enter "q" when done.\n')
    
    init_puzzle = []
    
    while True:
        row = input()
        if row.lower() == 'q':
            break
        init_puzzle.append([int(i) for i in (row).split()])

    r,c = find_zero_index(init_puzzle)
    
    h = int(input('\nSelect Solver: 0 - Uniform Cost, 1 - Misplaced Tiles, 2 - Manhattan\n'))
    start_time = time.time()

    if h == 0:
        init_node = Node(init_puzzle,r,c,h=h)
        node = uniform_cost(init_node=init_node)
    else:
        init_node = Node(init_puzzle,r,c,h=h)
        node = A_Star(init_node)

    print(f'Elapsed Time: {time.time()-start_time}')
    

    solution = []

    depth = 0

    while node.parent != 'init':
        solution.append(node.puzzle)
        node = node.parent
        depth += 1

    print_puzzle(init_puzzle)
    for puzzle in reversed(solution):
        print_puzzle(puzzle)

    print(f"Depth: {depth}")