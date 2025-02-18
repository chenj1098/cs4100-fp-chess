#
# The GUI engine for Python Chess
#
# Author: Boo Sung Kim, Eddie Sharick
# Note: The pygame tutorial by Eddie Sharick was used for the GUI engine. The GUI code was altered by Boo Sung Kim to
# fit in with the rest of the project.
#
import chess_engine
import pygame as py
import constants
import ai_constants

import ai_engine
import custom_ai_engines
from enums import Player

"""Variables"""
WIDTH = HEIGHT = 512  # width and height of the chess board
#DIMENSION = 8
DIMENSION_ROW = constants.DIMENSION_ROW  # the dimensions of the chess board
DIMENSION_COL = constants.DIMENSION_COL  # the dimensions of the chess board
SQ_SIZE = HEIGHT // DIMENSION_ROW  # the size of each of the squares in the board
MAX_FPS = 15  # FPS for animations
IMAGES = {}  # images for the chess pieces
colors = [py.Color("white"), py.Color("gray")]

# TODO: AI black has been worked on. Mirror progress for other two modes
def load_images():
    '''
    Load images for the chess pieces
    '''
    for p in Player.PIECES:
        IMAGES[p] = py.transform.scale(py.image.load("images/" + p + ".png"), (SQ_SIZE, SQ_SIZE))


def draw_game_state(screen, game_state, valid_moves, square_selected):
    ''' Draw the complete chess board with pieces

    Keyword arguments:
        :param screen       -- the pygame screen
        :param game_state   -- the state of the current chess game
    '''
    draw_squares(screen)
    highlight_square(screen, game_state, valid_moves, square_selected)
    draw_pieces(screen, game_state)


