""" 
    Copyright (C) 2020 Hiiragi <heterophyllus.work@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
# -*- coding: utf-8 -*
import sys
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from gui import Ui_MainWindow
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from lens import Lens
import surface as s
import json


class MplCanvas(FigureCanvas):
	def __init__(self, parent=None, width=10, height=10, dpi=100):
		fig = Figure(dpi=dpi)
		self.axes = fig.add_subplot(111)

		FigureCanvas.__init__(self, fig)
		self.setParent(parent)

		FigureCanvas.setSizePolicy(self,QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
		FigureCanvas.updateGeometry(self)


class Window(QtWidgets.QMainWindow):
	def __init__(self, parent=None):

		super(Window, self).__init__(parent)
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)

		self.currentFile = ""

		self.initializeCoefTable('left')
		self.initializeCoefTable('right')

		# lens list
		self.lens_list = []

		# inputs
		self.ui.lineEdit_Thickness.setValidator(QtGui.QDoubleValidator())
		self.ui.lineEdit_R1_Diameter_Inner.setValidator(QtGui.QDoubleValidator())
		self.ui.lineEdit_R1_Diameter_Outer.setValidator(QtGui.QDoubleValidator())
		self.ui.lineEdit_R2_Diameter_Inner.setValidator(QtGui.QDoubleValidator())
		self.ui.lineEdit_R2_Diameter_Outer.setValidator(QtGui.QDoubleValidator())
		
		# draw area
		self.l = QtWidgets.QVBoxLayout(self.ui.tab_Draw)
		self.sc = MplCanvas(self.ui.tab_Draw, width=5, height=5, dpi=100)
		self.l.addWidget(self.sc)
		self.l.addWidget(NavigationToolbar(self.sc,self))

		# signals & slots
		self.ui.pushButton_AddLens.clicked.connect(lambda: self.addNewLens())
		self.ui.pushButton_DeleteLens.clicked.connect(self.deleteSelectedLens)

		self.ui.action_About.triggered.connect(self.showAbout)

		self.ui.action_New.triggered.connect(self.newFile)
		self.ui.action_Open.triggered.connect(self.openFile)
		self.ui.action_SaveAs.triggered.connect(self.saveAs)

		self.connectAll()


		self.addNewLens()
		self.ui.listWidget_Lens.setCurrentRow(0)

	def connectAll(self):

		try:
			self.ui.listWidget_Lens.currentRowChanged.connect(self.changeLens)
		except ConnectionError:
			pass

		try: 
			self.ui.comboBox_R1_Type.currentIndexChanged.connect(lambda : self.changeSurfaceType('left'))
		except ConnectionError:
			pass
		try: 
			self.ui.comboBox_R2_Type.currentIndexChanged.connect(lambda : self.changeSurfaceType('right'))
		except ConnectionError:
			pass

		try:
			self.ui.tableWidget_R1_Coefs.cellChanged.connect(self.updateDrawing)
		except ConnectionError:
			pass
		try:
			self.ui.tableWidget_R2_Coefs.cellChanged.connect(self.updateDrawing)
		except ConnectionError:
			pass

		try:
			self.ui.lineEdit_Thickness.textEdited.connect(self.updateDrawing)
		except ConnectionError:
			pass

		try:
			self.ui.textEdit_Description.textChanged.connect(self.editDescription)
		except ConnectionError:
			pass

		try:
			self.ui.lineEdit_R1_Diameter_Inner.textEdited.connect(self.updateDrawing)
		except ConnectionError:
			pass
		try:
			self.ui.lineEdit_R1_Diameter_Outer.textEdited.connect(self.updateDrawing)
		except ConnectionError:
			pass
		try:
			self.ui.lineEdit_R2_Diameter_Inner.textEdited.connect(self.updateDrawing)
		except ConnectionError:
			pass
		try:
			self.ui.lineEdit_R2_Diameter_Outer.textEdited.connect(self.updateDrawing)
		except ConnectionError:
			pass


	def disconnectAll(self):
		try:
			self.ui.listWidget_Lens.currentRowChanged.disconnect()
		except:
			pass

		try:
			self.ui.comboBox_R1_Type.currentIndexChanged.disconnect()
		except:
			pass
		try:
			self.ui.comboBox_R2_Type.currentIndexChanged.disconnect()
		except:
			pass
		
		try:
			self.ui.tableWidget_R1_Coefs.cellChanged.disconnect()
		except:
			pass
		try:
			self.ui.tableWidget_R2_Coefs.cellChanged.disconnect()
		except:
			pass
		
		try:
			self.ui.lineEdit_Thickness.textEdited.disconnect()
		except:
			pass

		try:
			self.ui.textEdit_Description.textChanged.disconnect()
		except:
			pass

		try:
			self.ui.lineEdit_R1_Diameter_Inner.textEdited.disconnect()
		except:
			pass
		try:
			self.ui.lineEdit_R1_Diameter_Outer.textEdited.disconnect()
		except:
			pass
		try:
			self.ui.lineEdit_R2_Diameter_Inner.textEdited.disconnect()
		except:
			pass
		try:
			self.ui.lineEdit_R2_Diameter_Outer.textEdited.disconnect()
		except:
			pass
		

	def getUiObjects(self, which_surf= 'left'):
		if which_surf == 'left':
			return self.ui.lineEdit_R1_Diameter_Outer, self.ui.lineEdit_R1_Diameter_Inner, self.ui.comboBox_R1_Type, self.ui.tableWidget_R1_Coefs, self.ui.tableWidget_R1_Data
		else:
			return self.ui.lineEdit_R2_Diameter_Outer, self.ui.lineEdit_R2_Diameter_Inner, self.ui.comboBox_R2_Type, self.ui.tableWidget_R2_Coefs, self.ui.tableWidget_R2_Data


	def initializeCoefTable(self, which_surf= 'left'):
		""" 
		initialize coefficients table
		"""
		
		_, _, combo, coef_table, _ = self.getUiObjects(which_surf)
		
		surf_type_index = int(combo.currentIndex())

		# horizontal header
		coef_table.clear()
		coef_table.setColumnCount(1)
		coef_table.setHorizontalHeaderLabels(['Value'])
		
		# vertical header
		header_labels = []
		if surf_type_index == 0: # sphere
			coef_table.setRowCount(1)
			header_labels = ['Radius']
			coef_table.setItem(0,0, QtWidgets.QTableWidgetItem('Inf'))

		elif surf_type_index == 1: # even asphere
			coef_table.setRowCount(1 + 1 + 9) # R, k, A4-A20
			header_labels = ['Radius']
			coef_table.setItem(0,0, QtWidgets.QTableWidgetItem('Inf'))
			header_labels.append('k')
			coef_table.setItem(1,0, QtWidgets.QTableWidgetItem('0.0'))
			for i in range(2,10+1):
				header_labels.append('A' + str(i*2))
				coef_table.setItem(i,0, QtWidgets.QTableWidgetItem('0.0'))

		elif surf_type_index == 2: # odd asphere
			coef_table.setRowCount(1 + 1 + 17) # R, k, A4-A20
			header_labels = ['Radius']
			coef_table.setItem(0,0, QtWidgets.QTableWidgetItem('Inf'))
			header_labels.append('k')
			coef_table.setItem(1,0, QtWidgets.QTableWidgetItem('0.0'))
			for i in range(2,21+1):
				header_labels.append('A' + str(i+1))
				coef_table.setItem(i,0, QtWidgets.QTableWidgetItem('0.0'))
		
		coef_table.setVerticalHeaderLabels(header_labels)
		coef_table.show()

	
	def addNewLens(self, lens=None):
		""" 
		Adds a new lens to the list
		"""
		if lens is None:
			new_lens = Lens()
			new_lens.name = "New Lens"
		else:
			new_lens = lens

		self.ui.listWidget_Lens.addItem(new_lens.name)
		item = self.ui.listWidget_Lens.item(self.ui.listWidget_Lens.count()-1)
		item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
		
		self.lens_list.append(new_lens)


	def deleteSelectedLens(self):
		""" 
		Delete the selected lens from the list
		"""

		index = self.ui.listWidget_Lens.currentIndex().row()
		if index >= 0:
			self.ui.listWidget_Lens.takeItem(index)
			self.lens_list.pop(index)
		else:
			print("No lens is selected")
			return

	def changeLens(self):
		"""
		Slot function connected to selection change of listWidget
		"""

		lens = self.lens_list[self.ui.listWidget_Lens.currentRow()]
		self.setLensToUI(lens)
		self.updateDrawing()


	def changeSurfaceType(self, which_surf='left'):
		"""
		Slot function connected to comboBox change
		"""

		self.disconnectAll()
		self.initializeCoefTable(which_surf)
		self.connectAll()

		# update lens data
		lens = self.getLensFromUI()
		self.lens_list[self.ui.listWidget_Lens.currentRow()] = lens


	def getSurfaceFromUI(self, which_surf='left'):

		edit_outer, edit_inner, combo, coef_table, _ = self.getUiObjects(which_surf)

		type_index = combo.currentIndex()
		
		if type_index == 0: # sphere
			surf = s.Sphere()
			r = np.inf
			try:
				r = float(coef_table.item(0,0).text())
			except ValueError:
				r = np.inf

			surf.r = r

		else:
			r = np.inf
			try:
				r = float(coef_table.item(0,0).text())
			except ValueError:
				r = np.inf

			try:
				k = float(coef_table.item(1,0).text())
			except AttributeError as e:
				print(e)
				k = 0.0
				return

			coefs = np.zeros(coef_table.rowCount()-2)
			for i in range(2,coef_table.rowCount()):
				try:
					coefs[i-2]= float(coef_table.item(i,0).text())
				except AttributeError as e:
					print(e)
					coefs[i-2] = 0.0
				except ValueError:
					coefs[i-2] = 0.0

			if type_index == 1:
				surf = s.EvenAsphere(r,k,coefs)
			else:
				surf = s.OddAsphere(r,k,coefs)
				
		
		# diameters
		try:
			surf.outer_d = float(edit_outer.text())
		except ValueError:
			surf.outer_d = 0.0
		
		try:
			surf.inner_d = float(edit_inner.text())
		except ValueError:
			surf.inner_d = 0.0

		return surf
	
	def setSurfaceToUI(self, surf=None, which_surf= 'left'):

		if surf is None:
			return
		
		self.disconnectAll()

		edit_outer, edit_inner, combo, coef_table, _ = self.getUiObjects(which_surf)

		if surf.type == 'SPH':
			combo.setCurrentIndex(0)
			self.disconnectAll()
			self.initializeCoefTable(which_surf)
			try:
				coef_table.item(0,0).setText(str(surf.r))
			except AttributeError:
				pass
		else:
			combo.setCurrentIndex(1)
			self.disconnectAll()
			self.initializeCoefTable(which_surf)
			r,k,coefs = surf.get_parameters()
			try:
				coef_table.item(0,0).setText(str(r))
				coef_table.item(1,0).setText(str(k))
				for i,A in enumerate(coefs):
					coef_table.item(i+2,0).setText(str(A))
			except AttributeError:
				pass
			

		# diameters
		edit_outer.setText(str(surf.outer_d))
		edit_inner.setText(str(surf.inner_d))

		self.connectAll()

	def getLensFromUI(self):
		"""
		Get lens parameters from UI
		"""

		# lens name
		lens = Lens()
		lens.name = self.ui.listWidget_Lens.currentItem().text()
		
		# both surface
		lens.left  = self.getSurfaceFromUI('left')
		lens.right = self.getSurfaceFromUI('right')

		# material
		lens.material = self.ui.lineEdit_Glass.text()

		# thickness
		try:
			lens.thickness = float(self.ui.lineEdit_Thickness.text())
		except ValueError:
			lens.thickness = 0.0

		# description
		lens.description = self.ui.textEdit_Description.toPlainText()

		return lens

	def setLensToUI(self, lens=None):
		if lens is None:
			return
		
		self.setSurfaceToUI(lens.left,'left')
		self.setSurfaceToUI(lens.right,'right')

		self.disconnectAll()
		self.ui.lineEdit_Glass.setText(lens.material)
		self.ui.lineEdit_Thickness.setText(str(lens.thickness))
		self.ui.textEdit_Description.setPlainText(lens.description)
		self.connectAll()
	
	def editDescription(self):
		text = self.ui.textEdit_Description.toPlainText()
		self.lens_list[self.ui.listWidget_Lens.currentRow()].description = text
		
	def drawLens(self, lens=None):
		"""
		Draws the lens schematic

		Args:
			lens(Lens): lens object to be drawn
		"""

		self.sc.axes.clear()
		self.sc.draw()
		self.ui.tableWidget_R1_Data.clear()
		self.ui.tableWidget_R2_Data.clear()


		if lens is None:
			return

		if lens.left.inner_d <= 0.0 or lens.right.inner_d <= 0.0:
			#print("Invalid diameter (<=0)")
			return
		

		header_labels = ['h', 'sag', 'slope', 'local_R']
		step = 0.25
		color = 'b'

		# --------------
		# left surface
		# --------------

		# curve
		h1 = np.linspace(-lens.left.inner_d/2, lens.left.inner_d/2)
		z1 = lens.left.sag(h1)
		self.sc.axes.plot(z1, h1, color)

		# plane
		h1a = np.linspace(lens.left.inner_d/2, lens.left.outer_d/2)
		z1a = np.zeros_like(h1a) + z1[-1]
		self.sc.axes.plot(z1a, h1a, color)
		self.sc.axes.plot(z1a, -h1a, color)

		# data
		h1p = np.arange(0.0, lens.left.inner_d/2, step)
		sag1 = lens.left.sag(h1p)
		slope1 = lens.left.slope(h1p)
		localR1 = lens.left.local_radius(h1p)

		table = self.ui.tableWidget_R1_Data
		table.clear()
		table.setColumnCount(len(header_labels))
		table.setHorizontalHeaderLabels(header_labels)
		table.setRowCount(len(h1p))

		for i in range(len(h1p)):
			table.setItem(i,0, QtWidgets.QTableWidgetItem('{:.4f}'.format(h1p[i])))
			table.setItem(i,1, QtWidgets.QTableWidgetItem('{:.4f}'.format(sag1[i])))
			table.setItem(i,2, QtWidgets.QTableWidgetItem('{:.4f}'.format(slope1[i])))
			table.setItem(i,3, QtWidgets.QTableWidgetItem('{:.4f}'.format(localR1[i])))

		# ---------------
		# right surface
		# ---------------

		# curve
		h2 = np.linspace(-lens.right.inner_d/2, lens.right.inner_d/2)
		z2 = lens.right.sag(h2) + lens.thickness
		self.sc.axes.plot(z2, h2, color)

		# plane
		h2a = np.linspace(lens.right.inner_d/2, lens.right.outer_d/2)
		z2a = np.zeros_like(h2a) + z2[-1]
		self.sc.axes.plot(z2a, h2a, color)
		self.sc.axes.plot(z2a, -h2a, color)

		# data
		h2p = np.arange(0.0, lens.right.inner_d/2, step)
		sag2 = lens.right.sag(h2p)
		slope2 = lens.right.slope(h2p)
		localR2 = lens.right.local_radius(h2p)
		
		table = self.ui.tableWidget_R2_Data
		table.clear()
		table.setColumnCount(len(header_labels))
		table.setHorizontalHeaderLabels(header_labels)
		table.setRowCount(len(h2p))
		
		for i in range(len(h2p)):
			table.setItem(i,0, QtWidgets.QTableWidgetItem('{:.4f}'.format(h2p[i])))
			table.setItem(i,1, QtWidgets.QTableWidgetItem('{:.4f}'.format(sag2[i])))
			table.setItem(i,2, QtWidgets.QTableWidgetItem('{:.4f}'.format(slope2[i])))
			table.setItem(i,3, QtWidgets.QTableWidgetItem('{:.4f}'.format(localR2[i])))


		# -----
		# edge
		# -----
		z3 = np.array([z1[0], z2[0]],dtype=float)
		h3 = np.array([lens.left.outer_d/2, lens.right.outer_d/2],dtype=float)
		self.sc.axes.plot(z3, h3, color)
		self.sc.axes.plot(z3, -h3, color)


		# set axis scale
		margin = 1.0
		max_d = np.maximum(lens.left.outer_d/2,lens.right.outer_d/2)
		axis_lim = np.maximum(max_d,lens.thickness) + margin
		self.sc.axes.set_xlim([-axis_lim,axis_lim])
		self.sc.axes.set_ylim([-axis_lim,axis_lim])

		self.sc.draw()


	def updateDrawing(self):
		""" 
		Update the current lens data and drawing
		"""
		
		lens = self.getLensFromUI()
		self.lens_list[self.ui.listWidget_Lens.currentRow()] = lens
		self.drawLens(lens)


	def showAbout(self):
		msg = ("Copyright (C) 2020 Hiiragi <heterophyllus.work@gmail.com>\n"
		"\n"
		"This program is free software: you can redistribute it and/or modify "
		"it under the terms of the GNU General Public License as published by "
		"the Free Software Foundation, either version 3 of the License, or "
		"(at your option) any later version.\n"
		"\n"
		"This program is distributed in the hope that it will be useful, "
		"but WITHOUT ANY WARRANTY; without even the implied warranty of "
		"MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the "
		"GNU General Public License for more details.\n"
		"\n"
		"You should have received a copy of the GNU General Public License "
		"along with this program.  If not, see <http://www.gnu.org/licenses/>.\n"
		"\n"
		"You can get the further information from the repository:\n" 
		"https://github.com/heterophyllus/lens-drawing")
		
		msgBox = QtWidgets.QMessageBox()
		msgBox.setText("Python Program for Lens Drawing")
		msgBox.setInformativeText(msg)
		msgBox.setStandardButtons(QtWidgets.QMessageBox.Close )
		msgBox.setDefaultButton(QtWidgets.QMessageBox.Close)
		msgBox.exec_()

	def newFile(self):
		self.currentFile = ""
		self.disconnectAll()
		self.lens_list.clear()
		self.ui.listWidget_Lens.clear()
		self.connectAll()
		self.addNewLens()
		

	def openFile(self):
		fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file','',"JSON Files (*.json);;All Files (*)")
		if fileName != "":
			self.loadFile(fileName)
			self.currentFile = fileName

	def saveCurrent(self):
		if self.currentFile == "":
			self.saveAs()
		else:
			self.saveToJSON(self.currentFile)

	def saveAs(self):
		fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', '',"JSON Files (*.json);;All Files (*)")
		if fileName != "":
			self.saveToJSON(fileName)
			self.currentFile = fileName

	def saveToJSON(self,filepath=""):

		# dict of all lenses
		dataset = {}
		dataset['lens_count'] = len(self.lens_list)
		for i,lens in enumerate(self.lens_list):
			lens_dict = lens.to_dict()
			dataset[str(i)] = lens_dict

		# save as json
		with open(filepath, 'w') as outfile:
			json.dump(dataset,outfile, indent=4)
		
		print("Saved to " + filepath)
	
	def loadFile(self,filepath=""):
		self.disconnectAll()
		self.lens_list.clear()
		self.ui.listWidget_Lens.clear()

		with open(filepath) as f:
			dataset = json.load(f)

			lens_count = int(dataset['lens_count'])
			for i in range(lens_count):
				lens_dict = dataset[str(i)]
				lens = Lens()
				lens.from_dict(lens_dict)
				self.addNewLens(lens)
		self.connectAll()
		self.currentFile = filepath

		QtWidgets.QMessageBox.information(self, "Info", "JSON file has bben loaded")


if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	w = Window()
	w.resize(5,5)
	w.show()
	sys.exit(app.exec_())

