#!/usr/bin/python
# -*- coding: utf-8 -*-
#TODO
# - Add Spinbox for QTY Editing in-place
# - Add Coloured BG to QTY cell, if qty low - look at Qt.BackgroundColorRole (in data method)

#TODO
#Look what super() does. (Is it necessary in Dialog? componentDialog)
#or is it possible to call the int like QtGui.QDialog.__init__(self, parent)

# Position of QTY column
QTY = 4

import sys
from PySide import QtGui
from PySide import QtCore
import operator

header = ['Name', 'Category', 'Description', 'Package', 'Qty', 'Manufacturer', 'Datasheet']
data = [['2N222', 'Transistor', 'All in one package', 'Through Hole', '10', 'Texas', 'No'],
['WOWZa', 'MOSFET', 'Does what its told', 'Through Hole', '2', 'SM', 'No']]

class Window(QtGui.QMainWindow):
    
    def __init__(self):
        super(Window, self).__init__()
        
        self.form_widget = Overview(self) 
        self.setCentralWidget(self.form_widget) 
        
        #Actions
        addAction = QtGui.QAction('&Add', self)
        addAction.setShortcut('Ctrl+A')
        addAction.setStatusTip('Add a new component')
        #addAction.triggered.connect()

        modifyAction = QtGui.QAction('&Modify', self)
        modifyAction.setShortcut('Ctrl+M')
        modifyAction.setStatusTip('Modify selected component')
        #addAction.triggered.connect()
        
        aboutAction = QtGui.QAction('&About', self)
        aboutAction.setStatusTip('About Electronic Components Organiser')
        #addAction.triggered.connect()
        

        #Menubar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(addAction)
        fileMenu.addAction(modifyAction)
        
        fileMenu = menubar.addMenu('&Help')
        fileMenu.addAction(aboutAction)
        fileMenu.addAction(aboutAction)
        
        
        self.setGeometry(300, 300, 850, 550)
        self.setWindowTitle('Electronic Components Organiser')
        self.statusBar().showMessage('Welcome')
        
        self.show()
        

class Overview(QtGui.QWidget):

    def __init__(self, parent = None):
        super(Overview, self).__init__(parent)

        self.initUI()

    def initUI(self):


        """nameLabel = QtGui.QLabel('Name')
        catLabel = QtGui.QLabel('Category')
        descLabel = QtGui.QLabel('Description')
        packLabel = QtGui.QLabel('Package')
        qtyLabel = QtGui.QLabel('Qty')
        manufLabel = QtGui.QLabel('Manufacturer')
        dataLabel = QtGui.QLabel('Datasheet')"""

        # Create the view
        self.tableview = QtGui.QTableView()

        # Set the Model
        self.tablemode = MyTableModel(data, header, self)
        self.tableview.setModel(self.tablemode)
        
        #Enable Sorting
        self.tableview.setSortingEnabled(True)
        
        #Hide Grid
        #tableview.setShowGrid(False)
        
        #Resize Mode
        self.tableview.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

        self.removeBtn = QtGui.QPushButton('Remove', self)
        self.removeBtn.setStatusTip('Remove Selected Component')
        self.modifyBtn = QtGui.QPushButton('Modify', self)
        self.modifyBtn.setStatusTip('Modify selected component')
        self.addBtn = QtGui.QPushButton('Add', self)
        self.addBtn.setStatusTip('Add a new component')
        self.connect(self.removeBtn, QtCore.SIGNAL("clicked()"), self.removeSelectedRows)
        self.connect(self.addBtn, QtCore.SIGNAL("clicked()"), self.updateUi)
        self.connect(self.modifyBtn, QtCore.SIGNAL("clicked()"), self.openDialog)
        
        

        bottomLayout = QtGui.QHBoxLayout()
        bottomLayout.addStretch()
        bottomLayout.addWidget(self.removeBtn)
        bottomLayout.addWidget(self.modifyBtn)
        bottomLayout.addWidget(self.addBtn)

        midLayout = QtGui.QVBoxLayout()
        midLayout.addWidget(self.tableview)
        midLayout.addLayout(bottomLayout)

        self.setLayout(midLayout)
        
        
    def updateUi(self):
        
        print "rowCount:", self.tablemode.rowCount(self)
        print "columnCount:", self.tablemode.columnCount(self)
        
        
        #print self.tableview.selectionModel().currentIndex()
        #print self.tableview.selectionModel().selectedIndexes()
       
        self.tablemode.insertRows(0)
        
        #self.emit(QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)

        """QtGui.QToolTip.setFont(QtGui.QFont('SansSerif',  10))

        self.setToolTip('This is a <b>QWidge</b> widget')

        btn = QtGui.QPushButton('Button', self)
        btn.setToolTip('This is a <b>QPushButton</b> widget')
        btn.move(50, 50)"""

        #self.show()
       
       
    def removeSelectedRows(self):
        
        #Get index list of all selected cells
        indexList = self.tableview.selectionModel().selectedIndexes()
        if (len(indexList) < 1):
            return
        
        
        if QtGui.QMessageBox.question(self, "Remove Components", ("Are you sure you want to remove "+str(len(indexList))+" components?"), QtGui.QMessageBox.Yes|QtGui.QMessageBox.No) == QtGui.QMessageBox.No:
            return
        
        #Go through list and remove rows
        #for index in indexList:
        #    print index.column()
        
        firstRow = indexList[0].row()
        lastRow = indexList[-1].row()
        
        rowsToDelete = lastRow - firstRow + 1

        self.tablemode.removeRows(firstRow, rowsToDelete)
        
        
    def openDialog(self):
        
        self.dialog = componentDialog(self)
        
        #Modal Dialog
        self.dialog.exec_()


