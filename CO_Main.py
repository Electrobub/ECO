#!/usr/bin/python
# -*- coding: utf-8 -*-
#TODO
# - Add Spinbox for QTY Editing in-place


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
        self.setWindowTitle('Tooltips')
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
        tableview = QtGui.QTableView()

        # Set the Model
        self.tablemode = MyTableModel(data, header, self)
        tableview.setModel(self.tablemode)
        
        #Enable Sorting
        tableview.setSortingEnabled(True)
        
        #Hide Grid
        #tableview.setShowGrid(False)
        
        #Resize Mode
        tableview.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

        self.modifyBtn = QtGui.QPushButton('Modify', self)
        self.modifyBtn.setStatusTip('Modify selected component')
        self.addBtn = QtGui.QPushButton('Add', self)
        self.addBtn.setStatusTip('Add a new component')
        self.connect(self.addBtn, QtCore.SIGNAL("clicked()"), self.updateUi)
        

        bottomLayout = QtGui.QHBoxLayout()
        bottomLayout.addStretch()
        bottomLayout.addWidget(self.modifyBtn)
        bottomLayout.addWidget(self.addBtn)

        midLayout = QtGui.QVBoxLayout()
        midLayout.addWidget(tableview)
        midLayout.addLayout(bottomLayout)

        self.setLayout(midLayout)
        
        
    def updateUi(self):
        
        print "rowCount:", self.tablemode.rowCount(self)
        print "columnCount:", self.tablemode.columnCount(self)
        
        self.tablemode.insertRows(1)
        #self.tablemode.insertRow(0)
        
        #self.emit(QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)

        """QtGui.QToolTip.setFont(QtGui.QFont('SansSerif',  10))

        self.setToolTip('This is a <b>QWidge</b> widget')

        btn = QtGui.QPushButton('Button', self)
        btn.setToolTip('This is a <b>QPushButton</b> widget')
        btn.move(50, 50)"""

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
    
    #setData must be implemented for editable model subclasses - must also emit the datChanged signal
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

def main():

    app = QtGui.QApplication(sys.argv)
    ex = Window()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