def draw_squares(screen):
    ''' Draw the chess board with the alternating two colors

    :param screen:          -- the pygame screen
    '''
    for r in range(DIMENSION_ROW):
        for c in range(DIMENSION_COL):
            color = colors[(r + c) % 2]
            py.draw.rect(screen, color, py.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces(screen, game_state):
    ''' Draw the chess pieces onto the board

    :param screen:          -- the pygame screen
    :param game_state:      -- the current state of the chess game
    '''
    for r in range(DIMENSION_ROW):
        for c in range(DIMENSION_COL):
            piece = game_state.get_piece(r, c)
            if piece is not None and piece != Player.EMPTY:
                screen.blit(IMAGES[piece.get_player() + "_" + piece.get_name()],
                            py.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def highlight_square(screen, game_state, valid_moves, square_selected):
    if square_selected != () and game_state.is_valid_piece(square_selected[0], square_selected[1]):
        row = square_selected[0]
        col = square_selected[1]

        if (game_state.whose_turn() and game_state.get_piece(row, col).is_player(Player.PLAYER_1)) or \
                (not game_state.whose_turn() and game_state.get_piece(row, col).is_player(Player.PLAYER_2)):
            # hightlight selected square
            s = py.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(py.Color("blue"))
            screen.blit(s, (col * SQ_SIZE, row * SQ_SIZE))

            # highlight move squares
            s.fill(py.Color("green"))

            for move in valid_moves:
                screen.blit(s, (move[1] * SQ_SIZE, move[0] * SQ_SIZE))


def main():
    # Check for the number of players and the color of the AI
    cpu_player = []
    while True:
        try:
            number_of_players = input("How many players (0, 1 or 2)?\n")
            if int(number_of_players) == 1:
                number_of_players = 1
                while True:
                    human_player = input("What color do you want to play (w or b)?\n")
                    if human_player is "w":
                        cpu_player.append("b")
                        break
                    elif human_player is "b":
                        cpu_player.append("w")
                        break
                    else:
                        print("Enter w or b.\n")
                break
            elif int(number_of_players) == 2:
                number_of_players = 2
                break
            elif int(number_of_players) == 0:
                number_of_players = 0
                next_player = "w"
                cpu_player.append("w")
                cpu_player.append("b")
                break
            else:
                print("Enter 0, 1 or 2.\n")
        except ValueError:
            print("Enter 0, 1 or 2.")

    py.init()
    screen = py.display.set_mode((WIDTH, HEIGHT))
    clock = py.time.Clock()
    game_state = chess_engine.game_state()
    load_images()
    running = True
    square_selected = ()  # keeps track of the last selected square
    player_clicks = []  # keeps track of player clicks (two tuples)
    valid_moves = []
    game_over = False

    ai = ai_constants.AI1
    ai2 = ai_constants.AI2
    game_state = chess_engine.game_state()
    
    # run an ai game
    if number_of_players == 0:
        autoplay = input("Play automatically (0 or 1)?\n")
        if int(autoplay) == 1:
            autoplay = 1
        elif int(autoplay) == 0:
            autoplay = 0
        
        next_player = "w"
        
        if autoplay == 0:
            while running:
                for e in py.event.get():
                    if e.type == py.QUIT:
                        running = False
                    if e.type == py.MOUSEBUTTONDOWN and not game_over:
                        if next_player == "w":
                            ai_move = ai.get_move(game_state, Player.PLAYER_1)
                            game_state.move_piece(ai_move[0], ai_move[1], True)
                            next_player = "b"
                        elif next_player == "b":
                            ai_move = ai2.get_move(game_state, Player.PLAYER_2)
                            game_state.move_piece(ai_move[0], ai_move[1], True)
                            next_player = "w"

                draw_game_state(screen, game_state, valid_moves, square_selected)
                endgame = game_state.checkmate_stalemate_checker()
                if endgame == 0:
                    game_over = True
                    draw_text(screen, "Black wins.")
                elif endgame == 1:
                    game_over = True
                    draw_text(screen, "White wins.")
                elif endgame == 2:
                    game_over = True
                    draw_text(screen, "Stalemate.")

                clock.tick(MAX_FPS)
                py.display.flip()

        elif autoplay == 1:
            games = input("How many games?\n")
            games = int(games)
            for i in range(games):
                #print("game", i)
                turns = 0
                while running:
                    # quit
                    for e in py.event.get():
                        if e.type == py.QUIT:
                            running = False

                    if turns > 200:
                        game_over = True
                        print("game", i, endgame, "timeout in", turns, "turns")
                        break

                    # play game
                    if not game_over:
                        #print("turn", turns, "player", next_player)
                        if next_player == "w":
                            ai_move = ai.get_move(game_state, Player.PLAYER_1)
                            game_state.move_piece(ai_move[0], ai_move[1], True)
                            next_player = "b"
                        elif next_player == "b":
                            ai_move = ai2.get_move(game_state, Player.PLAYER_2)
                            game_state.move_piece(ai_move[0], ai_move[1], True)
                            next_player = "w"
                        turns = turns + 1

                    draw_game_state(screen, game_state, valid_moves, square_selected)

                    # calculating endgame
                    endgame = game_state.checkmate_stalemate_checker()
                    if endgame == 0:
                        # white lost
                        game_over = True
                        print("game", i, endgame, "black wins in", turns, "turns")
                        break
                    elif endgame == 1:
                        # black lost
                        game_over = True
                        print("game", i, endgame, "white wins in", turns, "turns")
                        break
                    elif endgame == 2:
                        game_over = True
                        print("game", i, endgame, "tie in", turns, "turns")
                        break

                    clock.tick(MAX_FPS)
                    py.display.flip()

                # updating values
                if endgame == 1:
                    ai.save_in_file()
                    ai2.save_in_file()
                elif endgame == 0:
                    ai.save_in_file()
                    ai2.save_in_file()

                # reset game
                game_over = False
                game_state = chess_engine.game_state()
                valid_moves = []
                square_selected = ()
                player_clicks = []
                valid_moves = []
                ai.restart()
                ai2.restart()
        return
    
    # run a game with human players
    if number_of_players == 1 and human_player is 'b':
        ai_move = ai_move = ai.get_move(game_state, Player.PLAYER_1)
        game_state.move_piece(ai_move[0], ai_move[1], True)
    while running:
        for e in py.event.get():
            if e.type == py.QUIT:
                running = False
            elif e.type == py.MOUSEBUTTONDOWN:
                if not game_over:
                    location = py.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if square_selected == (row, col):
                        square_selected = ()
                        player_clicks = []
                    else:
                        square_selected = (row, col)
                        player_clicks.append(square_selected)
                    if len(player_clicks) == 2:
                        # this if is useless right now
                        if (player_clicks[1][0], player_clicks[1][1]) not in valid_moves:
                            square_selected = ()
                            player_clicks = []
                            valid_moves = []
                        else:
                            game_state.move_piece((player_clicks[0][0], player_clicks[0][1]),
                                                (player_clicks[1][0], player_clicks[1][1]), False)
                            square_selected = ()
                            player_clicks = []
                            valid_moves = []

                            if 'w' in cpu_player:
                                ai_move = ai_move = ai_move = ai.get_move(game_state, Player.PLAYER_1)
                                game_state.move_piece(ai_move[0], ai_move[1], True)
                            elif 'b' in cpu_player:
                                ai_move = ai_move = ai_move = ai.get_move(game_state, Player.PLAYER_2)
                                game_state.move_piece(ai_move[0], ai_move[1], True)
                    else:
                        valid_moves = game_state.get_valid_moves((row, col))
                        if valid_moves is None:
                            valid_moves = []
            elif e.type == py.KEYDOWN:
                if e.key == py.K_r:
                    game_over = False
                    game_state = chess_engine.game_state()
                    valid_moves = []
                    square_selected = ()
                    player_clicks = []
                    valid_moves = []
                    ai.restart()
                elif e.key == py.K_u:
                    game_state.undo_move()
                    print(len(game_state.move_log))

        draw_game_state(screen, game_state, valid_moves, square_selected)

        endgame = game_state.checkmate_stalemate_checker()
        if endgame == 0:
            game_over = True
            draw_text(screen, "Black wins.")
        elif endgame == 1:
            game_over = True
            draw_text(screen, "White wins.")
        elif endgame == 2:
            game_over = True
            draw_text(screen, "Stalemate.")

        clock.tick(MAX_FPS)
        py.display.flip()

    # elif human_player is 'w':
    #     ai = ai_engine.chess_ai()
    #     game_state = chess_engine.game_state()
    #     valid_moves = []
    #     while running:
    #         for e in py.event.get():
    #             if e.type == py.QUIT:
    #                 running = False
    #             elif e.type == py.MOUSEBUTTONDOWN:
    #                 if not game_over:
    #                     location = py.mouse.get_pos()
    #                     col = location[0] // SQ_SIZE
    #                     row = location[1] // SQ_SIZE
    #                     if square_selected == (row, col):
    #                         square_selected = ()
    #                         player_clicks = []
    #                     else:
    #                         square_selected = (row, col)
    #                         player_clicks.append(square_selected)
    #                     if len(player_clicks) == 2:
    #                         if (player_clicks[1][0], player_clicks[1][1]) not in valid_moves:
    #                             square_selected = ()
    #                             player_clicks = []
    #                             valid_moves = []
    #                         else:
    #                             game_state.move_piece((player_clicks[0][0], player_clicks[0][1]),
    #                                                   (player_clicks[1][0], player_clicks[1][1]), False)
    #                             square_selected = ()
    #                             player_clicks = []
    #                             valid_moves = []
    #
    #                             ai_move = ai.minimax(game_state, 3, -100000, 100000, True, Player.PLAYER_2)
    #                             game_state.move_piece(ai_move[0], ai_move[1], True)
    #                     else:
    #                         valid_moves = game_state.get_valid_moves((row, col))
    #                         if valid_moves is None:
    #                             valid_moves = []
    #             elif e.type == py.KEYDOWN:
    #                 if e.key == py.K_r:
    #                     game_over = False
    #                     game_state = chess_engine.game_state()
    #                     valid_moves = []
    #                     square_selected = ()
    #                     player_clicks = []
    #                     valid_moves = []
    #                 elif e.key == py.K_u:
    #                     game_state.undo_move()
    #                     print(len(game_state.move_log))
    #         draw_game_state(screen, game_state, valid_moves, square_selected)
    #
    #         endgame = game_state.checkmate_stalemate_checker()
    #         if endgame == 0:
    #             game_over = True
    #             draw_text(screen, "Black wins.")
    #         elif endgame == 1:
    #             game_over = True
    #             draw_text(screen, "White wins.")
    #         elif endgame == 2:
    #             game_over = True
    #             draw_text(screen, "Stalemate.")
    #
    #         clock.tick(MAX_FPS)
    #         py.display.flip()
    #
    # elif human_player is 'b':
    #     pass


def draw_text(screen, text):
    font = py.font.SysFont("Helvitca", 32, True, False)
    text_object = font.render(text, False, py.Color("Black"))
    text_location = py.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - text_object.get_width() / 2,
                                                      HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)


if __name__ == "__main__":
    main()