class componentDialog(QtGui.QDialog):
    
    def __init__(self, parent):
        super(componentDialog, self).__init__()

        nameLabel = QtGui.QLabel('Name')
        manufLabel = QtGui.QLabel('Manufacturer')
        catLabel = QtGui.QLabel('Category')
        packLabel = QtGui.QLabel('Package')
        descLabel = QtGui.QLabel('Description')
        dataLabel = QtGui.QLabel('Datasheet')
        commentLabel = QtGui.QLabel('Comments')
        
        nameEdit = QtGui.QLineEdit('Name')
        manufEdit = QtGui.QComboBox()
        catEdit = QtGui.QComboBox()
        packEdit = QtGui.QComboBox()
        descEdit = QtGui.QLineEdit()
        dataEdit = QtGui.QLineEdit()
        commentEdit = QtGui.QTextEdit()
        
        boxLabel = QtGui.QLabel('Storage Box')
        posLabel = QtGui.QLabel('Position')
        
        boxEdit = QtGui.QComboBox()
        posEdit = QtGui.QLineEdit()
        
        minQtyLabel = QtGui.QLabel('Min. Qty Alert')
        maxQtyLabel = QtGui.QLabel('Desired Max Qty')
        qtyLabel = QtGui.QLabel('Qty')
        
        minQtyEdit = QtGui.QSpinBox()
        maxQtyEdit = QtGui.QSpinBox()
        qtyEdit = QtGui.QSpinBox()
        

        supplier1Label = QtGui.QLabel('Supplier 1')
        key1Label = QtGui.QLabel('KeyCode')
        
        supplier1Edit = QtGui.QComboBox()
        key1Edit = QtGui.QLineEdit()
        
        supplier2Label = QtGui.QLabel('Supplier 2')
        key2Label = QtGui.QLabel('KeyCode')
        
        supplier2Edit = QtGui.QComboBox()
        key2Edit = QtGui.QLineEdit()
        
        supplier3Label = QtGui.QLabel('Supplier 3')
        key3Label = QtGui.QLabel('KeyCode')
        
        supplier3Edit = QtGui.QComboBox()
        key3Edit = QtGui.QLineEdit()

        
        manufEdit.addItems(['Texas Instruments','SF','Avr','Maxxim'])
        manufEdit.setEditable(True)
        
        catEdit.addItems(['Linear Regulators', 'Microcontrollers'])
        catEdit.setEditable(True)
        
        packEdit.addItems(['PDIP-12','PDIP-8'])
        packEdit.setEditable(True)
        
        boxEdit.addItems(['Briefcase', 'Drawers-1', 'Drawers-2'])
        boxEdit.setEditable(True)
        
        supplier1Edit.addItems(['RS Components','Element14','Jaycar','Conrad'])
        supplier1Edit.setEditable(True)
        
        supplier2Edit.addItems(['', 'RS Components','Element14','Jaycar','Conrad'])
        supplier2Edit.setEditable(True)
        
        supplier3Edit.addItems(['', 'RS Components','Element14','Jaycar','Conrad'])
        supplier3Edit.setEditable(True)
        
        minQtyEdit.setMinimum(-1)
        maxQtyEdit.setValue(5)
        

        buttonWidget = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Save | QtGui.QDialogButtonBox.Cancel)
        
        buttonWidget.rejected.connect(self.reject)

        
        groupBox = QtGui.QGroupBox('Location')
        reorderBox = QtGui.QGroupBox('Reordering')
        qtyBox = QtGui.QGroupBox('Stock')
        
        grid = QtGui.QGridLayout()
        grid.addWidget(nameLabel, 0, 0)
        grid.addWidget(manufLabel, 1, 0)
        grid.addWidget(catLabel, 2, 0)
        grid.addWidget(packLabel, 3, 0)
        grid.addWidget(descLabel, 4, 0)
        grid.addWidget(dataLabel, 5, 0)
        grid.addWidget(commentLabel, 6, 0)
        
        grid.addWidget(nameEdit, 0, 1)
        grid.addWidget(manufEdit, 1, 1)
        grid.addWidget(catEdit, 2, 1)
        grid.addWidget(packEdit, 3, 1)
        grid.addWidget(descEdit, 4, 1)
        grid.addWidget(dataEdit, 5, 1)
        grid.addWidget(commentEdit, 6, 1, 1, 1)

        
        locatGrid = QtGui.QGridLayout()
        locatGrid.addWidget(boxLabel, 0, 0)
        locatGrid.addWidget(posLabel, 1, 0)
        
        locatGrid.addWidget(boxEdit, 0, 1)
        locatGrid.addWidget(posEdit, 1, 1)
        locatGrid.setRowStretch(2, 1)
        
        qtyGrid = QtGui.QGridLayout()
        qtyGrid.addWidget(minQtyLabel, 0, 0)
        qtyGrid.addWidget(maxQtyLabel, 1, 0)
        qtyGrid.addWidget(qtyLabel, 3, 0)
        qtyGrid.setRowStretch(4, 1)
        
        qtyGrid.addWidget(minQtyEdit, 0, 1)
        qtyGrid.addWidget(maxQtyEdit, 1, 1)
        qtyGrid.setRowMinimumHeight(2, 20)
        qtyGrid.addWidget(qtyEdit, 3, 1)
        
        reorderGrid = QtGui.QGridLayout()
        reorderGrid.addWidget(supplier1Label, 0, 0)
        reorderGrid.addWidget(supplier1Edit, 0, 1)
        reorderGrid.addWidget(key1Label, 0, 2)
        reorderGrid.addWidget(key1Edit, 0, 3)
        
        reorderGrid.addWidget(supplier2Label, 1, 0)
        reorderGrid.addWidget(supplier2Edit, 1, 1)
        reorderGrid.addWidget(key2Label, 1, 2)
        reorderGrid.addWidget(key2Edit, 1, 3)
        
        reorderGrid.addWidget(supplier3Label, 2, 0)
        reorderGrid.addWidget(supplier3Edit, 2, 1)
        reorderGrid.addWidget(key3Label, 2, 2)
        reorderGrid.addWidget(key3Edit, 2, 3)
        
        
        groupBox.setLayout(locatGrid)
        reorderBox.setLayout(reorderGrid)
        qtyBox.setLayout(qtyGrid)
        
        grid.addWidget(groupBox, 0, 2, 5, 1)
        grid.addWidget(reorderBox, 7, 0, 3, 2)
        grid.addWidget(qtyBox, 6, 2, 3, 1)
        grid.addWidget(buttonWidget, 9, 2, 1, 1)
        
        commentLayout = QtGui.QHBoxLayout()
        commentLayout.addWidget(commentLabel)
        commentLayout.addWidget(commentEdit)
        
        
        
        
        topLeftLayout = QtGui.QVBoxLayout()

        topLayout = QtGui.QHBoxLayout()

        topLayout.addLayout(grid)

        self.setLayout(topLayout)

        
        self.setGeometry(300, 300, 650, 350)
        self.setWindowTitle('Component Viewer')
        #self.statusBar().showMessage('Welcome')
        
        #self.show()


