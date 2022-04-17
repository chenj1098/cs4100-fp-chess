import math
import random
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
    def get_move(self, game_state, color, max_color):
        raise Exception("evaluate_board not implemented")

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
        print("this turn is:", color)
        print("best val", val)
        print("white evaluation", self.heuristic.evaluate_board(game_state, "white"))
        print("black evaluation", self.heuristic.evaluate_board(game_state, "black"))
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
