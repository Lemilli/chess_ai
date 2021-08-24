import chess
from chess.polyglot import open_reader
import sys
import time
from random import randint
import arrays 


TURN_COUNT = 1

class AI:
    def __init__(self, board, player_color, depth):
        self.board = board
        self.ai_color = not player_color
        self.depth = depth
        
        
    # Chooses and makes a move for the AI (void)
    def ai_move(self):
        with open_reader('openings.bin') as reader:
            opening_moves = []
            for entry in reader.find_all(board):
                opening_moves.append(entry.move)

        # Documentation on opening moves https://python-chess.readthedocs.io/en/latest/polyglot.html#chess.polyglot.Entry.move
        if opening_moves:
            rand_open_move = opening_moves[randint(0, len(opening_moves)-1)]
            self.board.push(rand_open_move)
            print('\nOpening Book Computer move: ', str(rand_open_move))
        else:
            global_score = -1e6 if self.ai_color else 1e6
            chosen_move = None

            for move in self.board.legal_moves:
                self.board.push(move)
                local_score = self.minimax(self.depth - 1, not self.ai_color, -1e6, 1e6)

                if self.ai_color and local_score > global_score:
                    global_score = local_score
                    chosen_move = move

                elif not self.ai_color and local_score < global_score:
                    global_score = local_score
                    chosen_move = move
                self.board.pop()
                print('Possible move:', move, '|| Move evaluation:', local_score)
    
            print('\nComputer move: ', str(chosen_move), '|| Value of move:', str(global_score))
    
            self.board.push(chosen_move)

    # Minimax with alpha-beta Pruning which returns
    def minimax(self, depth, is_maxing_white, alpha, beta):
        # if depth is 0 or game is over
        if depth == 0 or not self.board.legal_moves:
            return evaluate_board(self.board)

        best_score = -1000000 if is_maxing_white else 1000000
        for move in self.board.legal_moves:
            self.board.push(move)

            local_score = self.minimax(depth - 1, not is_maxing_white, alpha, beta)

            if is_maxing_white:
                best_score = max(best_score, local_score)
                alpha = max(alpha, best_score)
            else:
                best_score = min(best_score, local_score)
                beta = min(beta, best_score)

            self.board.pop()

            if beta <= alpha:
                break

        return best_score


def evaluate_board(board):
    if board.is_checkmate():
        if board.result() == '1-0':
            return 100000
        else:
            return -100000
    else:
        total_evaluation = 0
        for square in range(64):
            total_evaluation += get_piece_value(board.piece_at(square), square)

        return total_evaluation

def get_piece_value(piece, i):
    # If the square is empty (i.e., no piece at the square)
    if piece is None or piece.piece_type == chess.KING:
        return 0
    
    # Documentation of chess pieces on this part - https://python-chess.readthedocs.io/en/latest/core.html
    # If piece is white
    if piece.color == chess.WHITE:
        if piece.piece_type == chess.PAWN:
            return 10 + arrays.pawn_eval_white[i]
        elif piece.piece_type == chess.ROOK:
            return 50 + arrays.rook_eval_white[i]
        elif piece.piece_type == chess.BISHOP:
            return 32 + arrays.bishop_eval_white[i]
        elif piece.piece_type == chess.KNIGHT:
            return 30 + arrays.knight_eval[i]
        elif piece.piece_type == chess.QUEEN:
            return 90 + arrays.queen_eval[i]
        elif piece.piece_type == chess.KING:
            return arrays.king_eval_white[i]
        
    # If piece is black
    else:
        if piece.piece_type == chess.PAWN:
            return -(10 + arrays.pawn_eval_black[i])
        elif piece.piece_type == chess.ROOK:
            return -(50 + arrays.rook_eval_black[i])
        elif piece.piece_type == chess.BISHOP:
            return -(32 + arrays.bishop_eval_black[i])
        elif piece.piece_type == chess.KNIGHT:
            return -(30 + arrays.knight_eval[i])
        elif piece.piece_type == chess.QUEEN:
            return -(90 + arrays.queen_eval[i])
        elif piece.piece_type == chess.KING:
            return -arrays.king_eval_black[i]
        
    
# Uses UNICODE
def print_board(board):
    if ENCODING == 0:
        board = board.mirror()
        for square in chess.SQUARES:
            piece = board.piece_at(square)

            if square % 8 == 0 and square != 0:
                print()
            if piece is None:
                print(' ', end='')
            else:
                print(chess.UNICODE_PIECE_SYMBOLS[str(piece)], end = '', sep='')
            print(' ', end='')
        print('\na b c d e f g h')
    else:
        print(board)

def user_move():
    print_board(computer.board)
    print('Turn: ', int(TURN_COUNT))

    while 1:
        try:
            user_input = input("Your turn: ")
            user_input = chess.Move.from_uci(user_input)
            if user_input in computer.board.legal_moves:
                computer.board.push(user_input)
                break
            else:
                print("This move is illegal. Try again.")
        except KeyboardInterrupt:
            sys.exit(0)
        except:
            print("Try again.")
            continue
    

def print_result():
    if computer.board.result() == '1-0':
        print("Game over. White won.")
    elif computer.board.result() == '0-1':
        print("Game over. Black won.")
    else:
        print("Game finished by Draw.")

def game_finished():
    if computer.board.is_game_over():
            print_result()
            return True
    return False
        
        
#main
board = chess.Board() # Create new board
user_color = int(input("Choose a color of your pieces (white: 1, black: 0): "))
ENCODING = int(input("If you are using command line that doesn't support Unicode enter 1, otherwise enter 0: "))
input_depth = int(input("Choose AI depth (fast AI moves: depth 3, better but slower: 4): "))

computer = AI(board, user_color, input_depth)

while 1:
    if user_color == chess.WHITE:
        user_move()
        if game_finished():
            break

        start = time.time() # Start timer
        computer.ai_move()
        if game_finished():
            break

        end = time.time() # Stop timer
        print('Time spent on this turn by AI: ', int(end - start), 'seconds.') # Timer result

    else:
        start = time.time() # Start timer

        computer.ai_move()
        if game_finished():
            break

        end = time.time() # Stop timer
        print('Time spent on this turn by AI: ', int(end - start), 'seconds.') # Timer result

        user_move()
        if game_finished():
            break

    TURN_COUNT += 1

    
    