class MyTableModel(QtCore.QAbstractTableModel):
    def __init__(self, mylist, header, *args):
        QtCore.QAbstractTableModel.__init__(self, *args)
        self.mylist = mylist
        self.header = header
    def rowCount(self, parent):
        return len(self.mylist)
    def columnCount(self, parent):
        return len(self.mylist[0])
    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != QtCore.Qt.DisplayRole:
            return None
        #QtGui.QBrush.setGreen()
        return self.mylist[index.row()][index.column()]
    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[col]
        return None
        
    def flags(self, index):
        if not index.isValid() or index.column() is not QTY:
            #return QtCore.Qt.ItemIsEnabled
            return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index))
        return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index) | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable)
    
    #setData must be implemented for editable model subclasses - must also emit the dataChanged signal
    #Rapid GUI Programming Pg 449 Table 14.2
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid() and 0 <= index.row() < len(self.mylist):
            column = index.column()
            if column == QTY:
                try: #Make sure it's an integer
                    self.mylist[index.row()][QTY] = int(value)
                except:
                    return False
            self.emit(QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
                
            return True
        return False
                
    def sort(self, col, order):
        """sort table by given column number col"""
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self.mylist = sorted(self.mylist,
            key=operator.itemgetter(col))
        if order == QtCore.Qt.DescendingOrder:
            self.mylist.reverse()
        self.emit(QtCore.SIGNAL("layoutChanged()"))
        
        
    #def insertRow(self, row, parent):
    #    return self.insertRows(row, 1, parent)

    def insertRows(self, position, rows=1, index=QtCore.QModelIndex()):
        self.beginInsertRows(QtCore.QModelIndex(), position, position + rows - 1)
        for row in range(rows):
            self.mylist.insert(position + row, ['Extra', 'Transistor', 'All in one package', 'Through Hole', '10', 'Texas', 'No'])
        self.endInsertRows()
        return True
    
    def removeRows(self, position, rows=1, index=QtCore.QModelIndex()):
        self.beginRemoveRows(QtCore.QModelIndex(), position, position + rows - 1)
        self.mylist = self.mylist[:position] + self.mylist[position + rows:]
        self.endRemoveRows()
        return True

def main():

    app = QtGui.QApplication(sys.argv)
    ex = Window()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
