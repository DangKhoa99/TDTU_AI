### AI - Minimax Algorithm

from tkinter import *
from tkinter import messagebox
import random
## Khởi tạo board 3x3
## 0 1 2
## 3 4 5
## 6 7 8
boardGame = [None] * 9

## Các trường hợp thắng
winningCases = [[0, 1 ,2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]

## Hàm trả về các bước đi có sẵn (chưa đi)
def availableMoves(node):
	movesArr = []
	for x in range(9):
		if(None == node[x]):
			movesArr.append(x)
	return movesArr

## Kiểm tra xem game kết thúc chưa
def finish(node):
	fullBoard = True
	for x in range(9):
		if(node[x] == None):
			fullBoard = False
	if(fullBoard):
		return True
	if(winner(node) != None):
		return True
	return False

## Hàm trả về người thắng hoặc hòa = None
def winner(node):
	for player in ['X', 'O']:
		playerPositions = getSquares(player, node)
		for combo in winningCases:
			win = True
			for position in combo:
				if(position not in playerPositions):
					win = False
			if(win):
				return player
	return None

## Trả về ô người chơi đã đi
def getSquares(player, node):
	squares = []
	for x in range(9):
		if(node[x] == player):
			squares.append(x)
	return squares

## Thay ô trống bằng biểu tượng của người chơi
def makeMove(position, player, node):
	node[position] = player

## Thuật toán Minimax
def minimax(node, maxPlayer):
	## nếu trò chơi đã kết thúc, trả về:
	## -1 nếu thua,
	## 1 nếu thắng, 
	## 0 nếu hòa 
	## và node
	if(finish(node)):
		if(winner(node) == 'X'):
			return (1, node)
		elif(winner(node) == 'O'):
			return (-1, node)
		return (0, node)

	## MAX
	if(maxPlayer):
		best = -1
		bestMove = None
		## Đi qua từng node con vào gọi minimax
		for move in availableMoves(node):
			makeMove(move, 'X', node)
			value, choice = minimax(node, False)
			makeMove(move, None, node)
			## bestMove và best được cập nhật nếu value lớn hơn best trước đó
			if(value >= best):
				bestMove = move
				best = value
		return (best, bestMove)
	## MIN
	else:
		best = 1
		bestMove = None
		for move in availableMoves(node):
			makeMove(move, 'O', node)
			value, choice = minimax(node, True)
			makeMove(move, None, node)
			if(value <= best):
				bestMove = move
				best = value
		return (best, bestMove)

## Hàm sự kiện click vào màn hình
def update(event):
	global boardGame
	## Hoặc số lượng vị trí đi của 2 bên bằng nhau
	if len(getSquares('X', boardGame)) != len(getSquares('O', boardGame)):
		messagebox.showerror('ERROR', 'ERROR - Bấm chơi lại 1')
		return

	## Sự kiện nhấp chuột theo tọa độ điểm pixel
	if(event.x in range(1, 66) and event.y in range(1, 66)):
		if(boardGame[0] == None):
			boardGame[0] = 'O'
		else:
			return
	elif(event.x in range(68, 133) and event.y in range(1, 66)):
		if(boardGame[1] == None):
			boardGame[1] = 'O'
		else:
			return
	elif(event.x in range(135, 201) and event.y in range(1, 66)):
		if(boardGame[2] == None):
			boardGame[2] = 'O'
		else:
			return
	elif(event.x in range(1, 66) and event.y in range(68, 133)):
		if(boardGame[3] == None):
			boardGame[3] = 'O'
		else:
			return
	elif(event.x in range(69, 131) and event.y in range(68, 133)):
		if(boardGame[4] == None):
			boardGame[4] = 'O'
		else:
			return
	elif(event.x in range(135, 201) and event.y in range(68, 133)):
		if(boardGame[5] == None):
			boardGame[5] = 'O'
		else:
			return
	elif(event.x in range(1, 66) and event.y in range(135, 201)):
		if(boardGame[6] == None):
			boardGame[6] = 'O'
		else:
			return
	elif(event.x in range(68, 133) and event.y in range(135, 201)):
		if(boardGame[7] == None):
			boardGame[7] = 'O'
		else:
			return
	elif(event.x in range(135, 200) and event.y in range(135, 201)):
		if(boardGame[8] == None):
			boardGame[8] = 'O'
		else:
			return
	elif((event.x in range(67) and event.y in range(67)) or (event.x in range(134) and event.y in range(134))):
		messagebox.showerror('ERROR', 'Vui lòng bấm vào ô trống')
		return
	draw()
	## Nếu trò chơi đã kết thúc, thì end game sau khi lượt player đi
	if(finish(boardGame)):
		endboardGame()
		return 

	## Kiểm tra checkbox chọn mode trong giao diện
	if(easy.get() != 0):
		## Nếu không chọn chế độ dễ, gọi minimax
		print("hard")
		outcome, bestMove = minimax(boardGame, True)
		boardGame[bestMove] = 'X'
	else:
		## Chế độ dễ thì cho AI tự random chỗ đi
		print("easy")
		easyMove = randomMove(boardGame)
		boardGame[easyMove] = 'X'
	draw()
	# Kiểm tra trò chơi đã kết thúc, thì end game sau khi lượt AI đi
	if(finish(boardGame)):
		endboardGame()
		return

## Trả về bước đi random 
def randomMove(boardGame):
	return random.choice(availableMoves(boardGame))

## Hàm vẽ X, O trên màn hình giao diện
def draw():
	global boardGame
	count = 0
	## Tọa độ x, y theo điểm pixel
	for x in range(33, 167, 66):
		for y in range(33, 167, 66):
			if(boardGame[count] == None):
				symbol = ' '
			else:
				symbol = boardGame[count]

			if(symbol == 'X'):
				canvas.create_text((y, x), font = ('Arial', 50), text = symbol, fill = 'red', tag ='checked')
			else:
				canvas.create_text((y, x), font = ('Arial', 50), text = symbol, fill = 'blue', tag ='checked')
			count += 1
	root.update()

## Kết thúc game và đưa thông báo
def endboardGame():
	global boardGame
	if winner(boardGame) == 'X':
		messagebox.showinfo('NOTIFY', 'AI WIN :((')
	elif winner(boardGame) == 'O':
		messagebox.showinfo('NOTIFY', 'YOU WIN :))')
	else:
		messagebox.showinfo('NOTIFY', 'HÒA !!!')

## Chơi lại
def restart():
	global boardGame
	boardGame = [None] * 9
	canvas.delete('checked')
	draw()

## Khởi tạo GUI bởi Tkinter
root = Tk()
root.title('Cờ CARO')
root.geometry('300x300')

easy = IntVar() ## Giữ một số nguyên; giá trị mặc định 0
modes = ['Chế độ: Dễ', 'Chế độ: Khó']

for val, mode in enumerate(modes):
	Radiobutton(root, text = mode, variable = easy, value = val, padx = 50).pack(anchor = W)

reset = Button(root, text = 'Chơi lại', command = restart)
reset.pack()
canvas = Canvas(root, width = 200, height = 200, bg = 'tan')
canvas.bind('<Button-1>', update)
canvas.create_line(0, 67, 201, 67, width = 1)
canvas.create_line(0, 134, 201, 134, width = 1)
canvas.create_line(67, 0, 67, 201, width = 1)
canvas.create_line(134, 0, 134, 201, width = 1)
canvas.pack()

root.mainloop()