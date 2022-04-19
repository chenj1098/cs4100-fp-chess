import json
import math
import random
from os.path import exists

from enums import Player
import constants

DIMENSION_ROW = constants.DIMENSION_ROW
DIMENSION_COL = constants.DIMENSION_COL


'''
an action is a tuple:
((start row, start col)), (end row, end col))

'''

def next_color(color):
    if color == "black":
        return "white"
    else:
        return "black"

class heuristic():
    def evaluate_board(self, game_state, max_color):
        raise Exception("evaluate_board not implemented")

class agent():
    def get_move(self, game_state, color):
        raise Exception("evaluate_board not implemented")
    def update(self, reward=0.0, file=None):
        pass

class q_agent(agent):
    def __init__(self, explore_rate = 0.5, learn_rate = 0.2, discount_factor = 0.8, file="q_agent"):
        # reading the data from the file
        if exists(file):
            print('loading file')
            with open(file) as f:
                data = f.read()
            f.close()
        else:
            data = "{}"
        
        self.explore_rate = explore_rate
        self.learn_rate = learn_rate
        self.discount_factor = discount_factor
        self.file = file
        self.q_values = json.loads(data)
        self.q_updates = []
    
    def get_q_val(self, game_state, move):
        return self.q_values.get(game_state.get_board_str() + str(move), 0.0)
    
    def get_best_move_and_val(self, game_state, color):
        moves = game_state.get_all_legal_moves(color)
        move = None
        val = -1000.0
        for m in moves:
            v = self.get_q_val(game_state, m)
            if v > val:
                move = m
                val = v
        return move, val

    def get_move(self, game_state, color):
        #print(game_state.get_board_str())
        move = None
        next_val = 0
        # explore
        if random.random() > self.explore_rate:
            moves = game_state.get_all_legal_moves(color)
            if moves:
                move = random.choice(moves)
                game_state.move_piece(move[0], move[1], True)
                next_val = self.get_best_move_and_val(game_state, color)[1]
                game_state.undo_move()

        # exploit
        else:
            move, _ = self.get_best_move_and_val(game_state, color)
            game_state.move_piece(move[0], move[1], True)
            next_val = self.get_best_move_and_val(game_state, color)[1]
            game_state.undo_move()
        
        # save values for q update step
        #print(next_val)
        self.q_updates.append((game_state.get_board_str(), move, next_val))
        return move

    def update(self, reward=0.0, file=None):
        #print(self.q_updates)
        for game_state_str, move, best_val in self.q_updates:
            v = self.q_values.get(game_state_str + str(move), 0.0)
            self.q_values[game_state_str + str(move)] = v + self.learn_rate * (reward + self.discount_factor * best_val - v)

        if file==None:
            file = self.file
        
        #print("writing file")
        with open(file, 'w') as f:
            f.write(json.dumps(self.q_values))
        f.close()

    

        


class moves_heuristic(heuristic):
    def evaluate_board(self, game_state, max_color):
        evaluation_score = 0
        for row in range(0, DIMENSION_ROW):
            for col in range(0, DIMENSION_COL):
                # print(row, col)
                if game_state.is_valid_piece(row, col):
                    evaluated_piece = game_state.get_piece(row, col)
                    if evaluated_piece.get_player() == max_color:
                        piece_moves = evaluated_piece.get_valid_piece_moves(game_state)
                        evaluation_score += len(piece_moves)
        return evaluation_score

