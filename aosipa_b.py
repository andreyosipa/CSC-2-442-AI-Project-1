"""
CSC442 Project #1, Part B
Andrii Osipa
"""

import copy
import random
import time
import sys

"""
Game state is the following:
    field: 3x3x9 array
    result: value in {-2,-1,0,1}
    f_move: #s of fields where current move must be done
"""

def minimum(x, ignore_vals=[-2,2]):
    tmp = [a for a in x if not a in ignore_vals]
    if len(tmp) > 0:
        return min(tmp)
    return None

def maximum(x, ignore_vals=[-2,2]):
    tmp = [a for a in x if not a in ignore_vals]
    if len(tmp) > 0:
        return max(tmp)
    return None

class Game_state:
    def __init__(self, orig=None):
        if orig is None:
            self.non_copy_constructor()
        else:
            self.copy_constructor(orig)
            
    def non_copy_constructor(self):
        self.field =  [[-1 for i in xrange(9)] for j in xrange(9)]
        self.result = -2
        self.f_move = range(9)
    
    def copy_constructor(self, orig):
        self.field = copy.deepcopy(orig.field)
        self.result = orig.result
        self.f_move = orig.f_move
        
    def available_moves(self):
        result = []
        for f in self.f_move:
            for idx in range(9):
                if self.field[f][idx] == -1:
                    result.append((f, idx))
        if len(result) == 0 and self.result == -2:
            self.f_move = range(9)
            result = self.available_moves()
        return result
    
    def move(self, m):
        res = Game_state(self)
        res.field[m[0]][m[1]] = self.turn()
        res.f_move = list([m[1]])
        res.result = res.comp_result()
        return res
        
    def turn(self):
        return int((sum([sum(x) for x in self.field]) + 81 ) % 3 == 0)
    
    def comp_result(self):
        if self.result == -2:
            for f in range(0,9):
                for row in range(0,3):
                    if (self.field[f][row*3] == self.field[f][row*3 + 1]) and (self.field[f][row*3 + 1] == self.field[f][row*3 + 2]) and (self.field[f][row*3] >= 0):
                        return (self.field[f][row*3]*2)-1
                for col in range(0,3):
                    if (self.field[f][col] == self.field[f][col + 3]) and (self.field[f][col + 3] == self.field[f][col + 6]) and (self.field[f][col] >= 0):
                        return (self.field[f][col]*2)-1
                if (self.field[f][0] == self.field[f][4]) and (self.field[f][4] == self.field[f][8]) and (self.field[f][0] >= 0):
                    return (self.field[f][0]*2)-1
                if (self.field[f][2] == self.field[f][4]) and (self.field[f][4] == self.field[f][6]) and (self.field[f][2] >= 0):
                    return (self.field[f][2]*2)-1
            if sum([sum(x) for x in self.field]) == 41:
                return 0 
        return self.result
    
    def print_move(self, field):
        for f in range(9):
            for idx in range(9):
                if self.field[f][idx] != field[f][idx]:
                    print >> sys.stdout, f+1, idx+1
                    return
    
    def controlled_by(self, f, role):
        res = 0
        for row in range(0,3):
            if ((self.field[f][row*3] == role and self.field[f][row*3 + 1] == role and self.field[f][row*3 + 2] == -1) or 
               (self.field[f][row*3] == role and self.field[f][row*3 + 1] == -1 and self.field[f][row*3 + 2] == role) or
               (self.field[f][row*3] == -1 and self.field[f][row*3 + 1] == role and self.field[f][row*3 + 2] == role)):
                return 1
            if ((self.field[f][row] == role and self.field[f][row + 3] == role and self.field[f][row + 6] == -1) or 
               (self.field[f][row] == role and self.field[f][row + 3] == -1 and self.field[f][row + 6] == role) or
               (self.field[f][row] == -1 and self.field[f][row + 3] == role and self.field[f][row + 6] == role)):
                return 1
        if ((self.field[f][0] == role and self.field[f][4] == role and self.field[f][8] == -1) or 
            (self.field[f][0] == role and self.field[f][4] == -1 and self.field[f][8] == role) or
            (self.field[f][0] == -1 and self.field[f][4] == role and self.field[f][8] == role)):
            #res += 1
            return 1
        if ((self.field[f][2] == role and self.field[f][4] == role and self.field[f][6] == -1) or 
            (self.field[f][2] == role and self.field[f][4] == -1 and self.field[f][6] == role) or
            (self.field[f][2] == -1 and self.field[f][4] == role and self.field[f][6] == role)):
            return 1
        return 0
    
    def score(self):
        prev_turn = int(not self.turn())
        if self.result != -2:
            return self.result, self.result
        result = 0
        for f in range(9):
            result = result + 0.1 * self.controlled_by(f, 1) - 0.1 * self.controlled_by(f, 0)
        return result, result
        
    def equal(self, gs):
        return self.field == gs.field

