import pandas as pd
import random as rd
import csv
from math import inf
from concurrent.futures import ThreadPoolExecutor
from time import time
import numpy
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

class GeneticScheduler():

	def threadInit(self, fileName, typeFile):
		if (typeFile == 1):
			with open(fileName) as f:
				data = csv.reader(f)
				for row in data:
					for col in row:
						self.classRoom.append(col)

		elif (typeFile == 2):
			tmp = pd.read_csv(fileName).values
			for row in tmp:
				try:
					self.lecturers[row[0]] = row[1].split(';') 
				except:
					self.lecturers[row[0]] = []

		elif (typeFile == 3):
			tmp = pd.read_csv(fileName).values
			for row in tmp:
				self.subjects[str(row[0])] = row[1:]

	def __init__(self, fileClassRoom = 'classrooms.csv', fileLecture = 'lecturers.csv', fileSubject = 'subjects.csv'):
		self.classRoom = []		# List phòng học
		self.lecturers = {}		# Dict giảng viên
		self.subjects = {}		# Dict môn học
		self.populations = []	# List quần thể

		with ThreadPoolExecutor(max_workers = 3) as executor:
			executor.submit(self.threadInit(fileClassRoom, 1))
			executor.submit(self.threadInit(fileLecture, 2))
			executor.submit(self.threadInit(fileSubject, 3))

	# Hàm tạo quần thể
	def createPopulations(self, n = 100):	
		lecturerId = self.lecturers.keys()
		print("Create: ", lecturerId)

		totalClasses = 0 # Tổng số lớp
		for x in self.subjects.values():
			totalClasses += x[-1] # Col solop

		i = 0
		while (i < n):
			self.populations.append(self.createGen(lecturerId, totalClasses // len(lecturerId) + 1))
			i += 1

	def myRandom(self, typeRandom):
		if (typeRandom == 0): # Ca
			shift = rd.randint(0, 3) # Random 4 ca học [0, 1, 2, 3]
			return shift
		elif (typeRandom == 1): # Thứ
			weekDays = numpy.random.choice(numpy.arange(0, 7), p=[0.19, 0.18, 0.18, 0.18, 0.17, 0.08, 0.02]) # Random 7 thứ [0, 1, 2, 3, 4, 5, 6] ~~ [T2, T3, T4, T5, T6, T7, CN]
			return weekDays
		else:
			return 0

	# Hàm tạo gen
	def createGen(self, lecturerId, n = 3):
		gen = {key: [] for key in lecturerId}
		scheduleRoom = [[[] for i in range(7)] for j in range(4)]
		
		for _id in lecturerId:
			numShifts = rd.randint(n - 1, n)
			haveShifts = [] # Chứa những ca được sắp xếp để tránh bị trùng lặp

			for i in range(numShifts):
				if (self.lecturers[_id] == [] or self.lecturers[_id] == None):
					continue

				subjectCode = rd.choice(self.lecturers[_id])
				shift = self.myRandom(0)
				weekDays = self.myRandom(1)

				while ([weekDays, shift] in haveShifts):
					shift = self.myRandom(0)
					weekDays = self.myRandom(1)

				room = rd.choice(self.classRoom)

				while (room in scheduleRoom[shift][weekDays]):
					room = rd.choice(self.classRoom)
				
				haveShifts.append([weekDays, shift])
				scheduleRoom[shift][weekDays].append(room)
				gen[_id].append([subjectCode, room, weekDays, shift])
		return gen
	
	# Hàm đánh giá gen
	# *type1 dung de debug
	def rateGen(self, gen, scheduleRoom, type1 = 1):
		rate = 10000 # Để cho số nó ra dương cho đẹp
		test = {idMH: 0 for idMH in self.subjects.keys()}

		# Đánh giá tiêu chí số lớp được mở
		for val in gen.values():	# Đếm số lớp của từng môn trong GEN
			if (type(val) != int):
				for idMH in val:
					test[idMH[0]] += 1

		for idMH in self.subjects.keys(): # So sánh kết quả với dữ liệu và tính rate
			if (type1 == 0):
				print("%s - real = %d - new = %d - sub = %d"%(idMH, self.subjects[idMH][-1], test[idMH], abs(self.subjects[idMH][-1] - test[idMH])))
			# Dù chỉ lệch một lớp cũng bị trừ điểm cực nặng -> Không thể lên top
			rate -= abs(self.subjects[idMH][-1] - test[idMH]) * 10000
		
		if (type1 == 0):
			print("B1 = ", rate)

		# Đánh giá độ chênh lệch số ca dạy của giảng viên
		maxNumShifts = -inf
		minNumShifts = inf
		distance = 0 # Tổng khoảng cách giữa các các phòng của một giảng viên trong cùng một ngày

		for _id, val in gen.items():
			if (val is None or val == []):
				continue

			if (type(val) != int):
				# Tìm số lượng max, min
				if (len(val) > maxNumShifts):
					maxNumShifts = len(val)
				if (len(val) < minNumShifts):
					minNumShifts = len(val)

				# Đánh giá khoảng cách giữa các phòng khi có các ca trong cùng một ngày
				gen[_id] = sorted(val, key=lambda x: x[2]) # sắp xếp theo thứ
				nowWeekDay = gen[_id][0][2]
				nowRoom = gen[_id][0][1]

				for x in gen[_id][1:]: 
					if (nowWeekDay == x[2]): # Cùng ngày thì tính khoảng cách
						distance += abs(int(x[1]) - int(nowRoom))
					nowWeekDay = x[2]
					nowRoom = x[1]
		
		rate = rate - (maxNumShifts - minNumShifts) * 1000
		if (type1 == 0):
			print("B2 Đánh giá ca dạy = ", rate)
			print("MAX ca = %d - MIN ca = %d"%(maxNumShifts, minNumShifts))

		rate = rate - distance * 5
		if (type1 == 0):
			print("B3 Đánh giá khoảng cách phòng = ", rate)

		# Đánh giá số lượng phòng được dùng
		counterRoom = []
		for shift in range(4):
			for weekday in range(7):
				counterRoom.extend(scheduleRoom[shift][weekday])
		
		rate = rate - len(set(counterRoom)) * 10
		if (type1 == 0):
			print("B4 = ", rate)
		return rate
	
	def rateAllGen(self):
		i = 0
		n = len(self.populations)
		self.threadRateGens(i, n)

	def threadRateGens(self, i, n):
		while (i < n):
			genTmp = self.populations[i]

			scheduleRoom = [[[] for i in range(7)] for j in range(4)]
			
			for val in genTmp.values():
				if (type(val) != int):
					for idMH, room, weekDays, shift in val:
						scheduleRoom[shift][weekDays].append(room)
			
			self.populations[i]["rate"] = self.rateGen(self.populations[i], scheduleRoom)
			i += 1

	# Hàm chọn lọc
	def selectGen(self, percent):
		num = int(percent * (len(self.populations)))
		self.populations = sorted(self.populations, key=lambda x: x["rate"], reverse=True)
		self.populations = self.populations[0:num]

	# Hàm lai ghép
	def hybridGen(self):
		n = len(self.populations)
		for times in range(n):
			father = rd.randint(0, len(self.populations) - 1)
			mother = rd.randint(0, len(self.populations) - 1)
			con = self.populations[father].copy()

			while (mother == father): # Đảm bảo không bị trùng
				mother = rd.randint(0, len(self.populations) - 1)
			
			for _id in con.keys():
				if (rd.randint(0,1) == 1):
					con[_id] = self.populations[mother][_id]
			
			self.populations.append(con)

	# Hàm đột biến
	def mutationGen(self):
		lecturerId = list(self.lecturers.keys())

		# Random một cá thể bất kỳ
		index = rd.randint(0, len(self.populations) - 1)
		new = self.populations[index].copy()

		# Đối với đột biến kiểu thêm vào hoặc mất đi
		scheduleRoom = [[[] for i in range(7)] for j in range(4)]

		for val in self.populations[index].values():
			if (type(val) != int):
				for idMH, room, weekDays, shift in val:
					scheduleRoom[shift][weekDays].append(room)

		_id = rd.choice(lecturerId)

		while (self.lecturers[_id] is None or self.lecturers[_id] == []):
			_id = rd.choice(lecturerId)

		typeMutation = rd.randint(0, 2)
		if (typeMutation == 0):
			# đột biến kiểu thêm vào
			haveShifts = [[x[2], x[3]] for x in new[_id]]
			shift = self.myRandom(0)
			weekDays = self.myRandom(1)
			
			while ([weekDays, shift] in haveShifts):
				shift = self.myRandom(0)
				weekDays = self.myRandom(1)
				
			subjectCode = rd.choice(self.lecturers[_id])
			room = rd.choice(self.classRoom)

			while (room in scheduleRoom[shift][weekDays]):
				room = rd.choice(self.classRoom)
			
			new[_id].append([subjectCode, room, weekDays, shift])
		else:
			if (typeMutation == 1):
				# đột biến kiểu xóa bớt một NST
				while (len(new[_id]) <= 1):
					_id = rd.choice(lecturerId)
				removeId = rd.randint(0, len(new[_id]) - 1)
				new[_id].pop(removeId)

			elif (typeMutation == 2):
				# đột biến kiểu thay đổi
				haveShifts = [[x[2], x[3]] for x in new[_id]]
				shift = self.myRandom(0)
				weekDays = self.myRandom(1)

				while ([weekDays, shift] in haveShifts):
					shift = self.myRandom(0)
					weekDays = self.myRandom(1)

				subjectCode = rd.choice(self.lecturers[_id])
				room = rd.choice(self.classRoom)

				while (room in scheduleRoom[shift][weekDays]):
					room = rd.choice(self.classRoom)

				new[_id][rd.randint(0, len(new[_id]) - 1)] = [subjectCode, room, weekDays, shift]
		self.populations.append(new)

	def mutationGens(self, n = 1):
		# with ThreadPoolExecutor(max_workers=3) as executor:
		i = 0
		while (i < n):
			# executor.submit(self.mutationGen())
			self.mutationGen()
			i += 1

	def schedule(self, n = 200, percent = 0.5): # percent phải >= 0,5
		i = 0
		start = time()

		# Tạo quần thể
		self.populations = []
		self.createPopulations(100)


		while(i < n):
			self.rateAllGen()
			self.selectGen(percent)
			self.hybridGen()
			self.mutationGens()
			i += 1

		end = time()
		print("Thời gian tính toán: ", (end - start))
	
	def getSchedule(self):
		self.rateAllGen()
		self.populations = sorted(self.populations, key=lambda x: x["rate"], reverse=True)
		return self.populations[0]

## GUI
# Dành cho các ô có i|j == 0
WIDTH_0 = 80
HEIGHT_0 = 40
CENTER_0_X = (WIDTH_0 + 4) //2
CENTER_0_Y = (HEIGHT_0 + 4) //2
BACKGROUND_COLOR_0 = '#006dcc'

# Dành cho phần còn lại
WIDTH_K = 120
HEIGHT_K = 120
CENTER_K_X = (WIDTH_K + 4) //2
CENTER_K_Y = (HEIGHT_K + 4) //2
BACKGROUND_COLOR = 'white'

FONT = 'Arial bold'
FONT_SIZE = 10
FILL = 'white'

class GraphicSchedule(tk.Frame):
	def __init__(self, parent, genetic):
		tk.Frame.__init__(self, parent)
		self.genetic = genetic
		self.colorCode = {key: self.randomColorCode() for key in self.genetic.subjects.keys()}
		self.parent = parent
		self.widgetCell = [[None for i in range(7)] for j in range(4)]
		self.control = []
		self.info = []
		self.subjects = []
		self.optionsMenus = []
		self.forms = []

		dataLecturers = pd.read_csv('lecturers_info.csv').values

		for row in dataLecturers:
			self.info.append("%s - %s"%(row[0], row[1]))
		self.initUI()

	def initUI(self):
		self.parent.title("Schedule System")
		tabControl = ttk.Notebook(self.parent)

		tab1 = ttk.Frame(tabControl)
		tabControl.add(tab1, text="Thời khóa biểu")
		self.createTabSchedule(tab1)
		
		tab2 = ttk.Frame(tabControl)
		tabControl.add(tab2, text="Sửa dữ liệu")
		self.createTabForm(tab2)

		tab3 = ttk.Frame(tabControl)
		tabControl.add(tab3, text="Thêm dữ liệu")
		self.createTabForm(tab3, 0)

		tabControl.pack(expand=1, fill="both")

	def callbackTmp(self, *args):
		index = int(*args[0][-1])
		print(args)
		print(self.control[index].get())
		if (index == 0):
			_id = self.control[0].get().split(' - ')[0]
			try:
				self.fillTable(self.genetic.getSchedule()[int(_id)])
			except:
				messagebox.showinfo('NOTIFY', "Dữ liệu vừa cập nhật hãy sắp lịch lại")
		else:
			data = {}
			if (index == 1):
				idGV, nameGV = self.control[index].get().split(' - ')
				subject = ';'.join(self.genetic.lecturers[int(idGV)])
				data = {
					'idGV': idGV.strip(),
					'name': nameGV.strip(),
					'subjects': subject.strip()
				}
			else:
				idMH, nameMH = self.control[index].get().split(' - ')
				idMH = idMH.strip()
				sotiet = self.genetic.subjects[idMH][-2]
				solop = self.genetic.subjects[idMH][-1]
				data = {
					"maMH": idMH,
					"nameMH": nameMH.strip(),
					"sotiet": sotiet,
					"solop": solop
				}
			self.forms[index-1].fillEntrys(data)

	def createTabSchedule(self, tab1):
		# Tạo OptionMenu
		frameRoot = tk.Frame(
			master=tab1,
			relief=tk.RAISED,
			borderwidth=2,
			padx=5
		)
		frameRoot.grid(row=0, column=0, sticky="snew")

		self.control.append(tk.StringVar(frameRoot))
		self.control[0].set(self.info[0])
		self.control[0].trace('w', self.callbackTmp)
		optionsMenu = tk.OptionMenu(
			frameRoot,
			self.control[0],
			*self.info
		)
		optionsMenu.pack(side = tk.LEFT)
		self.optionsMenus.append(optionsMenu)

		# Thêm LABEL
		label = tk.Label(frameRoot, text = "THỜI KHÓA BIỂU")
		label.config(font=("Arial bold", 12))
		label.place(in_=frameRoot, anchor="c", relx=.5, rely=.5)

		# Thêm Button
		btn = tk.Button(
			frameRoot,
			text = "Refresh",
			padx=3
		)
		btn.bind("<Button-1>", self.refresh)
		btn.pack(side=tk.RIGHT)

		btn = tk.Button(
			frameRoot,
			text = "Save",
			padx=3
		)
		btn.bind("<Button-1>", self.saveSchedule)
		btn.pack(side = tk.RIGHT)

		# Vẽ thời khóa biểu
		frameRoot = tk.Frame(
			master=tab1,
			relief=tk.RAISED,
			borderwidth=2,
		)
		frameRoot.grid(row=1, column=0, sticky="snew")
		shifts = [0, 1, 2, 3, 4]
		weekDays = ["Ca|Thứ", "Thứ hai", "Thứ ba", "Thứ tư", "Thứ năm", "Thứ sáu", "Thứ bảy", "Chủ Nhật"]
		
		for i in shifts: #row
			for j in range(len(weekDays)): #col
				frame = tk.Frame(
					master=frameRoot,
					relief=tk.RAISED,
					borderwidth=0,
					highlightthickness=1,
					highlightbackground='black'
				)
				frame.grid(row=i, column=j, sticky="snew")
				if (j == 0):
					if (i != 0):
						frame.config(highlightthickness = 0)
						canvas = tk.Canvas(
							frame,
							width=WIDTH_0,
							height= HEIGHT_K,
							bg=BACKGROUND_COLOR_0,
							highlightthickness=1,
							highlightbackground='white'
						)
						canvas.create_text(
							(CENTER_0_X, CENTER_K_Y),
							font = (FONT, FONT_SIZE + 3),
							text=str(i),
							fill='white'
						)
						canvas.pack()
					else:
						frame.config(highlightthickness = 0)
						canvas = tk.Canvas(
							frame, width=WIDTH_0,
							height=HEIGHT_0,
							bg=BACKGROUND_COLOR_0,
							highlightthickness=1,
							highlightbackground='white'
						)
						canvas.create_text(
							(CENTER_0_X ,CENTER_0_Y),
							font = (FONT, FONT_SIZE),
							text=weekDays[j],
							fill='white'
						)
						canvas.pack()
				else:
					if (i == 0):
						frame.config(highlightthickness = 0)
						canvas = tk.Canvas(
							frame,
							width=WIDTH_K,
							height=HEIGHT_0,
							bg=BACKGROUND_COLOR_0,
							highlightthickness=1,
							highlightbackground='white'
							
						)
						canvas.create_text(
							(CENTER_K_X , CENTER_0_Y),
							font = (FONT, FONT_SIZE),
							text=weekDays[j],
							fill='white'
						)
						canvas.pack()
					else:
						canvas = tk.Canvas(
							frame,width=WIDTH_K,
							height=HEIGHT_K,
							bg=BACKGROUND_COLOR,
							highlightthickness=0,
						)
						canvas.create_text(
							(CENTER_K_X ,CENTER_K_Y),
							font = (FONT, FONT_SIZE),
							text="TMP",
							tag="text",
							fill = FILL
						)
						canvas.pack()
						self.widgetCell[i-1][j-1] = canvas
		
		schedule = self.genetic.getSchedule()
		self.fillTable(schedule[list(schedule.keys())[0]])
	
	def createTabForm(self, tab, type1=1):
		frameRoot = tk.Frame(
			master=tab,
			relief=tk.RAISED,
			borderwidth=2,
			padx=5,
			height=50
		)

		# Thêm LABEL
		if(type1 == 1):
			label = tk.Label(frameRoot, text = "SỬA DỮ LIỆU")
		else:
			label = tk.Label(frameRoot, text = "THÊM DỮ LIỆU")

		label.config(font=("Arial bold", 15))
		label.place(in_=frameRoot, anchor="c", relx=.5, rely=.5)

		frameRoot.grid(row=0, column=0, sticky="snew")

		# Form của lecturer
		frameRoot = tk.Frame(
			master=tab,
			relief=tk.RAISED,
			borderwidth=2,
			padx=5
		)

		# Thêm LABEL
		label = tk.Label(frameRoot, text = "GIÁO VIÊN")
		label.config(font=("Arial bold", 12))
		label.place(in_=frameRoot, anchor="c", relx=.5, rely=.5)
		
		if (type1 == 1):
			self.control.append(tk.StringVar(frameRoot))
			self.control[-1].set(self.info[0])
			self.control[-1].trace('w', self.callbackTmp)
			optionsMenu = tk.OptionMenu(
				frameRoot,
				self.control[-1],
				*self.info
			)
			optionsMenu.pack(side = tk.LEFT)
			self.optionsMenus.append(optionsMenu)

			btn = tk.Button(frameRoot, text = "Delete") 
			btn.bind("<Button-1>", self.deleteData)
			btn.pack(side = tk.RIGHT)
			btn.id = 0

		btn = tk.Button(frameRoot, text = "Save") 
		btn.bind("<Button-1>", self.saveData) # btn được đánh id để phân biệt
		btn.pack(side = tk.RIGHT)
		frameRoot.grid(row=1, column=0, sticky="snew")
		
		frameRoot = tk.Frame(
			master=tab,
			relief=tk.RAISED,
			borderwidth=2,
			padx=5
		)

		if (type1 == 1):
			idGV, nameGV = self.info[0].split(" - ")
			subject = ';'.join(self.genetic.lecturers[int(idGV)])
		else:
			idGV = str(len(self.genetic.lecturers.keys()) + 1)
			nameGV = ""
			subject = ""

		data = {
			'idGV': ['Mã giáo viên', idGV.strip()],
			'name': ['Tên giáo viên', nameGV.strip()],
			'subjects': ["Mã môn học", subject.strip()]
		}
		form1 = Form(frameRoot, data, type1)
		form1.pack()
		self.forms.append(form1)
		btn.id = len(self.forms) - 1
		frameRoot.grid(row=2, column=0, sticky="snew")

		# Form cua mon hoc
		frameRoot = tk.Frame(
			master=tab,
			relief=tk.RAISED,
			borderwidth=2,
			padx=5
		)

		label = tk.Label(frameRoot, text = "MÔN HỌC")
		label.config(font=("Arial bold", 12))
		label.place(in_=frameRoot, anchor="c", relx=.5, rely=.5)

		if (type1 == 1):
			for key in self.genetic.subjects.keys():
				self.subjects.append("%s - %s" % (key, self.genetic.subjects[key][0]))

			self.control.append(tk.StringVar(frameRoot))
			self.control[-1].set(self.subjects[0])
			self.control[-1].trace('w', self.callbackTmp)
			optionsMenu = tk.OptionMenu(
				frameRoot,
				self.control[-1],
				*self.subjects
			)
			optionsMenu.pack(side = tk.LEFT)
			self.optionsMenus.append(optionsMenu)
			
			btn = tk.Button(frameRoot, text = "Delete") 
			btn.bind("<Button-1>", self.deleteData)
			btn.pack(side = tk.RIGHT)
			btn.id = 1

		btn = tk.Button(frameRoot, text = "Save")
		btn.bind("<Button-1>", self.saveData) # btn được đánh id để phân biệt
		btn.pack(side = tk.RIGHT)

		frameRoot.grid(row=3, column=0, sticky="snew")
		frameRoot = tk.Frame(
			master=tab,
			relief=tk.RAISED,
			borderwidth=2,
			padx=5
		)
		frameRoot.grid(row=4, column=0, sticky="snew")
		
		if (type1 == 1):
			idMH, nameMH = self.subjects[0].split('-')
			idMH = idMH.strip()
			sotiet = self.genetic.subjects[idMH][-2]
			solop = self.genetic.subjects[idMH][-1]
		else:
			idMH = ""
			nameMH = ""
			sotiet = 0
			solop = 0
			
		data = {
			"maMH": ["Mã môn học", idMH],
			"nameMH": ["Tên môn học", nameMH.strip()],
			"sotiet": ["Số tiết", sotiet],
			"solop": ["Số lớp", solop]
		}

		form = Form(frameRoot, data, type1)
		form.pack()
		self.forms.append(form)
		btn.id = len(self.forms) - 1

	def saveData(self, event):
		btnID = event.widget.id
		print("Saving data", btnID)
		data = self.forms[btnID].getAllFileds()

		print("________________________________________________\n")
		for x, y in data.items():
			print(x, y)
		print("________________________________________________")

		check = self.checkEmpty(data)
		if (check != None):
			messagebox.showinfo('NOTIFY', "%s không được để trống!"%(data[check][0]))
			return
		else:
			if (btnID == 0):
				try:
					# Cập nhật self.info
					idGV = int(data["idGV"][1])
					for i in range(len(self.info)):
						if (int(self.info[i].split(" - ")[0]) == idGV):
							self.info[i] = "%s - %s"%(idGV, data["name"][1])
							current = i
					
					# Cập nhật self.genetic.lecturers
					self.genetic.lecturers[idGV] = data["subjects"][1].split(";")

					# Ghi đè lên file lecturers.csv, lecturers_info.csv
					self.overWriteFileCsv(0)
					
					# Cập nhật lại optionMenu
					for i in range(2):
						self.control[i].set(self.info[current])
						self.optionsMenus[i]['menu'].delete(0, 'end')

						for option in self.info:
							self.optionsMenus[i]['menu'].add_command(label=option, command=tk._setit(self.control[i], option))

					messagebox.showinfo('NOTIFY', "Save succes!")
				except:
					messagebox.showinfo('NOTIFY', "Save error!")

			elif (btnID == 1):
				try:
					# Cập nhật self.subjects
					maMH = data["maMH"][1]
					for i in range(len(self.subjects)):
						if (self.subjects[i].split(" - ")[0] == maMH):
							self.subjects[i] = "%s - %s" %(maMH, data["nameMH"][1])
							current = i
					
					# Cập nhật self.genetic.subjects
					self.genetic.subjects[maMH] = [data["nameMH"][1], int(data["sotiet"][1]), int(data["solop"][1])]
					
					self.overWriteFileCsv(1)
					
					# Cập nhật lại optionMenu
					self.control[2].set(self.subjects[current])
					self.optionsMenus[2]['menu'].delete(0, 'end')

					for option in self.subjects:
						self.optionsMenus[2]['menu'].add_command(label=option, command=tk._setit(self.control[2], option))

					# Thêm mã màu mới
					self.colorCode[maMH] = self.randomColorCode()	
					messagebox.showinfo('NOTIFY', "Save succes!")
				except:
					messagebox.showinfo('NOTIFY', "Save error!")

			elif (btnID == 2):
				try:
					idGV = int(data["idGV"][1])
					for _idGV in self.genetic.lecturers.keys():
						if(idGV == _idGV):
							messagebox.showinfo('NOTIFY', "Mã giáo viên đã tồn tại")	
							return

					# Thêm vào info
					self.info.append("%s - %s"%(idGV, data["name"][1]))

					# Thêm vào lecturers
					self.genetic.lecturers[idGV] = data["subjects"][1].split(";")
					
					# Ghi đè lên file lecturers.csv, lecturers_info.csv
					self.overWriteFileCsv(0)

					# Cập nhật lại optionMenu
					for i in range(2):
						option = self.info[-1]
						self.optionsMenus[i]['menu'].add_command(label=option, command=tk._setit(self.control[i], option))

					messagebox.showinfo('NOTIFY', "Add succes!")
				except:
					messagebox.showinfo('NOTIFY', "Add error!")
				self.forms[btnID].clear(1)

			elif (btnID == 3):
				try:
					maMH = data["maMH"][1]
					for maMHH in self.genetic.subjects.keys():
						if(maMH == maMHH):
							messagebox.showinfo('NOTIFY', "Mã môn học đã tồn tại")	
							return

					self.subjects.append("%s - %s" %(maMH, data["nameMH"][1]))

					if(int(data["sotiet"][1]) < 3 or int(data["solop"][1]) < 1):
						messagebox.showinfo('NOTIFY', "Số tiết >= 3 hoặc số lớp >= 1")	
						return
					print("continue.....")

					self.genetic.subjects[maMH] = [data["nameMH"][1], int(data["sotiet"][1]), int(data["solop"][1])]
						
					self.overWriteFileCsv(1)

					# Cập nhật lại optionMenu
					option = self.subjects[-1]
					self.optionsMenus[2]['menu'].add_command(label=option, command=tk._setit(self.control[2], option))

					# Thêm mã màu mới
					self.colorCode[maMH] = self.randomColorCode()
					messagebox.showinfo('NOTIFY', "Add succes!")
				except:
					messagebox.showinfo('NOTIFY', "Add error!")
				self.forms[btnID].clear()
	
	def deleteData(self, event):
		btnID = event.widget.id
		_id = ''
		if (btnID == 0):
			try:
				index = self.info.index(self.control[1].get())
				print("tset:", index)
				_id = self.control[1].get().split(" - ")[0]
				
				# Cập nhật self.info
				self.info.pop(index)

				# Cập nhật self.genetic.lecturers
				self.genetic.lecturers.pop(int(_id))

				# Ghi đè lên file lecturers.csv, lecturers_info.csv
				self.overWriteFileCsv(0)

				# Cập nhật lại optionMenu
				tmp = index
				for i in range(2):
					self.optionsMenus[i]['menu'].delete(tmp)
					if (index >= len(self.info)):
						index = 0
					self.control[i].set(self.info[index])

				messagebox.showinfo('NOTIFY', "Delete succes")
			except:
				messagebox.showinfo('NOTIFY', "Delete error")

		elif (btnID == 1):
			try:
				index = self.subjects.index(self.control[2].get())
				_id = self.control[2].get().split(" - ")[0]

				# Cập nhật self.subjects
				self.subjects.pop(index)

				# Cập nhật self.genetic.subjects
				self.genetic.subjects.pop(_id)

				# Cập nhật self.genetic.lecturers
				for key in self.genetic.lecturers.keys():
					for val in self.genetic.lecturers[key]:
						if (_id in val):
							self.genetic.lecturers[key].remove(val)

				# Ghi đè lên file subjects.csv
				self.overWriteFileCsv(1)
				self.overWriteFileCsv(0)
				
				# Cập nhật lại optionMenu
				self.optionsMenus[2]['menu'].delete(index)
				if (index >= len(self.info)):
					index = 0
				self.control[2].set(self.subjects[index])
				
				messagebox.showinfo('NOTIFY', "Delete succes")
			except:
				messagebox.showinfo('NOTIFY', "Delete error")

		print("Deleting ", _id, index)
		return
	
	def overWriteFileCsv(self, type1 = 0):
		if (type1 == 0):
			# Ghi đè lên file lecturers_info.csv
			columnOfInfo = ["id", "monhoc"]
			tmp = [x.split(" - ") for x in self.info]
			dataFrame = pd.DataFrame(tmp, columns=columnOfInfo)
			dataFrame.to_csv("lecturers_info.csv", encoding="utf-8", index=False)
			
			# Ghi đè lên file lecturers.csv
			columnOfLecturer = ["id", "monhoc"]
			tmp = [[x,';'.join(y)] for x, y in self.genetic.lecturers.items()]
			dataFrame = pd.DataFrame(tmp, columns=columnOfLecturer)
			dataFrame.to_csv("lecturers.csv", encoding='utf-8', index=False)

		elif (type1 == 1):
			# Ghi đè lên file subjects.csv
			columnOfSubjects = ['mamon','ten','sotiet','solop']
			tmp = [[x] + list(y) for x, y in self.genetic.subjects.items()]
			dataFrame = pd.DataFrame(tmp, columns=columnOfSubjects)
			dataFrame.to_csv("subjects.csv", encoding='utf-8', index=False)

	def checkEmpty(self, data):
		for x, y in data.items():
			if (y[1].strip() == ''):
				return x
		return None

	def saveSchedule(self, event):
		try:
			schedule = self.genetic.getSchedule()
			column = ["idGV", "idMH", "room", "weekday", "shift"]
			tmp = []
			
			for key in schedule.keys():
				if (key != "rate"):
					for val in schedule[key]:
						tmp.append([key] + val)
			
			fileSchedule = pd.DataFrame(tmp, columns=column)
			fileSchedule.to_csv('schedule.csv', index=False, mode='w')
			messagebox.showinfo('NOTIFY', "Save succes!")
		except:
			messagebox.showinfo('ERROR', "Error!")
	
	def refresh(self, event):
		print("Refresh")
		_id = int(self.control[0].get().split(' - ')[0])
		self.genetic.populations = []
		self.genetic.schedule()
		tmp = self.genetic.getSchedule()
		print("Điểm ",tmp["rate"])
		self.fillTable(tmp[_id])

	def randomColorCode(self):
		## random màu tối
		R = rd.randint(1, 150)
		G = rd.randint(1, 150)
		B = rd.randint(1, 150)
		rgb_full= '#%02x%02x%02x'%(R, G, B)
		return rgb_full

	def fillTable(self, val):
		for i in range(4):
			for j in range(7):
				self.widgetCell[i][j].delete("text")
				self.widgetCell[i][j].config(background=BACKGROUND_COLOR)

		for idMH, room, weekDays, shift in val:
			fillInfo = "%s\n%s\nPhòng: %s\n"%(self.genetic.subjects[idMH][0], idMH, room)
			self.widgetCell[shift][weekDays].create_text(
				(CENTER_K_X ,CENTER_K_Y),
				font = (FONT, FONT_SIZE),
				text=fillInfo,
				tag="text",
				fill=FILL,
				width=110 ## Giới hạn để xuống dòng
			)
			self.widgetCell[shift][weekDays].config(background=self.colorCode[idMH])
	
class Form(tk.Frame):
	def __init__(self, parent, data, type1 = 1):
		tk.Frame.__init__(self, parent, pady = 30, padx = 240)
		self.data = data
		self.entrys = {}
		self.initUI(type1)
	
	def initUI(self, type1):
		i = 0
		for x, y in self.data.items():
			label = tk.Label(self, text=y[0] + ":", font=(FONT, FONT_SIZE))
			label.grid(row=i, column=0, sticky="W")
			txt = tk.Entry(self, font=(FONT, FONT_SIZE), width=50)
			txt.insert(0, y[1])
			txt.grid(row=i, column=1, sticky="snew")
			self.entrys[x] = txt
			if (i == 0 and type1 == 1):
				txt.config(state="disabled")
			i += 1
	
	def getAllFileds(self):
		return {key: [self.data[key][0], val.get()] for key, val in self.entrys.items()}

	def fillEntrys(self, data):
		i = 0
		for x, y in data.items():
			try:
				if (i == 0):
					self.entrys[x].config(state='normal')

				self.entrys[x].delete(0, tk.END)
				self.entrys[x].insert(0, y)

				if (i == 0):
					self.entrys[x].config(state='disabled')
			except:
				print("ERROR ", x)
			i += 1

	def clear(self, type1 = 0):
		i = 0
		for x in self.entrys.values():
			if (i == 0 and type1 == 1):
				str1 = x.get()
				x.delete(0, tk.END)
				x.insert(0, int(str1) + 1)
			else:
				x.delete(0, tk.END)
			i += 1

def main():
	genetic = GeneticScheduler()
	genetic.schedule()
	tmp = genetic.getSchedule()

	for x, y in tmp.items():
		print(x, y)

	test = {}
	rooms = set()
	lenClasses = 0
	scheduleRoom = [[[] for i in range(7)] for j in range(4)]

	for val in tmp.values():
		if (type(val) != int):
			lenClasses += len(val)
			for idMH, room, weekDays, shift in val:
				rooms.add(room)
				scheduleRoom[shift][weekDays].append(room)

				if (idMH in list(test.keys())):
					test[idMH] += 1
				else:
					test[idMH] = 1
			
	print("Số phòng được dùng:", len(rooms))
	print("Tổng số lớp được mở:", lenClasses)

	genetic.rateGen(tmp, scheduleRoom, 0)
	root = tk.Tk()
	app = GraphicSchedule(root, genetic)
	app.mainloop()

if __name__ == '__main__':
	main()