class capture_heuristic(heuristic):
    def evaluate_board(self, game_state, max_color):
        evaluation_score = 0
        for row in range(0, DIMENSION_ROW):
            for col in range(0, DIMENSION_COL):
                # print(row, col)
                if game_state.is_valid_piece(row, col):
                    evaluated_piece = game_state.get_piece(row, col)
                    piece_takes = evaluated_piece.get_valid_piece_takes(game_state)

                    for end in piece_takes:
                        # add to eval score if we can threaten a capture, and subtract if opponent is threatening a capture
                        target_piece = game_state.get_piece(end[0], end[1])

                        target_piece_value = self.get_capture_value(target_piece, max_color) 

                        evaluation_score += target_piece_value

                    # piece evaluation as per normal, weighted by 2
                    evaluation_score += self.get_piece_value(evaluated_piece, max_color) * 2

        # print("evaluated board", evaluation_score)
        return evaluation_score

    def get_piece_value(self, piece, max_color):
        # print("found piece", piece.get_name(), piece.get_player())
        if piece.get_player() == max_color:
            if piece.get_name() is "k":
                return 1000
            elif piece.get_name() is "q":
                return 90
            elif piece.get_name() is "r":
                return 50
            elif piece.get_name() is "b":
                return 30
            elif piece.get_name() is "n":
                return 30
            elif piece.get_name() is "p":
                return 10
        else:
            if piece.get_name() is "k":
                return -1000
            elif piece.get_name() is "q":
                return -90
            elif piece.get_name() is "r":
                return -50
            elif piece.get_name() is "b":
                return -30
            elif piece.get_name() is "n":
                return -30
            elif piece.get_name() is "p":
                return -10 

    def get_capture_value(self, piece, max_color):
        # print("found piece", piece.get_name(), piece.get_player())
        if piece.get_player() == max_color:
            if piece.get_name() is "k":
                return -1000
            elif piece.get_name() is "q":
                return -90
            elif piece.get_name() is "r":
                return -50
            elif piece.get_name() is "b":
                return -30
            elif piece.get_name() is "n":
                return -30
            elif piece.get_name() is "p":
                return -10
        else:
            if piece.get_name() is "k":
                return 1000 * .1
            elif piece.get_name() is "q":
                return 90 * .1
            elif piece.get_name() is "r":
                return 50 * .1
            elif piece.get_name() is "b":
                return 30 * .1
            elif piece.get_name() is "n":
                return 30 * .1
            elif piece.get_name() is "p":
                return 10 * .1

