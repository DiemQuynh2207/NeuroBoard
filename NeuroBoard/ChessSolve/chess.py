def generate_legal_moves(engine, check_incheck=True):
	"""
	Generate all legal moves for the current player's turn.
	"""
	legal_moves = []
	for row in range(8):
		for col in range(8):
			piece = engine.board[row][col] 
			if piece != '.' and ((engine.turn == 'w' and piece.isupper()) or (engine.turn == 'b' and piece.islower())):
				legal_moves.extend(get_piece_moves(engine, piece, (row, col), check_incheck))
	return legal_moves

#uci dict
square_file = {0:'a', 1:'b', 2:'c', 3:'d', 4:'e', 5:'f', 6:'g', 7:'h'} #column / x letter abc
square_rank = {0:8, 1:7, 2:6, 3:5, 4:4, 5:3, 6:2, 7:1} #row / y number   (from 1 -> 8)
# the rank is opposite because in tkinter gui the y begin from top to bottom
#  y=0 
#  y=1
#  y=2

def convert_to_uci_move(move):
	start, end = move
	start_rank, start_file = start
	end_rank, end_file = end

	#convert to uci
	start_file = square_file[start_file]
	start_rank = square_rank[start_rank]

	#convert to uci
	end_file = square_file[end_file]
	end_rank = square_rank[end_rank]
	return f"{start_file}{start_rank}{end_file}{end_rank}"


def get_piece_moves(engine, piece, position, check_incheck=True):
	"""
	Get all possible moves for a specific piece from a given position.
	"""
	row, col = position
	moves = []
	if piece.lower() == 'p':  # Pawn
		moves.extend(get_pawn_moves(engine, piece, position))
	elif piece.lower() == 'r':  # Rook
		moves.extend(get_rook_moves(engine, piece, position))
	elif piece.lower() == 'n':  # Knight
		moves.extend(get_knight_moves(engine, piece, position))
	elif piece.lower() == 'b':  # Bishop
		moves.extend(get_bishop_moves(engine, piece, position))
	elif piece.lower() == 'q':  # Queen
		moves.extend(get_rook_moves(engine, piece, position))
		moves.extend(get_bishop_moves(engine, piece, position))
	elif piece.lower() == 'k':  # King
		moves.extend(get_king_moves(engine, piece, position))

	# Check if move not make king be in check
	if check_incheck: 
		moves = [move for move in moves if is_move_safe(engine, move)]

	return moves


def get_pawn_moves(engine, piece, position, statefake=False):
	"""Generate all possible moves for a pawn."""
	row, col = position
	moves = []
	direction = -1 if piece.isupper() else 1  # White moves up, black moves down
	# Single square forward
	if is_empty(engine, row + direction, col):
		moves.append((position, (row + direction, col)))
	# Double square forward on first move
	if (row == 6 and piece.isupper()) or (row == 1 and piece.islower()):
		if is_empty(engine, row + direction, col) and is_empty(engine, row + 2 * direction, col):
			moves.append((position, (row + 2 * direction, col)))
	# Captures
	for dx in [-1, 1]:
		if is_within_board(engine, row + direction, col + dx) and is_enemy_piece(engine, row + direction, col + dx):
			moves.append((position, (row + direction, col + dx)))

	return moves

def get_rook_moves(engine, piece, position):
	"""Generate all possible moves for a rook."""
	return get_sliding_moves(engine, piece, position, directions=[(1, 0), (-1, 0), (0, 1), (0, -1)])

def get_bishop_moves(engine, piece, position):
	"""Generate all possible moves for a bishop."""
	return get_sliding_moves(engine, piece, position, directions=[(1, 1), (-1, -1), (1, -1), (-1, 1)])

def get_knight_moves(engine, piece, position):
	"""Generate all possible moves for a knight."""
	row, col = position
	moves = []
	knight_offsets = [(-2, -1), (-1, -2), (1, -2), (2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1)]
	for dx, dy in knight_offsets:

		if is_within_board(engine, row + dx, col + dy) and not is_friendly_piece(engine, row + dx, col + dy):
			moves.append((position, (row + dx, col + dy)))
	return moves

def get_king_moves(engine, piece, position):
	"""Generate all possible moves for a king."""
	row, col = position
	moves = []
	king_offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
	for dx, dy in king_offsets:
		if is_within_board(engine, row + dx, col + dy) and not is_friendly_piece(engine, row + dx, col + dy):
			moves.append((position, (row + dx, col + dy)))
	return moves

def get_sliding_moves(engine, piece, position, directions):
	"""Generate all possible moves for sliding pieces (rook, bishop, queen)."""
	row, col = position
	moves = []
	for dx, dy in directions:
		r, c = row + dx, col + dy
		while is_within_board(engine, r, c):
			if is_empty(engine, r, c):
				moves.append((position, (r, c)))
			elif is_enemy_piece(engine, r, c):
				moves.append((position, (r, c)))
				break
			else:
				break
			r, c = r + dx, c + dy
	return moves

def is_move_safe(engine, move):
	"""
	Simulate a move and check if it leaves the king in check.
	"""
	start, end = move
	sx, sy = start
	ex, ey = end

	# Save the current board state
	original_piece = engine.board[ex][ey]
	moving_piece = engine.board[sx][sy]

	# Simulate the move
	engine.board[ex][ey] = moving_piece
	engine.board[sx][sy] = '.'

	# Check if the king is in check
	is_safe = not is_king_in_check(engine)

	# Revert the move
	engine.board[sx][sy] = moving_piece
	engine.board[ex][ey] = original_piece

	return is_safe

