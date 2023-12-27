import random
import sys
sys.tracebacklimit = 0

class BreakthroughBoard:
    def __init__(self):
        self.board = [['.' for _ in range(8)] for _ in range(8)]
        self.initialize_board()
        self.current_player = 'P'
        self.ai_piece = 'p'
        self.user_move_history = []
        self.ai_move_history = []
        self.player_moves = 1
        self.en_passant_target = None
        self.strategy_table = {
            "AI's Turn": {
                "Prioritize Moving Closer to Player's Home Row": "Action: Move pawn closer to Player's home row",
                "Evaluate Capturing Player's Pawns": "Action: Move to capture Player's pawn if possible",
                "Blocking Player's Progress": "Action: Move to block and capture the Player's pawn if it's near rows 2 or 3",
                "Exploiting Two-Square First Move": "Action: Use two-square move option on the first move if available",
                "En Passant Move": "Action: Consider en passant move if applicable",
                "Endgame Strategy": "Action: Focus on reaching the other end of the board quickly for a win"
            },
            "Positions of AI's Pawns Closest to Player's Home Row": {
                "AI's Turn": "Action: Move pawn closer to opponent's home row",
            },
            "Positions of Player's Pawns Closest to AI's Home Row": {
                "AI's Turn": "Action: Move to capture opponent's pawn if possible",
            },
            "Available Legal Moves for AI": {
                "Forward Movement Only": "Action: Move to block and capture the player's pawn if it's near rows 4 or 5",
            },
            "Two-Square First Move": {
                "AI's Turn": "Action: Use two-square move option on the first move if available",
            },
            "Current Position of All Pieces": {
                "Whose Turn It Is": "Action: Focus on reaching the other end of the board quickly for a win",
            },
        }
        
    def initialize_board(self):
        for i in range(8):
            self.board[0][i] = 'P'
            self.board[1][i] = 'P'
            self.board[6][i] = 'p'
            self.board[7][i] = 'p'

    def display_board(self):
        print("   a b c d e f g h")
        for i in range(8, 0, -1):
            row = self.board[i - 1]
            pieces = [str(piece) for piece in row]
            print(i, end=" ")
            for piece in pieces:
                print(" " + piece, end="")
            print()
        print("   a b c d e f g h")
        
    def make_move(self, move_from, move_to):
        while True:
            from_x, from_y = self.square_to_coordinates(move_from)
            to_x, to_y = self.square_to_coordinates(move_to)
            piece = self.board[from_x][from_y]
            if piece == '.':
                print("No piece at that square. Try again.")
            elif not self.is_valid_move(from_x, from_y, to_x, to_y, piece):
                print("Invalid move. Please try again.")
            else:
                break
            
            if self.current_player == self.ai_piece:
                print("AI made an invalid move. Please debug your AI logic.")
                raise SystemExit(0)

            move_from = input("Select your piece to move (e.g., c2) or enter 'exit' to exit: ").strip()
            move_to = input("Move it to (e.g., c3): ").strip()
            if move_from.lower() == 'exit':
                print("Player exits. Opponent wins!")
                break
        current_pawns, opponent_pawns = self.find_closest_pawns()
        if (to_x, to_y) in current_pawns:
            print(f"Game over! A {self.current_player} pawn reached the opponent's end. {self.current_player} wins!")
            return True
        if piece.islower() and from_x == 4 and to_x == 5 and abs(from_y - to_y) == 1:
            captured_pawn_square = self.coordinates_to_square(4, to_y)
            self.board[4][to_y] = '.'
            print(f"En passant! {self.current_player}'s pawn captures {captured_pawn_square}.")

        self.board[to_x][to_y] = piece
        self.board[from_x][from_y] = '.'
        self.current_player = 'P' if piece.islower() else 'p'
        self.current_piece = piece
        if self.current_player != self.ai_piece:
            self.ai_move_history.append((move_from, move_to))
            self.player_moves += 1
        else:
            self.user_move_history.append((move_from, move_to))
        if self.check_for_win():
            return True
        return False
    
    def is_valid_move(self, from_x, from_y, to_x, to_y, piece):
        if to_x < 0 or to_x >= 8 or to_y < 0 or to_y >= 8:
            return False 

        if piece.islower():
            if from_x - to_x == 1 and from_y == to_y and self.board[to_x][to_y] == '.':
                return True
            if from_x - to_x == 2 and from_y == to_y and from_x == 6 and to_x == 4 and self.board[to_x][to_y] == '.' and self.board[to_x + 1][to_y] == '.':
                return True
            elif from_x - to_x == 1 and abs(from_y - to_y) == 1 and self.board[to_x][to_y].isupper():
                return True

            if from_x - to_x == 2 and from_y == to_y and from_x == 7 and to_x == 5 and self.board[to_x][to_y] == '.' and self.board[to_x + 1][to_y] == '.':
                return True
            elif from_x - to_x == 1 and abs(from_y - to_y) == 1 and self.board[to_x][to_y].isupper():
                return True
            if from_x == 4 and to_x == 5 and abs(from_y - to_y) == 1 and self.en_passant_target == self.coordinates_to_square(5, to_y):
                return True
            
        elif piece.isupper():
            if to_x - from_x == 1 and from_y == to_y and self.board[to_x][to_y] == '.':
                return True
            if to_x - from_x == 2 and from_y == to_y and from_x == 1 and to_x == 3 and self.board[to_x][to_y] == '.' and self.board[to_x - 1][to_y] == '.':
                return True
            elif to_x - from_x == 1 and abs(from_y - to_y) == 1 and self.board[to_x][to_y].islower():
                return True
            if to_x - from_x == 2 and from_y == to_y and from_x == 0 and to_x == 2 and self.board[to_x][to_y] == '.' and self.board[to_x - 1][to_y] == '.':
                return True
            elif to_x - from_x == 1 and abs(from_y - to_y) == 1 and self.board[to_x][to_y].islower():
                return True
            if from_x == 3 and to_x == 2 and abs(from_y - to_y) == 1 and self.en_passant_target == self.coordinates_to_square(2, to_y):
                return True
        return False

    def display_en_passant_target(self):
        if self.en_passant_target:
            print(f"En passant target square: {self.en_passant_target}")

    def square_to_coordinates(self, square):
        column, row = square[0], int(square[1])
        return row - 1, ord(column) - ord('a')

    def is_game_over(self):
        player_pawn = 'P'
        opponent_pawn = 'p'
        for row in self.board:
            if player_pawn in row or opponent_pawn in row:
                return False
        print(f"Game over! No {opponent_pawn} pawns left. {self.current_player} wins!")
        return True

    def ai_make_move(self):
        valid_moves = self.get_valid_moves()
        for move in valid_moves:
            move_from_x, move_from_y = self.square_to_coordinates(move[0])
            move_to_x, move_to_y = self.square_to_coordinates(move[1])
            if move_from_x == 6 and move_to_x == 5 and abs(move_from_y - move_to_y) == 1:
                self.make_move(move[0], move[1])
                return
        for i, move in enumerate(valid_moves):
            move_from, move_to = move
            move_from_x, move_from_y = self.square_to_coordinates(move_from)
            move_to_x, move_to_y = self.square_to_coordinates(move_to)
            percepts = {
                "AI's Turn": True if self.current_player == self.ai_piece else False,
                "Positions of AI's Pawns Closest to Opponent's Home Row": [(6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), 
                                                                           (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7)],
                "Positions of Player's Pawns Closest to AI's Home Row": self.find_closest_pawns()[1],
                "Available Legal Moves for AI": valid_moves,
                "Forward Movement Only": True,  # As pawns only move forward
                "Two-Square First Move": True if self.player_moves <= 2 and move_from_x in [6, 7] else False,
                "Current Position of All Pieces": self.board,
                "Whose Turn It Is": self.current_player,
            }
            action = self.determine_action(percepts)
            if action == "Action: Move pawn closer to opponent's home row":
                self.make_move(move_from, move_to)
                return
            if action == "Action: Move to capture opponent's pawn if possible":
                target_x, target_y = self.find_best_opponent_pawn_capture(move_to_x, move_to_y)
                if target_x is not None and target_y is not None:
                    target_square = self.coordinates_to_square(target_x, target_y)
                    self.make_move(move_from, target_square)
                    return
            if action == "Action: Move to block and capture the player's pawn if it's near rows 4 or 5":
                player_pawns_near_middle = any((row in [3, 4] for row, _ in self.find_closest_pawns()[1]))
                if player_pawns_near_middle:
                    self.make_move(move_from, move_to)
                    return
            if action == "Action: Use two-square move option on the first move if available":
                if self.player_moves <= 2 and move_from_x in [6, 7]:
                    self.make_move(move_from, move_to)
                    return
            if action == "Action: Consider en passant move if applicable":
                en_passant_target_square = self.check_en_passant(move_to_x, move_to_y)
                if en_passant_target_square:
                    self.make_move(move_from, en_passant_target_square)
                    return
            if action == "Action: Focus on reaching the other end of the board quickly for a win":
                if self.player_moves >= 60:
                    self.make_move(move_from, move_to)
                    return
            move_to_make = move_to
        if move_to_make is not None:
            self.make_move(move_from, move_to_make)
        else:
            default_action = "Action: Move pawn closer to opponent's home row"
            print(f"No specific action taken. Using default action: {default_action}")

    def determine_action(self, percepts):
        for percept_key in self.strategy_table:
            if percepts.get(percept_key, False):
                strategy = self.strategy_table[percept_key]
                for strategy_key in strategy:
                    if strategy_key in percepts and percepts[strategy_key]:
                        if percept_key == "Positions of AI's Pawns Closest to Opponent's Home Row":
                            all_closest_pawns_in_position = all(coord in percepts[percept_key] for coord in [(6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), 
                                                                            (6, 6), (6, 7), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7)])
                            if all_closest_pawns_in_position:
                                return strategy[strategy_key]
                            elif percept_key == "AI's Turn" and all(coord in percepts[percept_key] for coord in [(6, 0), (6, 1), (6, 2), (6, 3), (6, 4), 
                                                                (6, 5), (6, 6), (6, 7), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7)]):
                                return strategy[strategy_key]
        return "Default Action"
    
    def find_best_opponent_pawn_capture(self, current_x, current_y):
        opponent_pawns = self.find_closest_pawns()[1]
        best_capture = None
        best_capture_distance = float('inf')
        for opponent_x, opponent_y in opponent_pawns:
            if opponent_y == current_y:
                distance = opponent_x - current_x
                if 0 < distance < best_capture_distance:
                    best_capture = (opponent_x, opponent_y)
                    best_capture_distance = distance
        return best_capture
    
    def get_valid_moves(self):
        valid_moves = []
        player_piece = 'p'
        move_direction = -1
        for i in range(8):
            for j in range(8):
                if self.board[i][j] == player_piece:
                    if self.is_valid_move(i, j, i + move_direction, j, player_piece):
                        valid_moves.append((self.coordinates_to_square(i, j), self.coordinates_to_square(i + move_direction, j)))
                    if self.is_valid_move(i, j, i + move_direction, j + 1, player_piece):
                        valid_moves.append((self.coordinates_to_square(i, j), self.coordinates_to_square(i + move_direction, j + 1)))
                    if self.is_valid_move(i, j, i + move_direction, j - 1, player_piece):
                        valid_moves.append((self.coordinates_to_square(i, j), self.coordinates_to_square(i + move_direction, j - 1)))
        return valid_moves

    def coordinates_to_square(self, x, y):
        column = chr(y + ord('a'))
        row = str(x + 1)
        return column + row

    def check_for_win(self):
        for col in range(8):
            if self.board[7][col] == 'P':
                self.display_user_move_history()
                self.display_board()
                print(f"Game over! A player's pawn reached the last row. Player wins!")
                raise SystemExit(0)
                return True
        for col in range(8):
            if self.board[0][col] == 'p':
                self.display_ai_move_history()
                self.display_board()
                print(f"Game over! AI's pawn reached the first row. AI Agent wins!")
                raise SystemExit(0)
                return True
        return False

    def find_closest_pawns(self):
        current_home_row = 0 
        opponent_home_row = 7
        current_pawns = []
        opponent_pawns = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece == 'P' and row == current_home_row:
                    current_pawns.append((row, col))
                elif piece == 'p' and row == opponent_home_row:
                    opponent_pawns.append((row, col))
        return current_pawns, opponent_pawns

    def display_user_move_history(self):
        print("User Move History:")
        for i, move in enumerate(self.user_move_history, start=1):
            move_from, move_to = move
            print(f"{i}. {move_from} to {move_to}")

    def display_ai_move_history(self):
        print("AI Move History:")
        for i, move in enumerate(self.ai_move_history, start=1):
            move_from, move_to = move
            print(f"{i}. {move_from} to {move_to}")

    def is_valid_input(self, move):
        if len(move) != 2:
            return False
        column, row = move[0], move[1]
        if not column.isalpha() or not row.isdigit():
            return False
        column = column.lower()
        if column not in 'abcdefgh' or row not in '12345678':
            return False
        return True

    def play_game(self):
        print("****Welcome to the Breakthrough Game****")
        ai_turn = False
        while not self.is_game_over():
            self.display_board()
            if ai_turn:
                self.ai_make_move()
                self.display_ai_move_history()
            else:
                print(f"Player's turn (Turn {self.player_moves}).")
                while True:
                    move_from = input("Select your piece to move (e.g., c2) or enter 'exit' to exit: ").strip()
                    if move_from.lower() == 'exit':
                        print("Player exits. Opponent wins!")
                        break
                    if self.is_valid_input(move_from):
                        break
                    else:
                        print("Invalid input. Please enter a valid move.")
                if move_from.lower() == 'exit':
                    break
                while True:
                    move_to = input("Move it to (e.g., c3): ").strip()
                    if self.is_valid_input(move_to):
                        break
                    else:
                        print("Invalid input. Please enter a valid move.")
                self.make_move(move_from, move_to)
                self.display_user_move_history()
            ai_turn = not ai_turn 
        if ai_turn:
            self.display_ai_move_history()
        else:
            self.display_user_move_history()
        self.display_board()
        if self.is_game_over():
            return

if __name__ == "__main__":
    breakthrough_board = BreakthroughBoard()
    breakthrough_board.play_game()
