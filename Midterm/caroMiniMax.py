import numpy as np
import tkinter as tk
from tkinter import messagebox
from math import inf
import threading
import concurrent.futures

size = 12
cellSize = 40
center = (cellSize + 4)//2
fontSize = 30
board = np.full((size, size), ['.'])

def printBoard(board):
	for x in board:
		print(x)

def getPatterns(line, dict1, syms):
	i = 0
	s = ''
	
	while i < len(line):
		if line[i] == syms or line[i] == '.':
			if (i == 0):
				s += "0"
			elif line[i-1] != syms and line[i-1] != '.':
				s += "0"
			s += line[i]
			if (i == len(line) - 1):
				s += "0"
			elif line[i+1] != syms and line[i+1] != '.':
				s+= "0"
		if (line[i] != syms and line[i] != '.' or i == len(line) - 1):
			if s in dict1.keys():
				dict1[s] += 1
			else:
				dict1[s] = 1
			
			s = ''
		i+= 1
	
# Lấy theo hàng
def getPatternRow(patternDic, board):
	for i in range(board.shape[0]):
		getPatterns(board[i], patternDic, 'X')
	for i in range(board.shape[0]):
		getPatterns(board[i], patternDic, 'O')

# Lấy theo cột
def getPatternCol(patternDic, board):
	T = board.T
	for i in range(T.shape[0]):
		getPatterns(T[i], patternDic, 'X')
	for i in range(T.shape[0]):
		getPatterns(T[i], patternDic, 'O')

# Lấy đường chéo
def getPatternDiagonal(patternDic, board):
	for i in range(-board.shape[0] + 1, board.shape[0]):
		getPatterns(board.diagonal(i), patternDic, 'O')

	A = board[::-1, :]
	for i in range(-A.shape[0] + 1, A.shape[0]):
		getPatterns(A.diagonal(i), patternDic, 'O')
	
	for i in range(-board.shape[0] + 1, board.shape[0]):
		getPatterns(board.diagonal(i), patternDic, 'X')

	A = board[::-1, :]
	for i in range(-A.shape[0]+1, A.shape[0]):
		getPatterns(A.diagonal(i), patternDic, 'X')

def getAllPatterns(board):
	patternDic = {}
	getPatternRow(patternDic, board)
	getPatternCol(patternDic, board)
	getPatternDiagonal(patternDic, board)
	return patternDic

def winner(board):
	global patternDic, size
	patternDic = getAllPatterns(board)
	for key in patternDic:
		if('OOOOO' in key and key.count('0OOOOO0') == 0):
			return 'O'
		elif('XXXXX' in key and key.count('0XXXXX0') == 0):
			return 'X'
	return None

def finishGame(node):
	global size
	player = winner(node);
	fullBoard = True

	if(player != None):
		return (True, player)
	for i in range(size):
		for j in range(size):
			if (node[i][j] == "."):
				fullBoard = False
	return (fullBoard, player)

def checkInBoard(x, y, distance, direcx, direcy):
	# Tra ve nuoc di neu no nam trong bang
	global size
	y = y + distance * direcy
	x = x + distance * direcx
	if (0 <= y < size and 0 <= x < size):
		return (x, y)
	return None

def threadAvailableMove(direction, taken):
	availMove = []
	for direcx, direcy in direction:
		for x, y in taken:
			distance = 1
			# Kiem tra toa do co nam trong board
			move = checkInBoard(x, y, distance, direcx, direcy)
		
			if (move != None):
				if (move not in taken and move not in availMove):
					availMove.append(move)
	return availMove

def availableMove(board):
	# Trả về những nước gần trong phạm vi 3 ô của tất cả các nước đã đi
	global size
	# Những nước đã đi
	taken = []
	if (winner(board) != None):
		return []
	for x in range(size):
		for y in range(size):
			if (board[x][y] != '.'):
				taken.append((x, y))
	# print("Row 134", taken)
	direction1 = [(0,1),(0,-1),(1,0),(-1,0)]
	direction2 = [(1,1),(-1,-1),(-1,1),(1,-1)]
	availMove = []
	with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
		fu1 = executor.submit(threadAvailableMove, direction1, taken)
		fu2 = executor.submit(threadAvailableMove, direction2, taken)
		availMove.extend(fu1.result())
		availMove.extend(fu2.result())
	return set(availMove)

def getScore(board, player):
	patternDic = getAllPatterns(board)
	total = 0
	score = [0,0,2,9,15, 100000000]
	for key in patternDic:
		if (key.count(player*5) == 1 and key.count(".") >= 1):
			return score[5]
		if (key.count("0.") == 1 and key.count(".0") == 0) or (key.count("0.") == 0 and key.count(".0") == 1):
			if (key.count(player*4) == 1):
				total += 1000
			else:
				total += score[key.count(player)]
		if (key.count("0.") == 1 and key.count(".0") == 1):
			if (key.count(player) == 4):
				total += 10000
			total += key.count(player)*score[key.count(player)]
	return total 

def makeMove(x, y, player, board):
	board[x][y] = player

