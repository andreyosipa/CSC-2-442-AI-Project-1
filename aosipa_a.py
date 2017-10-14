"""
CSC442 Project #1, Part A
Andrii Osipa
"""

import copy
import sys
import time
import random

class Node:
    """
        Attributes:
            value    : Ttt_state;
            children : list of Ttt_state;
            explored : T/F list of len = len(children)
            utils    : utilities of children
    """
    def __init__(self, value):
        self.value = value
        self.children = []
        self.utils = []

"""
    Descriptions:
    
TTT_state is list of 10 elements, where first 9 are cells of the field and 10th is result of the game.
Result takes values -2(not finished), -1(o wins), 0(draw), 1(x wins).

Whose turn to play can be find out by looking at sum(field[:9])%3.
"""

def turn(field):
    return ((sum(field[:9]) + 9) % 3) == 0

def find_result(field):
    if field[-1] == -2:
        for row in range(0,3):
            if (field[row*3] == field[row*3 + 1]) and (field[row*3 + 1] == field[row*3 + 2]) and (field[row*3] >= 0):
                field[-1] = (field[row*3]*2)-1
        for col in range(0,3):
            if (field[col] == field[col + 3]) and (field[col + 3] == field[col + 6]) and (field[col] >= 0):
                field[-1] = (field[col]*2)-1
        if (field[0] == field[4]) and (field[4] == field[8]) and (field[0] >= 0):
            field[-1] = (field[0]*2)-1
        if (field[2] == field[4]) and (field[4] == field[6]) and (field[2] >= 0):
            field[-1] = (field[2]*2)-1
        if field[-1] == -2 and sum(field[:9]) == 5:
            field[-1] = 0
    return field

def move(field, cell):
    if field[cell] == -1:
        field[cell] = int(turn(field))
        field = find_result(field)
    return field

def available_moves(field):
    ans = []
    for idx in range(9):
        if field[idx] == -1:
            ans.append(idx)
    return ans

def follow_tree(tree, move):
    new_value = copy.copy(tree.value)
    new_value[move] = turn(tree.value)
    new_value = find_result(new_value)
    for child in tree.children:
        if child.value == new_value:
            return child
    return Node(new_value)

def game():
    while 1:
        print >> sys.stderr, "player role?"
        s = raw_input()
        if s.lower() == "x":
            role = 0
        else:
            if s.lower() == "o":
                role = 1
            else:
                print >> sys.stderr, "wrong input" 
        start = [-1] * 10
        start[-1] = -2
        if role == 0:
            print >> sys.stderr, "your move?"
            move = int(input()) - 1
            if move < 0 or move > 8:
                print sys.stderr, "wrong move"
                return
            start[move] = 1
        game_tree = Node(start)
        while game_tree.value[-1] == -2:
            st = time.time()
            game_tree = game_dfs(game_tree, role)
            fi = time.time()
            print >> sys.stderr, "move done in: ", fi-st, "s"
            if game_tree.value[-1] > -2:
                break
            print >> sys.stderr, "your move?"
            move = int(input()) - 1
            if not move in available_moves(game_tree.value):
                print >> sys.stderr, "wrong move"
                return
            game_tree = follow_tree(game_tree, move)

        if game_tree.value[-1] == -1:
            print >> sys.stderr, "O wins"
        if game_tree.value[-1] == 1:
            print >> sys.stderr, "X wins"
        if game_tree.value[-1] == 0:
            print >> sys.stderr, "draw"

def game_dfs(tree, role):
    #Def. Perfect move - one that leads to 100% chance of victory.
    #role = who camputer plays for
    if tree.value[-1] == -2:
        #no one yet won the game
        best_move_idx = -1
        move_by = turn(tree.value)
        
        #check if there is already perfect move in precomputed ones
        child_idx = 0
        while best_move_idx == -1 and child_idx < len(tree.children):
            if tree.utils[child_idx] == move_by*2 - 1:
                best_move_idx = child_idx
            child_idx += 1
            
        #check if all moves are already precomputed
        if len(tree.utils) > 0 and sum(tree.utils) < 9 and best_move_idx == -1:
            if move_by == 0:
                best_move_idx = tree.utils.index(min(tree.utils))
            else:
                best_move_idx = tree.utils.index(max(tree.utils))
              
        #there are no children listed
        if len(tree.children) == 0:
            moves = available_moves(tree.value)
            random.shuffle(moves)
            for mov in moves:
                tree.children.append(Node(move(list(tree.value), mov)))
                tree.children[-1].value = find_result(tree.children[-1].value)
                tree.utils.append(100)
            
        #not all moves are precomputed and there is no "perfect" move. exploration
        child_idx = 0
        while child_idx < len(tree.children) and best_move_idx == -1:
            #unexplored child found
            if tree.utils[child_idx] > 2:
                tree.utils[child_idx] = dfs(tree.children[child_idx])
                if tree.utils[child_idx] == 2*role - 1:
                    best_move_idx = child_idx
            child_idx += 1
        
        #last case: no perfect moves. pick best available
        if best_move_idx == -1:
            if move_by == 0:
                best_move_idx = tree.utils.index(min(tree.utils))
            else:
                best_move_idx = tree.utils.index(max(tree.utils))
                
        print >> sys.stdout, diff(tree.children[best_move_idx], tree)
        #function returns new "current" game tree
        return tree.children[best_move_idx]

def diff(state1, state2):
    for i in range(9):
        if state1.value[i] != state2.value[i]:
            return i + 1

def dfs(tree):
    moves = available_moves(tree.value)
    random.shuffle(moves)
    for mov in moves:
        tree.children.append(Node(move(list(tree.value), mov)))
        tree.children[-1].value = find_result(tree.children[-1].value)
        if tree.children[-1].value[-1] == -2:
            tree.utils.append(100)
        else:
            tree.utils.append(tree.children[-1].value[-1])
            if tree.utils[-1] == turn(tree.value) * 2 - 1:
                return tree.utils[-1]
            
    for child_idx in range(len(moves)):
        if tree.children[child_idx].value[-1] == -2:
            tree.utils[child_idx] = dfs(tree.children[child_idx])
        if tree.utils[child_idx] == turn(tree.value) * 2 - 1:
            return tree.utils[child_idx]
    if turn(tree.value) == 0:
        return min(tree.utils)
    else:
        return max(tree.utils)

game()