class piece_squares_table_heuristic(heuristic):
    def __init__(self):
        self.pawn_table_8 = [
        0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5,  5, 10, 25, 25, 10,  5,  5,
        0,  0,  0, 20, 20,  0,  0,  0,
        5, -5,-10,  0,  0,-10, -5,  5,
        5, 10, 10,-20,-20, 10, 10,  5,
        0,  0,  0,  0,  0,  0,  0,  0]

        self.pawn_table_6x4 = [
        [50, 50, 50, 50],
        [30, 30, 25, 25],
        [10, 10, 10, 10],
        [5, 10, 10, 5],
        [5, 5, 5, 5],
        [0, 0, 0, 0]]
    
        self.knight_table_8 = [
        -50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -50,-40,-30,-30,-30,-30,-40,-50]

        self.knight_table_6x4 = [
        [0, 0, 0, 0],
        [0, 5, 5, 0],
        [0, 15, 15, 0],
        [0, 15, 15, 0],
        [0, 5,  5, 0],
        [-5,-5,-5,-5]]

        self.bishop_table_8 = [
        -20,-10,-10,-10,-10,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10, 10, 10, 10, 10, 10, 10,-10,
        -10,  5,  0,  0,  0,  0,  5,-10,
        -20,-10,-10,-10,-10,-10,-10,-20]
    
        self.bishop_table_6x4 = [
        [5, 10, 10, 5],
        [5, 10, 10, 5],
        [10, 10, 10, 10],
        [10, 10, 10, 10],
        [5, 10, 10, 5],
        [5, 10, 10, 5]]

        self.rook_table_8 = [
        0,  0,  0,  0,  0,  0,  0,  0,
        5, 10, 10, 10, 10, 10, 10,  5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        0,  0,  0,  5,  5,  0,  0,  0]

        self.rook_table_6x4 = [
        [0,  0,  0,  0],
        [5, 10, 10,  5],
        [5,  0, 0, 5],
        [5,  0, 0, 5],
        [5,  0, 0, 5],
        [0,  5,  5,  0]]

        self.queen_table_8 = [
        -20,-10,-10, -5, -5,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5,  5,  5,  5,  0,-10,
        -5,  0,  5,  5,  5,  5,  0, -5,
        0,  0,  5,  5,  5,  5,  0, -5,
        -10,  5,  5,  5,  5,  5,  0,-10,
        -10,  0,  5,  0,  0,  0,  0,-10,
        -20,-10,-10, -5, -5,-10,-10,-20]

        self.queen_table_6x4 = [
        [-20, -10, -10, -20],
        [-10,  0,  0, -10],
        [-10,  5,  5, -10],
        [-10,  5,  5, -10],
        [-10,  5,  5, -10],
        [-20,-10, -10,-20]]

        self.king_table_start_8 = [
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -20,-30,-30,-40,-40,-30,-30,-20,
        -10,-20,-20,-20,-20,-20,-20,-10,
        20, 20,  0,  0,  0,  0, 20, 20,
        20, 30, 10,  0,  0, 10, 30, 20]


        self.king_table_start_6x4 = [
        [-30,-40,-40,-30],
        [-30,-40,-40,-30],
        [-30,-40,-40,-30],
        [-10,-20,-20,-10],
        [20, 10, 10, 20],
        [20, 30, 30, 20]]

        self.king_table_end_8 = [
        -50,-40,-30,-20,-20,-30,-40,-50,
        -30,-20,-10,  0,  0,-10,-20,-30,
        -30,-10, 20, 30, 30, 20,-10,-30,
        -30,-10, 30, 40, 40, 30,-10,-30,
        -30,-10, 30, 40, 40, 30,-10,-30,
        -30,-10, 20, 30, 30, 20,-10,-30,
        -30,-30,  0,  0,  0,  0,-30,-30,
        -50,-30,-30,-30,-30,-30,-30,-50]

        self.king_table_end_6x4 = [
        [-50,-30,-30,-50],
        [-30,-10,-10,-30],
        [-30,10,10,-30],
        [-30,10,10,-30],
        [-30,0,0,-30],
        [-50,-30,-30,-50]]

    def evaluate_board(self, game_state, max_color):
        evaluation_score = 0
        for row in range(0, DIMENSION_ROW):
            for col in range(0, DIMENSION_COL):
                # print(row, col)
                if game_state.is_valid_piece(row, col):
                    evaluated_piece = game_state.get_piece(row, col)
                    evaluation_score += self.get_piece_square_value(evaluated_piece, max_color) * 0.2 + self.get_piece_value(evaluated_piece, max_color)
        # print("evaluated board", evaluation_score)
        return evaluation_score

    def get_piece_square_value(self, piece, max_color):
        if piece.get_player() == max_color:
            # print("row " +  str(piece.get_row_number()))
            # print("col " +  str(piece.get_col_number()))
            if piece.get_name() is "k":
                return self.king_table_end_6x4[piece.get_row_number()][piece.get_col_number()]
            elif piece.get_name() is "q":
                return self.queen_table_6x4[piece.get_row_number()][piece.get_col_number()]
            elif piece.get_name() is "r":
                return self.rook_table_6x4[piece.get_row_number()][piece.get_col_number()]
            elif piece.get_name() is "b":
                return self.bishop_table_6x4[piece.get_row_number()][piece.get_col_number()]
            elif piece.get_name() is "n":
                return self.knight_table_6x4[piece.get_row_number()][piece.get_col_number()]
            elif piece.get_name() is "p":
                return self.pawn_table_6x4[piece.get_row_number()][piece.get_col_number()]
        else:
            # print("row " +  str(DIMENSION_ROW - piece.get_row_number()))
            # print("col " +  str(piece.get_col_number()))
            if piece.get_name() is "k":
                return -self.king_table_end_6x4[DIMENSION_ROW - piece.get_row_number() - 1][piece.get_col_number()]
            elif piece.get_name() is "q":
                return -self.queen_table_6x4[DIMENSION_ROW - piece.get_row_number() - 1][piece.get_col_number()]
            elif piece.get_name() is "r":
                return -self.rook_table_6x4[DIMENSION_ROW - piece.get_row_number() - 1][piece.get_col_number()]
            elif piece.get_name() is "b":
                return -self.bishop_table_6x4[DIMENSION_ROW - piece.get_row_number() - 1][piece.get_col_number()]
            elif piece.get_name() is "n":
                return -self.knight_table_6x4[DIMENSION_ROW - piece.get_row_number() - 1][piece.get_col_number()]
            elif piece.get_name() is "p":
                return -self.pawn_table_6x4[DIMENSION_ROW - piece.get_row_number() - 1][piece.get_col_number()]

    def get_piece_value(self, piece, max_color):
        # print("found piece", piece.get_name(), piece.get_player())
        if piece.get_player() == max_color:
            if piece.get_name() is "k":
                return 1000
            elif piece.get_name() is "q":
                return 100
            elif piece.get_name() is "r":
                return 50
            elif piece.get_name() is "b":
                return 30
            elif piece.get_name() is "n":
                return 30
            elif piece.get_name() is "p":
                return 10
        else:
            if piece.get_name() is "k":
                return -1000
            elif piece.get_name() is "q":
                return -100
            elif piece.get_name() is "r":
                return -50
            elif piece.get_name() is "b":
                return -30
            elif piece.get_name() is "n":
                return -30
            elif piece.get_name() is "p":
                return -10
    


