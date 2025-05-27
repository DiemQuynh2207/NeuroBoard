import tkinter as tk
import tkinter.ttk as ttk

from PIL import Image, ImageTk
import chess as cl
from games4e import Game, alpha_beta_cutoff_search
import copy

class Statecopy:
	def __init__(self, realstate):
		self.board = copy.deepcopy(realstate.board)
		self.turn = realstate.turn

	def updateTurn(self):
		self.turn = 'b' if self.turn == 'w' else 'w'

	def update_board(self, start, end):
		sx, sy = start
		ex, ey = end
		self.board[ex][ey] = self.board[sx][sy]
		self.board[sx][sy] = '.'
		#check promotion
		if self.board[ex][ey].lower()=='p' and (ex==7 or ex==0):
			print('promote')
			self.board[ex][ey] = "Q" if self.board[ex][ey].isupper() else "q"


class ChessGame(Game):

	def actions(self, state):
		"""
		Return all legal moves in the current state.
		"""
		return list(cl.generate_legal_moves(state))

	def result(self, state, move):
		"""
		Return the new state after applying the move.
		"""
		start, end = move
		
		new_state = Statecopy(state)
		new_state.update_board(start, end)
		new_state.updateTurn()
		return new_state

	def utility(self, state, player):
		"""
		Define a utility function: positive for white, negative for black.
		"""
		# Use a simple evaluation based on material
		score = cl.evaluate_board(state.board)
		return score if player=='w' else -score

	def terminal_test(self, state):
		"""
		Check if the game is over.
		"""
		return not self.actions(state)

	def to_move(self, state):
		"""
		Return the player whose turn it is to move.
		"""
		return state.turn



