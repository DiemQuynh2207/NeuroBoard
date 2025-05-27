import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw, ImageFont
import os
import chess as cl
from games4e import Game, alpha_beta_cutoff_search
import copy
import time


# Chessboard dimensions
BOARD_SIZE = 480  # Size of the chessboard in pixels
SQUARE_SIZE = BOARD_SIZE // 8

pieces_dict = {'P':'white_pawn', 'R':'white_rook', 'N':'white_knight', 'B':'white_bishop', 'Q':'white_queen', 'K':'white_king', 'p':'black_pawn', 'r':'black_rook', 'n':'black_knight', 'b':'black_bishop', 'q':'black_queen', 'k':'black_king'}


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

class EngineBoard:
	def __init__(self):
		self.board = self.initialize_board()
		self.turn = 'w'  # 'w' for white, 'b' for black

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

	def is_valid_move(self, start, end):
		sx, sy = start
		ex, ey = end

		piece = self.board[sx][sy]
		target = self.board[ex][ey]

		#this is check for logic move of piece
		moves = cl.get_piece_moves(self, piece, (sx, sy))
		if (start, end) in moves:
			return True
		return False

st.title("Chess")

# Generate a chessboard image
def create_chessboard():
	"""Create a chessboard image using PIL."""
	board = Image.new("RGBA", (BOARD_SIZE+20, BOARD_SIZE+20), "#2e2927")
	draw = ImageDraw.Draw(board)
	
	for row in range(8):
		for col in range(8):
			color = "#133E87" if (row + col) % 2 == 0 else "#CBDCEB"
			x1 = col * SQUARE_SIZE
			y1 = row * SQUARE_SIZE
			x2 = x1 + SQUARE_SIZE
			y2 = y1 + SQUARE_SIZE
			draw.rectangle([x1, y1, x2, y2], fill=color)
	path = os.getcwd()+"\\font\\BeVietnamPro-Bold.ttf"
	font = ImageFont.truetype(path, 13)
	for y, x in cl.square_file.items():
		#rank
		rank = abs(y-8)	
		draw.text((485.5, y*60+25), text=f"{rank}", font=font, fill="WHITE")
		#file
		draw.text((y*60+25, 482), text=x, font=font, fill="WHITE")
	return board

def getImg(name, size):
	piece_folder = os.getcwd()+"\\images\\imgs-80px"
	img = Image.open(os.path.join(piece_folder, f"{name}.png")).resize((size, size))
	return img

def draw_highlight_last(draw, lastmove, color):
	row, col = lastmove
	x1 = col * SQUARE_SIZE
	y1 = row * SQUARE_SIZE
	x2 = x1 + SQUARE_SIZE
	y2 = y1 + SQUARE_SIZE
	draw.rectangle([x1, y1, x2, y2], fill=color)

def draw_highlight_click(draw, move, color, type=1):
	row, col = move
	x1 = col * SQUARE_SIZE
	y1 = row * SQUARE_SIZE
	x2 = x1 + SQUARE_SIZE
	y2 = y1 + SQUARE_SIZE
	if type==1:
		draw.rectangle([x1, y1, x2, y2], fill=color)
	else:
		draw.ellipse([x1+15, y1+15, x2-15, y2-15],
				fill = color, outline ="BLACK")   

def load_piece(lastmove1=None, lastmove2=None, hightlightclick1=None):
	engine = st.session_state["board_engine"]
	img = copy.deepcopy(st.session_state["board_image_clear"])
	draw = ImageDraw.Draw(img)
	moves = None

	if lastmove1 and lastmove2:
		color1 = "#ebe665"
		color2 = "#fcf403"
		draw_highlight_last(draw, lastmove1, color1)
		draw_highlight_last(draw, lastmove2, color2)



	if hightlightclick1:
		color = "#D4BDAC"
		draw_highlight_click(draw, hightlightclick1, color)
		ex, ey = hightlightclick1
		piece = engine.board[ex][ey]
		moves = cl.get_piece_moves(engine, piece, hightlightclick1)
		moves = [end for _, end in moves]
		
	for row in range(8):
		for col in range(8):
			pchar = engine.board[row][col]
			if pchar != ".":
				pimg = getImg(pieces_dict[pchar], SQUARE_SIZE)
				img.paste(pimg, (col*SQUARE_SIZE, row*SQUARE_SIZE), pimg)
			if hightlightclick1:
				if (row, col) in moves:
					draw_highlight_click(draw, (row, col), "#DFF2EB", type=2)
	#update to board 		
	st.session_state["board_image"] = img

if "board_engine" not in st.session_state:
	bengine = EngineBoard()
	st.session_state["board_engine"] = bengine

if "board_image" not in st.session_state:
	st.session_state["board_image"] = create_chessboard()
	st.session_state["board_image_clear"] = copy.deepcopy(st.session_state["board_image"])
	load_piece()

# if "pieces" not in st.session_state:
# 	draw_piece()

col1, col2 = st.columns([8, 2])
with col1:
	#Reset dữ liệu
	if st.button("Reset board"):
		bengine = EngineBoard()
		print("button reset")
		st.cache_data.clear()
		st.session_state.clear()
		st.cache_resource.clear()
		st.session_state["board_engine"] = bengine
		st.session_state["board_image"] = create_chessboard()
		st.session_state["board_image_clear"] = copy.deepcopy(st.session_state["board_image"])
		st.session_state["diem"] = 1
		st.session_state["pos1"] = (-1, -1)
		st.session_state['key'] = 1
		st.session_state['highlight1'] = 1
		st.session_state["error"] = 1

		print("Reload")
		load_piece()
		st.rerun()