class Node:
    def __init__(self, value):
        self.value = value
        self.children = []
        #alpha and beta for pruning. Initial assumption: everything is possible.
        if value.result == -2:
            self.alpha = -2
            self.beta = 2
        else:
            self.alpha = value.result
            self.beta = value.result

def dfs(tree, alpha, beta, depth, depth_bound = 3):
    global cutoffs

    if tree.value.result != -2:
        return tree.value.result, tree.value.result
    
    t = tree.value.turn()
    
    if depth < depth_bound:
        moves = tree.value.available_moves()
        random.shuffle(moves)
        for mov in moves:
            tree.children.append(Node(tree.value.move(mov)))
            
        for idx in range(len(tree.children)):
            tree.children[idx].alpha = -2
            tree.children[idx].beta = 2
            a,b = dfs(tree.children[idx], tree.alpha, tree.beta, depth + 1, depth_bound=depth_bound)
            tree.children[idx].alpha = a
            tree.children[idx].beta = b
            if t == 0:
                tree.beta = minimum([tree.beta, b])
            else:
                tree.alpha = maximum([tree.alpha, a])
            if t == 0 and tree.beta < alpha:
                cutoffs += 1
                return tree.alpha, tree.beta
            if t == 1 and beta < tree.alpha:
                cutoffs += 1
                return tree.alpha, tree.beta
            
        #computation of alpha/beta after everything is explored
        if t == 0:
            tree.alpha = tree.beta
        else:
            tree.beta = tree.alpha
        
        return tree.alpha, tree.beta
    else:
        return tree.value.score()

def game_dfs(tree, role, dfs_depth):
    if tree.value.result == -2:
        best_move_idx = -1
        move_by = tree.value.turn()
        
        tree.children = []
        
        tree.alpha = -2
        tree.beta = 2

        a, b = dfs(tree, -2, 2, 0, depth_bound=dfs_depth)

        tree.alpha = a
        tree.beta = b
        
        alphas = []
        betas = []
        for idx in range(len(tree.children)):
            alphas.append(tree.children[idx].alpha)
            betas.append(tree.children[idx].beta)
        
        if move_by == 0:
            best_move_idx = betas.index(minimum(betas))
        else:
            best_move_idx = alphas.index(maximum(alphas))
                
        #function returns new "current" game tree
        tree.value.print_move(tree.children[best_move_idx].value.field)
        return tree.children[best_move_idx]

def game():
    while 2:
        times = []

        print >> sys.stderr, "player role?"
        role = raw_input()
        if role.lower() == "x":
            role = 0
        else:
            if role.lower() == "o":
                role = 1
            else:
                print >> sys.stderr, "Wrong input"
                return

        start = Game_state()
        step = 0

        if role == 0:
            print >> sys.stderr, "your move?"
            mov = raw_input().split(' ')
            mov = (int(mov[0]) - 1, int(mov[1]) - 1)
            if mov[0] < 0 or mov[0] > 8 or mov[1] < 0 or mov[1] > 8:
                return "Wrong move"
            start = start.move(mov)
            step += 1

        game_tree = Node(start)
        while game_tree.value.result == -2:
            
            #statistics parameters
            global cutoffs
            cutoffs = 0
            st = time.time()

            game_tree = game_dfs(game_tree, role, depth_func(step))  

            fi = time.time()
            print >> sys.stderr, "Statistics:"
            print >> sys.stderr, "search took ", fi-st, "s"
            print >> sys.stderr, "# cutted branches: ", cutoffs

            step += 1
            if game_tree.value.result > -2:
                break
            print >> sys.stderr, "your move?"
            mov = raw_input().split(' ')
            mov = (int(mov[0]) - 1, int(mov[1]) - 1)
            if not mov in game_tree.value.available_moves():
                print >> sys.stderr, "Wrong move"
                return
            game_tree = Node(game_tree.value.move(mov))
            step += 1
        if game_tree.value.result == 1:
            print >> sys.stderr, "X wins"
        else:
            if game_tree.value.result == -1:
                print >> sys.stderr, "O wins"
            else:
                print sys.stderr, "draw"

def depth_func(x):
    if x == 0:
        return 1
    if x < 30:
        return 3
    if x >= 30:
        return 4

cutoffs = 0
game()