def minimax(node, maxPlayer, depth=3, alpha = -inf, beta = inf):

	if (depth == 1 or finishGame(node)[0]):
		return (getScore(node, "X") - getScore(node, "O"), None)
	moves = availableMove(node)
	## MAX
	if(maxPlayer):
		best = -inf
		bestMove = None
		## Đi qua từng node con vào gọi minimax
		
		while moves:
			move = moves.pop()
			x = move[0]
			y = move[1]
			makeMove(x, y, 'X', node)
			value = minimax(node, False, depth-1, alpha, beta)[0]
			makeMove(x, y, ".", node)
			## bestMove và best được cập nhật nếu value lớn hơn best trước đó
			if(value > best):
				bestMove = move
				best = value
			if (value >= beta):
				return (best, bestMove)
			alpha = max(value, alpha)
		
		return (best, bestMove)
	## MIN
	else:
		best = inf
		bestMove = None
		
		while (moves):
			move = moves.pop()
			x = move[0]
			y = move[1]
			makeMove(x, y, 'O', node)
			value = minimax(node, True, depth-1, alpha, beta)[0]
			makeMove(x, y, ".", node)
			if(value < best):
				bestMove = move
				best = value
			if (value <= alpha):
				return (best, bestMove)
			beta = min(value, beta)
			
		return (best, bestMove)
player = "X"

def endBoardGame(board):
	if(winner(board) == 'X'):
		messagebox.showinfo('NOTIFY', 'X WIN')
	elif(winner(board) == 'O'):
		messagebox.showinfo('NOTIFY', 'O WIN')
	else:
		messagebox.showinfo('NOTIFY', 'DRAW')

def drawX(x, y, player):
	global cells, moveHistory
	if (moveHistory is not None):
		cells[moveHistory[0]][moveHistory[1]].config(highlightbackground="#F4A460")
	moveHistory = (x, y)
	if (player == "O"):
		cells[x][y].create_text(
			(center, center),
			font = ('Bradley Hand ITC', fontSize, 'bold'),
			text = player,
			fill = 'blue', tag ='Checked')
	else:
		cells[x][y].create_text(
			(center, center),
			font = ('Bradley Hand ITC', fontSize, 'bold'),
			text = player,
			fill = 'black', tag ='Checked')
	cells[moveHistory[0]][moveHistory[1]].config(highlightbackground="red")

def thread1(board, x, y):
	global player
	playerWin = winner(board)
	# print("player win:", playerWin)
	
	if(v.get() != "1"):
		## Player - AI
		if(board[x][y] == '.' and playerWin == None):
			player = "O"
			makeMove(x, y, player, board)
			
			x1 = threading.Thread(target=drawX, args=(x, y, player))
			x1.start()

		else:
			return
		
		if(finishGame(board)[0]):
			endBoardGame(board)
			return
		## AI
		# print("hard")

		with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
			fu = executor.submit(minimax, board, True)

			bestMove = fu.result()[1]
			
			board[bestMove[0]][bestMove[1]] = 'X'
			player = "X"
			
			x = threading.Thread(target=drawX, args=(bestMove[0], bestMove[1], player))
			x.start()
			if(finishGame(board)[0]):
				endBoardGame(board)
				return
	else:
		## 2 player
		if(board[x][y] == '.' and playerWin == None):

			drawX(x, y, player)

			makeMove(x, y, player, board)
			if(player == "X"):
				player = "O"
			else:
				player = "X"
		else:
			return
		
		if(finishGame(board)[0]):
			# printBoard(board)
			endBoardGame(board)
			return
	
moveHistory = None
def motion(event):
	global board, player
	x = event.widget.positionX
	y = event.widget.positionY
	x = threading.Thread(target=thread1, args=(board, x, y))
	x.start()

def resetGame(event):
	global cells, size, board, player, moveHistory
	if (moveHistory != None):
		cells[moveHistory[0]][moveHistory[1]].config(highlightbackground="gray")
	# print("Reset Game")
	for row in cells:
		for x in row:
			x.delete("Checked")
	board = np.full((size, size), ['.'])
	player = "X"
	if (v.get() == "2"):
		moveFirst()

def isEmpty():
	global board, size
	for i in range(size):
		for j in range(size):
			if (board[i][j] != "."):
				return False
	return True

def moveFirst():
	global size, cells, player
	if (v.get() == "2"):
		if (isEmpty()):
			x = np.random.randint(size//2 - 2, size//2 + 2)
			y = np.random.randint(size//2 - 2, size//2 + 2)
			board[x][y] = "X"
			drawX(x, y, player)
			player = "O"
	else:
		resetGame(None)

root = tk.Tk()
root.title("Cờ caro")
cells = np.full((size, size), None)
count = 0

frameRoot = tk.Frame(
		master=root,
		relief=tk.RAISED,
		borderwidth=1
		)
frameRoot.grid(row=0, column=0)

# Tao che do choi
MODES = [
	("Mode: 2 players", "1"),
	("Mode: player - AI(first)", "2"),
	("Mode: player - AI(last)", "3"),
]

v = tk.StringVar()
v.set("1") # khoi tao

for text, mode in MODES:
	b = tk.Radiobutton(frameRoot, text=text,variable=v, value=mode, command = moveFirst)
	b.pack(anchor=tk.W)

# Tao button choi lai
btn = tk.Button(frameRoot, text="Chơi lại")
btn.bind("<Button-1>", resetGame)
btn.pack()
# Dong 1 chua ban co caro
frameRoot = tk.Frame(
	master=root,
	relief=tk.RAISED,
	borderwidth=1
)
frameRoot.grid(row=1, column=0)

for x in range(size):
	for y in range(size):
		frame = tk.Frame(
			master = frameRoot,
			relief = tk.RAISED,
			borderwidth = 1,
		)

		frame.grid(row = x, column = y, sticky = tk.N + tk.E + tk.S + tk.W)
		canvas = tk.Canvas(frame, width = cellSize, height = cellSize, bg = '#F4A460', highlightthickness=2, highlightbackground="#F4A460")
		canvas.bind("<Button-1>", motion)
		# canvas.create_text((center, 10), font = ('Arial', 8), text = "%d, %d"%(x,y))
		canvas.positionX = x
		canvas.positionY = y
		canvas.pack()
		cells[x][y] = canvas
		count += 1

root.mainloop()