def is_king_in_check(engine):
	"""
	Check if the current player's king is in check.
	"""
	# Find the king's position
	king_symbol = 'K' if engine.turn == 'w' else 'k'
	king_position = None

	for row in range(8):
		for col in range(8):
			if engine.board[row][col] == king_symbol:
				king_position = (row, col)
				break
		if king_position:
			break

	if not king_position:
		raise ValueError("King not found on the board!")

	# Check if any enemy piece attacks the king
	engine.updateTurn()
	moves = generate_legal_moves(engine, check_incheck=False)
	engine.updateTurn()
	if king_position in [end for _, end in moves]:
		return True
		
	# 
	# opponent_turn = 'b' if engine.turn == 'w' else 'w'
	# for row in range(8):
	# 	for col in range(8):
	# 		piece = engine.board[row][col]
	# 		if piece != '.' and ((opponent_turn == 'w' and piece.isupper()) or (opponent_turn == 'b' and piece.islower())):
	# 			if king_position in [end for start, end in get_piece_moves(engine, piece, (row, col))]:
	# 				return True

	return False

def is_valid(start, end):
	sx, sy = start
	ex, ey = end
	if not (0 <= sx < 8 and 0 <= sy < 8 and 0 <= ex < 8 and 0 <= ey < 8):
		return False  # Out of bounds

def is_within_board(engine, row, col):
	return 0 <= row < 8 and 0 <= col < 8

def is_empty(engine, row, col):
	return engine.board[row][col] == '.'

def is_friendly_piece(engine, row, col):
	piece = engine.board[row][col]
	return piece != '.' and ((engine.turn == 'w' and piece.isupper()) or (engine.turn == 'b' and piece.islower()))

def is_enemy_piece(engine, row, col):
	piece = engine.board[row][col]
	return piece != '.' and ((engine.turn == 'b' and piece.isupper()) or (engine.turn == 'w' and piece.islower()))

def evaluate_board(board):
    piece_values = {
        "p": 100, "n": 300, "b": 330, "r": 500, "q": 900, "k": 0,
        "P": 100, "N": 300, "B": 330, "R": 500, "Q": 900, "K": 0
    }
    
    # Positional values for all pieces
    pawn_table = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [5, 10, 10, -20, -20, 10, 10, 5],
        [5, -5, -10, 0, 0, -10, -5, 5],
        [0, 0, 0, 20, 20, 0, 0, 0],
        [5, 5, 10, 25, 25, 10, 5, 5],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]
    knight_table = [
        [-50, -40, -30, -30, -30, -30, -40, -50],
        [-40, -20, 0, 0, 0, 0, -20, -40],
        [-30, 0, 10, 15, 15, 10, 0, -30],
        [-30, 5, 15, 20, 20, 15, 5, -30],
        [-30, 0, 15, 20, 20, 15, 0, -30],
        [-30, 5, 10, 15, 15, 10, 5, -30],
        [-40, -20, 0, 5, 5, 0, -20, -40],
        [-50, -40, -30, -30, -30, -30, -40, -50],
    ]
    bishop_table = [
        [-20, -10, -10, -10, -10, -10, -10, -20],
        [-10, 0, 0, 0, 0, 0, 0, -10],
        [-10, 0, 5, 10, 10, 5, 0, -10],
        [-10, 5, 5, 10, 10, 5, 5, -10],
        [-10, 0, 10, 10, 10, 10, 0, -10],
        [-10, 10, 10, 10, 10, 10, 10, -10],
        [-10, 5, 0, 0, 0, 0, 5, -10],
        [-20, -10, -10, -10, -10, -10, -10, -20],
    ]
    rook_table = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [5, 10, 10, 10, 10, 10, 10, 5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [0, 0, 0, 5, 5, 0, 0, 0],
    ]
    queen_table = [
        [-20, -10, -10, -5, -5, -10, -10, -20],
        [-10, 0, 0, 0, 0, 0, 0, -10],
        [-10, 0, 5, 5, 5, 5, 0, -10],
        [-5, 0, 5, 5, 5, 5, 0, -5],
        [0, 0, 5, 5, 5, 5, 0, -5],
        [-10, 5, 5, 5, 5, 5, 0, -10],
        [-10, 0, 5, 0, 0, 0, 0, -10],
        [-20, -10, -10, -5, -5, -10, -10, -20],
    ]
    king_table = [
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-20, -30, -30, -40, -40, -30, -30, -20],
        [-10, -20, -20, -20, -20, -20, -20, -10],
        [20, 20, 0, 0, 0, 0, 20, 20],
        [20, 30, 10, 0, 0, 10, 30, 20],
    ]

    evaluation = 0
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece == '.':
                continue

            value = piece_values[piece]
            if piece.isupper():  # White piece
                evaluation += value
                if piece == "P":
                    evaluation += pawn_table[row][col]
                elif piece == "N":
                    evaluation += knight_table[row][col]
                elif piece == "B":
                    evaluation += bishop_table[row][col]
                elif piece == "R":
                    evaluation += rook_table[row][col]
                elif piece == "Q":
                    evaluation += queen_table[row][col]
                elif piece == "K":
                    evaluation += king_table[row][col]
            else:  # Black piece
                evaluation -= value
                if piece == "p":
                    evaluation -= pawn_table[7 - row][col]
                elif piece == "n":
                    evaluation -= knight_table[7 - row][col]
                elif piece == "b":
                    evaluation -= bishop_table[7 - row][col]
                elif piece == "r":
                    evaluation -= rook_table[7 - row][col]
                elif piece == "q":
                    evaluation -= queen_table[7 - row][col]
                elif piece == "k":
                    evaluation -= king_table[7 - row][col]

    return evaluation