def move_piece(pos1, pos2):
	engine = st.session_state["board_engine"]
	if engine.is_valid_move(pos1, pos2):
		engine.updateTurn()
		engine.update_board(pos1, pos2)
		load_piece(pos1, pos2)

def play_bot():
	engine = st.session_state["board_engine"]
	print("play bot")
	chessbotgame = ChessGame()
	new_state = Statecopy(engine)
	move = None
	move = alpha_beta_cutoff_search(
		state=new_state, game=chessbotgame, d=2, cutoff_test=None, eval_fn=None
	)
	start, end = move
	row, col = start
	piecesstr = pieces_dict[engine.board[row][col]]
	engine.update_board(start, end)
	engine.updateTurn()
	load_piece(start, end)
	return piecesstr, move

	

if "diem" not in st.session_state:
	st.session_state["diem"] = 1
	st.session_state["pos1"] = (-1, -1)
	st.session_state['key'] = 1
	st.session_state['highlight1'] = 1
	st.session_state["error"] = 1
	print("Reload")

def load_canvas():
	global canvas_result
	canvas_result = st_canvas(
		stroke_width = 1,
		stroke_color = '',
		background_image=st.session_state["board_image"],
		height=BOARD_SIZE+20,
		width=BOARD_SIZE+20,
		drawing_mode="point",
		point_display_radius=0,
		display_toolbar=False,
		key=f"canvas_1",
	)
with col1:
	load_canvas()


with col2:
	if canvas_result.json_data is not None:
		objs = canvas_result.json_data.get("objects", [])
		if objs and objs[-1]["type"] =="circle":
			left = objs[-1]["left"]
			top = objs[-1]["top"]
			
			st.write("click",left, top, st.session_state["diem"])
			col = int(left // SQUARE_SIZE)
			row = int(top // SQUARE_SIZE)
			if not (col < 0 or col > 7 or row < 0 or row > 7):
				engine = st.session_state["board_engine"]
				if engine.turn=="w":
					if st.session_state["diem"] == 1 and st.session_state["key"] ==1 and st.session_state["error"] == 1:
						if cl.is_friendly_piece(engine, row, col):
							st.write("Bạn đang chọn: ", getImg(pieces_dict[engine.board[row][col]], 50), "Vị trí: ",f"{cl.square_file[col]}{cl.square_rank[row]}")
							st.write("Hãy click vị trí muốn di chuyển đến")
							st.session_state["pos1"] = (row, col)
							st.session_state["diem"] = 2
							st.session_state['key'] = 1
							st.session_state['highlight1'] = 2
							load_piece(hightlightclick1=(row, col))
							st.rerun()

							#st.session_state['key'] = 5
					elif st.session_state["diem"] == 2 and st.session_state["key"] == 1 and st.session_state["highlight1"] == 2:
						st.session_state["highlight1"] = 3
						st.write("Bạn đang chọn: ", getImg(pieces_dict[engine.board[row][col]], 50), "Vị trí: ",f"{cl.square_file[col]}{cl.square_rank[row]}")
						st.write("Hãy click vị trí có ô tròn màu xanh muốn di chuyển đến")
					elif st.session_state["diem"] == 2 and st.session_state["key"] == 1 and st.session_state["highlight1"] == 3:
						print("run so 2")
						if cl.is_empty(engine, row, col) or not cl.is_friendly_piece(engine, row, col):
							pos1 = st.session_state["pos1"]
							pos2 = (row,col)
							if engine.is_valid_move(pos1, pos2):
								rowp1, colp1 = pos1
								piecesstr = pieces_dict[engine.board[rowp1][colp1]]
								move_piece(pos1, pos2)
								pos1uci = f"{cl.square_file[colp1]}{cl.square_rank[rowp1]}"
								pos2uci = f"{cl.square_file[col]}{cl.square_rank[row]}"
								st.session_state["diem"] = 1
								st.session_state['key'] = 2
								st.session_state['uci1']  = pos1uci
								st.session_state['uci2']  = pos2uci
								st.session_state['pstr']  = piecesstr
								st.success("Đi thành công")
								st.cache_data.clear()
								st.rerun()
																

							else:
								load_piece()
								st.session_state["error"] = 2
								st.session_state["key"] = 1
								st.session_state["diem"] = 1
								st.rerun()
						else:
							load_piece()
							st.session_state["error"] = 2
							st.session_state["key"] = 1
							st.session_state["diem"] = 1
							st.rerun()
							
						st.session_state["diem"] = 1

with col2:
	if st.session_state["error"] == 2:
		st.error("Nước đi không hợp lệ")
		st.session_state["error"] = 1
			
with col2:
	if st.session_state["diem"] == 1 and st.session_state['key'] == 2:
		print("run bot 1")
		pbotstr, move = play_bot()
		st.session_state['key'] = 3
		st.session_state["diem"] = 1
		st.session_state["pbot"] = pbotstr
		st.session_state["move"] = move
		st.rerun()
		print("after run 1")

	if st.session_state["diem"] == 1 and st.session_state['key'] == 3:
		print("run bot 2")
		piecesstr = st.session_state['pstr']
		pos1uci = st.session_state['uci1']
		pos2uci = st.session_state['uci2']
		pbotstr = st.session_state["pbot"]
		move = st.session_state["move"]
		print(pos1uci)
		st.success("Đi thành công")
		st.write('Bot đã tìm nước đi tốt nhất')
		st.write(getImg(pbotstr, 50))
		st.write(cl.convert_to_uci_move(move))
		st.success("Bot đã di chuyển")
		st.session_state['key'] = 1