class piece_value_heuristic(heuristic):
    def evaluate_board(self, game_state, max_color):
        evaluation_score = 0
        for row in range(0, DIMENSION_ROW):
            for col in range(0, DIMENSION_COL):
                # print(row, col)
                if game_state.is_valid_piece(row, col):
                    evaluated_piece = game_state.get_piece(row, col)
                    evaluation_score += self.get_piece_value(evaluated_piece, max_color)
        # print("evaluated board", evaluation_score)
        return evaluation_score

    def get_piece_value(self, piece, max_color):
        # print("found piece", piece.get_name(), piece.get_player())
        if piece.get_player() == max_color:
            if piece.get_name() is "k":
                return 1000
            elif piece.get_name() is "q":
                return 100
            elif piece.get_name() is "r":
                return 50
            elif piece.get_name() is "b":
                return 30
            elif piece.get_name() is "n":
                return 30
            elif piece.get_name() is "p":
                return 10
        else:
            if piece.get_name() is "k":
                return -1000
            elif piece.get_name() is "q":
                return -100
            elif piece.get_name() is "r":
                return -50
            elif piece.get_name() is "b":
                return -30
            elif piece.get_name() is "n":
                return -30
            elif piece.get_name() is "p":
                return -10 

class random_agent(agent):
    def get_move(self, game_state, color):
        actions = game_state.get_all_legal_moves(color)
        return random.choice(actions)

class minimax_alpha_beta_agent(agent):
    def __init__(self, depth=3, alpha=-100000, beta=100000, heuristic=piece_value_heuristic()):
        self.depth = depth
        self.alpha = alpha
        self.beta = beta
        self.heuristic = heuristic

    def get_move(self, game_state, color):
        '''
        gets the best move according to the chess engine we implemented

        returns ((start row, start col)), (end row, end col))
        '''
        val, action = self.val_ab(game_state, color, color, self.depth, self.alpha, self.beta)
        # print("this turn is:", color)
        # print("best val", val)
        # print("white evaluation", self.heuristic.evaluate_board(game_state, "white"))
        # print("black evaluation", self.heuristic.evaluate_board(game_state, "black"))
        return action
    
    def val_ab(self, game_state, color, max_color, depth, alpha, beta):
        csc = game_state.checkmate_stalemate_checker()
        if csc == 0: # white lost
            if max_color == "white":
                return -5000000, None
            if max_color == "black":
                return 5000000, None
        elif csc == 1: # black lost
            if max_color == "white":
                return 5000000, None
            if max_color == "black":
                return -5000000, None
        elif csc == 2: # tie
            return 100, None

        if depth == 0:
            return self.heuristic.evaluate_board(game_state, max_color), None

        if color == max_color:
            return self.max_val(game_state, color, max_color, depth, alpha, beta)
        else:
            return self.min_val(game_state, color, max_color, depth, alpha, beta)

    # max val returns (value, action)
    def max_val(self, game_state, color, max_color, depth, alpha, beta):
        value = -math.inf
        actions = game_state.get_all_legal_moves(color)
        action = None
        alp = alpha
        bet = beta
        for a in actions:
            game_state.move_piece(a[0], a[1], True)
            v = self.val_ab(game_state, next_color(color), max_color, depth - 1, alpha, beta)[0]
            game_state.undo_move()

            if v > value:
                value = v
                action = a

            if value > bet:
                return value, action

            alp = max(alp, value)

        return value, action
    
    def min_val(self, game_state, color, max_color, depth, alpha, beta):
        value = math.inf
        actions = game_state.get_all_legal_moves(color)
        action = None
        alp = alpha
        bet = beta
        for a in actions:
            game_state.move_piece(a[0], a[1], True)
            v = self.val_ab(game_state, next_color(color), max_color, depth - 1, alpha, beta)[0]
            game_state.undo_move()

            if v < value:
                value = v
                action = a

            if value < alp:
                return value, action

            bet = min(bet, value)

        return value, action