class MainApp:
	def __init__(self):
		self.board = self.initialize_board()
		self.turn = 'w'  # 'w' for white, 'b' for black
		self.selected_piece = None
		self.start_square = None
		self.moves_highlight = None
		self.square_size = 80
		self.pieces_dict = {'P':'white_pawn', 'R':'white_rook', 'N':'white_knight', 'B':'white_bishop', 'Q':'white_queen', 'K':'white_king', 'p':'black_pawn', 'r':'black_rook', 'n':'black_knight', 'b':'black_bishop', 'q':'black_queen', 'k':'black_king'}

		self.width = 670
		self.height = 730

		# Create the tkinter window
		self.window = tk.Tk()
		self.window.title("Chess Game")
		self.canvas = tk.Canvas(self.window, width=self.width, height=self.height)
		self.canvas.pack()

		# Center screen
		screen_width = self.window.winfo_screenwidth()
		screen_height = self.window.winfo_screenheight()
		
		# Calculate the position to center the window
		
		x = (screen_width - self.width) // 2
		y = (screen_height - self.height) // 2
		
		# Set the geometry with width, height, and coordinates
		self.window.geometry(f"{self.width}x{self.height}+{x}+{y}")

		self.button = tk.Button(self.window, text="Reset board", command=self.reset, font=("source sans pro", 12), background="#EC8305")
		self.button.place(x=450, y=679)
		self.luot = tk.Label(self.window, text="Lượt chơi: Bạn", font=("source sans pro", 12), fg="GREEN")
		self.luot.place(x=150, y=687)

		# Anti resizable
		self.window.resizable(False, False)

		# Load piece images
		self.piece_images_DRAG = None
		self.piece_images = self.load_piece_images()
		self.draw_board()
		self.draw_pieces()

		# Bind mouse events
		self.canvas.bind("<Button-1>", self.on_piece_click)
		self.canvas.bind("<B1-Motion>", self.on_piece_drag)
		self.canvas.bind("<ButtonRelease-1>", self.on_piece_drop)

	def reset(self):
		self.board = self.initialize_board()
		self.turn = 'w'  # 'w' for white, 'b' for black
		self.selected_piece = None
		self.start_square = None
		self.moves_highlight = None
		self.piece_images_DRAG = None
		self.piece_images = self.load_piece_images()
		self.draw_board()
		self.draw_pieces()

	def initialize_board(self):
		# Representing the chessboard as a 2D list
		return [
			['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],  # Black pieces
			['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],  # Black pawns
			['.', '.', '.', '.', '.', '.', '.', '.'],  # Empty
			['.', '.', '.', '.', '.', '.', '.', '.'],  # Empty
			['.', '.', '.', '.', '.', '.', '.', '.'],  # Empty
			['.', '.', '.', '.', '.', '.', '.', '.'],  # Empty
			['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],  # White pawns
			['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],  # White pieces
		]
		

	def load_piece_images(self):
		"""Load images for chess pieces ."""
		piece_images = {}
		piece_images_drag = {}
		file = "images/imgs-80px/"
		file_drag = "images/imgs-128px/"
		for piece in self.pieces_dict.values():
			image = Image.open(f"{file}{piece}.png").convert("RGBA") # Convert to RGB format (removes transparency)
			resized = image.resize((self.square_size, self.square_size), Image.Resampling.LANCZOS)
			piece_images[piece] = ImageTk.PhotoImage(resized)

			#Image drag be bigger than image normal to highlight where we pick piece
			image = Image.open(f"{file_drag}{piece}.png").convert("RGBA") # Convert to RGB format (removes transparency)
			resized = image.resize((self.square_size+48, self.square_size+48), Image.Resampling.LANCZOS)
			piece_images_drag[piece] = ImageTk.PhotoImage(resized)
		self.piece_images_DRAG = piece_images_drag
		return piece_images
		
	def draw_board(self):
		"""Draw the chessboard."""
		self.canvas.delete("squares")  # Clear squares

		# Draw background
		self.canvas.create_rectangle(0, 0, 670, 670, fill="#F3C623",  
		outline="")

		# Draw square and file
		for y, x in cl.square_file.items():
			#rank
			self.canvas.create_text(653.5, y*80+40, text=abs(y-8), font=("source sans pro", 15), fill="WHITE")
			#file
			self.canvas.create_text(y*80+40, 653.5, text=x, font=("source sans pro", 15), fill="WHITE")


		#Draw block square for board
		for row in range(8):
			for col in range(8):
				color = "#133E87" if (row + col) % 2 == 0 else "#CBDCEB"  
				x1 = col * self.square_size
				y1 = row * self.square_size
				x2 = x1 + self.square_size
				y2 = y1 + self.square_size
				self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color, tags="squares")

	def draw_pieces(self):
		"""Draw the pieces on the board."""
		self.canvas.delete("pieces")  # Clear pieces
		for row in range(8):
			for col in range(8):
				piece = self.board[row][col]
				if piece != '.':
					x = col * self.square_size
					y = row * self.square_size
					self.canvas.create_image(x, y, anchor=tk.NW, image=self.piece_images[self.pieces_dict[piece]], tags="pieces")

	def on_piece_click(self, event):
		"""Handle piece selection on mouse click."""
		col = event.x // self.square_size
		row = event.y // self.square_size
		if (col > 7 or col < 0 or row > 7 or row < 0):
			return
		piece = self.board[row][col]

		if piece != '.' and ((self.turn == 'w' and piece.isupper()) or (self.turn == 'b' and piece.islower())):
			self.selected_piece = piece
			self.start_square = (row, col)
			self.canvas.tag_raise("pieces")  # Ensure pieces are on top
			self.moves_highlight = cl.get_piece_moves(self, piece, (row, col))


	def on_piece_drag(self, event):
		"""Drag the selected piece."""
		if self.selected_piece:
			convert_selected_piece = self.pieces_dict[self.selected_piece]
			self.canvas.delete("drag")
			x = event.x - self.square_size // 2 - 20 #(-20 for image center cursor)
			y = event.y - self.square_size // 2 - 20 #(-20 for image center cursor)
			if not self.canvas.find_withtag("moves_highlight"):
				self.draw_legal_moves_line()
			self.canvas.create_image(x, y, anchor=tk.NW, image=self.piece_images_DRAG[convert_selected_piece], tags="drag")
			

	# Draw last move
	def draw_last_move(self, move):
		self.canvas.delete("last_move")
		start, end = move
		row1, col1 = start
		row2, col2 = end
		self.draw_highlight_after_move(row1, col1, color="#FFF1DB") #color light
		self.draw_highlight_after_move(row2, col2, color="#D4BDAC") #dark

	def draw_highlight_after_move(self, row, col, color="#FFF1DB"):
		x1 = col * self.square_size
		y1 = row * self.square_size
		x2 = x1 + self.square_size
		y2 = y1 + self.square_size
		self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color, tags="last_move")

	# Draw green circle for the piece click to show where it can move to
	def draw_legal_moves_line(self):
		if self.moves_highlight:
			for move in self.moves_highlight:
				start, end = move
				row, col = end
				self.draw_highlight_legal(row, col)

	def draw_highlight_legal(self, row, col, color="#DFF2EB"):
		size = 30
		# pos 1
		x1 = col * self.square_size + 25
		y1 = row * self.square_size + 25

		# pos 2
		x2 = x1 + 30
		y2 = y1 + 30
		self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline="black", tags="moves_highlight")

	def on_piece_drop(self, event):
		"""Drop the selected piece and update the board."""
		if not self.selected_piece:
			return

		col = event.x // self.square_size
		row = event.y // self.square_size
		end_square = (row, col)
		if self.is_valid_move(self.start_square, end_square):
			self.update_board(self.start_square, end_square)
			self.updateTurn()
			self.draw_last_move((self.start_square, end_square))

		self.reload()

		#bot search for best move
		if self.turn == 'b':
			self.window.after(100, self.play_bot)
			#self.play_bot()

	def reload(self):
		self.selected_piece = None
		self.start_square = None
		self.canvas.delete("drag")
		self.draw_pieces()
		self.moves_highlight = None
		self.canvas.delete("moves_highlight")

	def play_bot(self):
		chessbotgame = ChessGame()
		new_state = Statecopy(self)
		move = None
		# algorithm = self.cbo.get()
		# if algorithm and algorithm == "Alpha beta pruning search":
		move = alpha_beta_cutoff_search(
			state=new_state, game=chessbotgame, d=2, cutoff_test=None, eval_fn=None
		)
		# elif algorithm and algorithm == "Monte Carlo Tree Search":
		# 	move = monte_carlo_tree_search(state=new_state, game=chessbotgame, N=2)
		print('Bot search best move: ',move,' -- UCI:',cl.convert_to_uci_move(move))
		start_square, end_square = move
		self.update_board(start_square, end_square)
		self.updateTurn()
		self.draw_last_move(move)
		self.reload()

	def updateTurn(self):
		self.turn = 'b' if self.turn == 'w' else 'w'

	def is_valid_move(self, start, end):
		sx, sy = start
		ex, ey = end

		piece = self.board[sx][sy]
		target = self.board[ex][ey]

		#this is check for logic move of piece
		import sys
		moves = cl.get_piece_moves(self, piece, (sx, sy))
		if (start, end) in moves:
			print('Player Make move: ',(start, end), '- UCI: ',cl.convert_to_uci_move((start, end)))
			return True
		return False

	def update_board(self, start, end):
		"""Update the board state."""
		sx, sy = start
		ex, ey = end
		self.board[ex][ey] = self.board[sx][sy]
		self.board[sx][sy] = '.'
		#check promotion
		if self.board[ex][ey].lower()=='p' and (ex==7 or ex==0):
			print('promote')
			self.board[ex][ey] = "Q" if self.board[ex][ey].isupper() else "q"
		chessbotgame = ChessGame()
		new_state = Statecopy(self)
		if self.turn=="w":
			self.luot.config(text="Lượt chơi: Bot")
		else:
			self.luot.config(text="Lượt chơi: Bạn")
		if chessbotgame.terminal_test(new_state):
			self.label.config(fg="RED")
			if chessbotgame.to_move(new_state) == "w":
				self.label.config(text = "Tình trạng: Rất tiếc, bạn đã thua")
			else:
				self.label.config(text = "Xin chúc mừng!Bạn là người chiến thắng")


	def run(self):
		#loop to open main window
		self.window.mainloop()


# RUN
if	__name__ ==	"__main__":
	gameapp = MainApp()
	gameapp.run()
	