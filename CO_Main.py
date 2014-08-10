#!/usr/bin/python
# -*- coding: utf-8 -*-
#TODO
# - Fix Table Sorting (implement __lt__ in ComponentClass? Or other that is required)
# - Add regexp search box on main window (look at QSortFilterProxyModel)

#TODO
# - Look what super() does. (Is it necessary in Dialog? componentDialog)
#or is it possible to call the int like QtGui.QDialog.__init__(self, parent)
# - In componentDialog figure out the proper passing of parent, so the dialog gets centred correctly
# - look into setSelectionMode(SingleSelection) - To select a row at a time?

# List Positions
NAME = 0
MANUFACTURER = 1
CATEGORY = 2
PACKAGE = 3
DESCRIPTION = 4
DATASHEET = 5
COMMENTS = 6
LOCATION = 7
POSITION = 8
MINQTY = 9
DESIREDQTY = 10
QTY = 11
SUPPLIERS = 12

import sys
from PySide import QtGui
from PySide import QtCore
import operator
from Components import ComponentContainer, Component

header = [NAME, CATEGORY, DESCRIPTION, PACKAGE, DATASHEET, QTY]
#header = ['Name', 'Category', 'Description', 'Package', 'Qty', 'Manufacturer', 'Datasheet']
#data = [['2N222', 'Transistor', 'All in one package', 'Through Hole', '10', 'Texas', 'No'],
#['WOWZa', 'MOSFET', 'Does what its told', 'Through Hole', '2', 'SM', 'No']]

dataLabels = ['Name', 'Manufacturer', 'Category', 'Package', 'Description', 'Datasheet', 'Comments', 'Location', 'Position', 'Minimum Qty.', 'Desired Qty.', 'Qty']
#dataset = [['2N2222', 'Fairchild', 'Transistors', 'NPN General-Purpose Amplifier', 'TO-92', 'http://datasheet.com', 'Very useful chip to have on hand', 'Storage Box', 'A7', '3', '10', '5'], ['LM741', 'Texas Instruments', 'Op-Amp', 'General Purpose Op-Amp', 'PDIP-8', 'http://datasheet.com', 'Not the prettiest but does the job', 'Storage Box', 'B2', '2', '5', '5']]

components = ComponentContainer('test.txt')

components.addComponent(Component('LM741', 'Texas Instruments', 'Op-Amp', 'PDIP-8', 'General Purpose Op-Amp', 'http://datasheet.com', 'Not the prettiest but does the job', 'Storage Box', 'B2', '2', '5', '5', [['RS', 1111], ['Conrad', 2222], ['YoShop', 3333]]))
components.addComponent(Component('2N2222', 'Fairchild', 'Transistors', 'TO-92', 'NPN General-Purpose Amplifier', 'http://datasheet.com', 'Very useful chip to have on hand', 'Storage Box', 'A7', '3', '10', '5', [['RS', 1111], ['Conrad', 2222], ['YoShop', 3333]]))

#components.recreateSets()   

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
        #self.move(200,40)
        
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
        self.delegate = qtyEditDelegate()
        
        # Set the Model
        self.tablemode = MyTableModel(self)
        self.tableview.setModel(self.tablemode)
        self.tableview.setItemDelegate(self.delegate)
        
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
        self.connect(self.addBtn, QtCore.SIGNAL("clicked()"), self.openAddDialog)
        #self.connect(self.addBtn, QtCore.SIGNAL("clicked()"), self.openDialog)
        self.connect(self.modifyBtn, QtCore.SIGNAL("clicked()"), self.openDialog)
        
        self.connect(self.tableview, QtCore.SIGNAL("doubleClicked(const QModelIndex &)"), self.doubleClick)
        
        

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
        
        #Check if more than one row is selected
        indexList = self.tableview.selectionModel().selectedIndexes()
        if (len(indexList) > 1):
            QtGui.QMessageBox.information(self, "Modify - Multiple Rows Selected", "Multiple Rows Selected - Please Choose A Single Row")
            return
        elif (len(indexList) is 0):
            QtGui.QMessageBox.information(self, "Modify", "No Row Selected - Please Choose A Single Row")
            return
        
        row = indexList[0].row()
        #rowData = self.tablemode.getRowData(row)
        #rowData = components[row]

        #indexRow = self.tableview.selectionModel()
        self.dialog = componentDialog(self, 'modify', row)
        #self.dialog.move(100,90)
        #Modal Dialog
        self.dialog.exec_()
        
    def openAddDialog(self):
        self.dialog = componentDialog(self, 'add')
        self.dialog.exec_()
        
    def doubleClick(self, index):   
        if header[index.column()] == DATASHEET:
            self.openDatasheet(index)
            return
        elif header[index.column()] is not QTY:
            self.openDialog()
            return
            
    def openDatasheet(self, index):
        QtGui.QMessageBox.information(self, "Datasheet", "Here is your "+str(components[index.row()].name)+" datasheet, sir")

class componentDialog(QtGui.QDialog):
    
    def __init__(self, parent = None, action = 'add', row=-1):
        #action can be add or modify
        super(componentDialog, self).__init__(parent)
        #self.move(400,30)
        
        self.parent = parent
        self.row = row
        self.action = action
        
        if self.action == 'add':
            self.component = Component('', '', '', '', '', '', '', '', '', 2, 10, 0, [['',0], ['',0], ['',0]])
        elif self.action == 'modify':
            self.component = components[self.row]
        
        print self.component

        nameLabel = QtGui.QLabel('Name')
        manufLabel = QtGui.QLabel('Manufacturer')
        catLabel = QtGui.QLabel('Category')
        packLabel = QtGui.QLabel('Package')
        descLabel = QtGui.QLabel('Description')
        dataLabel = QtGui.QLabel('Datasheet')
        commentLabel = QtGui.QLabel('Comments')
        
        self.nameEdit = QtGui.QLineEdit(self.component[NAME])
        self.manufEdit = QtGui.QComboBox()
        self.catEdit = QtGui.QComboBox()
        self.packEdit = QtGui.QComboBox()
        self.descEdit = QtGui.QLineEdit(self.component[DESCRIPTION])
        self.dataEdit = QtGui.QLineEdit(self.component[DATASHEET])
        self.commentEdit = QtGui.QTextEdit(self.component[COMMENTS])
        
        boxLabel = QtGui.QLabel('Storage Box')
        posLabel = QtGui.QLabel('Position')
        
        self.boxEdit = QtGui.QComboBox()
        self.posEdit = QtGui.QLineEdit(self.component[POSITION])
        
        minQtyLabel = QtGui.QLabel('Min. Qty Alert')
        maxQtyLabel = QtGui.QLabel('Desired Max Qty')
        qtyLabel = QtGui.QLabel('Qty')
        
        self.minQtyEdit = QtGui.QSpinBox()
        self.maxQtyEdit = QtGui.QSpinBox()
        self.qtyEdit = QtGui.QSpinBox()
        

        supplier1Label = QtGui.QLabel('Supplier 1')
        key1Label = QtGui.QLabel('KeyCode')
        
        self.supplier1Edit = QtGui.QComboBox()
        self.key1Edit = QtGui.QLineEdit(unicode(self.component.getSupplier(1, 'key')))
        
        supplier2Label = QtGui.QLabel('Supplier 2')
        key2Label = QtGui.QLabel('KeyCode')
        
        self.supplier2Edit = QtGui.QComboBox()
        self.key2Edit = QtGui.QLineEdit(unicode(self.component.getSupplier(2, 'key')))
        
        supplier3Label = QtGui.QLabel('Supplier 3')
        key3Label = QtGui.QLabel('KeyCode')
        
        self.supplier3Edit = QtGui.QComboBox()
        self.key3Edit = QtGui.QLineEdit(unicode(self.component.getSupplier(3, 'key')))

        manufList = sorted(components.getManufacturers())
        self.manufEdit.addItems(manufList)
        self.manufEdit.setEditable(True)
        self.manufEdit.setCurrentIndex(manufList.index(self.component[MANUFACTURER]))
        
        catList = sorted(components.getCategories())
        self.catEdit.addItems(catList)
        self.catEdit.setEditable(True)
        self.catEdit.setCurrentIndex(catList.index(self.component[CATEGORY]))
        
        packList = sorted(components.getPackages())
        self.packEdit.addItems(packList)
        self.packEdit.setEditable(True)
        self.packEdit.setCurrentIndex(packList.index(self.component[PACKAGE]))
        
        locList = sorted(components.getLocation())
        self.boxEdit.addItems(locList)
        self.boxEdit.setEditable(True)
        self.boxEdit.setCurrentIndex(locList.index(self.component[LOCATION]))
        
        #suppRefList = sorted(components.getSuppliers(), key = lambda x: x[0])
        suppList = sorted(components.getSuppliers())
        print suppList
        #print suppRefList
        #suppList = [x[0] for x in suppRefList]
        #self.supplier1Edit.addItems(['RS Components','Element14','Jaycar','Conrad'])
        self.supplier1Edit.addItems(suppList)
        self.supplier1Edit.setEditable(True)
        self.supplier1Edit.setCurrentIndex(suppList.index(self.component.getSupplier(1, 'name')))
        #self.supplier1Edit.setCurrentIndex(suppList.index(self.component[LOCATION]))
        
        self.supplier2Edit.addItems(suppList)
        self.supplier2Edit.setEditable(True)
        self.supplier2Edit.setCurrentIndex(suppList.index(self.component.getSupplier(2, 'name')))
        
        self.supplier3Edit.addItems(suppList)
        self.supplier3Edit.setEditable(True)
        self.supplier3Edit.setCurrentIndex(suppList.index(self.component.getSupplier(3, 'name')))
        
        self.minQtyEdit.setMinimum(-1)
        self.minQtyEdit.setValue(int(self.component[MINQTY]))
        self.maxQtyEdit.setValue(int(self.component[DESIREDQTY]))
        self.qtyEdit.setValue(int(self.component[QTY]))
        

        buttonWidget = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Save | QtGui.QDialogButtonBox.Cancel)
        
        buttonWidget.rejected.connect(self.reject)
        buttonWidget.accepted.connect(self.accept)

        
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
        
        grid.addWidget(self.nameEdit, 0, 1)
        grid.addWidget(self.manufEdit, 1, 1)
        grid.addWidget(self.catEdit, 2, 1)
        grid.addWidget(self.packEdit, 3, 1)
        grid.addWidget(self.descEdit, 4, 1)
        grid.addWidget(self.dataEdit, 5, 1)
        grid.addWidget(self.commentEdit, 6, 1, 1, 1)

        
        locatGrid = QtGui.QGridLayout()
        locatGrid.addWidget(boxLabel, 0, 0)
        locatGrid.addWidget(posLabel, 1, 0)
        
        locatGrid.addWidget(self.boxEdit, 0, 1)
        locatGrid.addWidget(self.posEdit, 1, 1)
        locatGrid.setRowStretch(2, 1)
        
        qtyGrid = QtGui.QGridLayout()
        qtyGrid.addWidget(minQtyLabel, 0, 0)
        qtyGrid.addWidget(maxQtyLabel, 1, 0)
        qtyGrid.addWidget(qtyLabel, 3, 0)
        qtyGrid.setRowStretch(4, 1)
        
        qtyGrid.addWidget(self.minQtyEdit, 0, 1)
        qtyGrid.addWidget(self.maxQtyEdit, 1, 1)
        qtyGrid.setRowMinimumHeight(2, 20)
        qtyGrid.addWidget(self.qtyEdit, 3, 1)
        
        #x, y = 0, 0
        #for supplierName, refCode in suppliers:
            #reorderGrid.addwidget(supplierName, y, x)
            #reorderGrid.addWidget( #add supplierEdit fn
        
        reorderGrid = QtGui.QGridLayout()
        reorderGrid.addWidget(supplier1Label, 0, 0)
        reorderGrid.addWidget(self.supplier1Edit, 0, 1)
        reorderGrid.addWidget(key1Label, 0, 2)
        reorderGrid.addWidget(self.key1Edit, 0, 3)
        
        reorderGrid.addWidget(supplier2Label, 1, 0)
        reorderGrid.addWidget(self.supplier2Edit, 1, 1)
        reorderGrid.addWidget(key2Label, 1, 2)
        reorderGrid.addWidget(self.key2Edit, 1, 3)
        
        reorderGrid.addWidget(supplier3Label, 2, 0)
        reorderGrid.addWidget(self.supplier3Edit, 2, 1)
        reorderGrid.addWidget(key3Label, 2, 2)
        reorderGrid.addWidget(self.key3Edit, 2, 3)
        
        
        groupBox.setLayout(locatGrid)
        reorderBox.setLayout(reorderGrid)
        qtyBox.setLayout(qtyGrid)
        
        grid.addWidget(groupBox, 0, 2, 5, 1)
        grid.addWidget(reorderBox, 7, 0, 3, 2)
        grid.addWidget(qtyBox, 6, 2, 3, 1)
        grid.addWidget(buttonWidget, 9, 2, 1, 1)
        
        commentLayout = QtGui.QHBoxLayout()
        commentLayout.addWidget(commentLabel)
        commentLayout.addWidget(self.commentEdit)
        
        
        
        
        topLeftLayout = QtGui.QVBoxLayout()

        topLayout = QtGui.QHBoxLayout()

        topLayout.addLayout(grid)

        self.setLayout(topLayout)

        
        self.setGeometry(300, 300, 650, 350)
        self.setWindowTitle('Component Viewer')
        #self.statusBar().showMessage('Welcome')
        
        #self.show()
        
        
    def accept(self):
        #global components
        class NameError(Exception): pass
        class QtyError(Exception): pass
        name = unicode(self.nameEdit.text())
        manuf = unicode(self.manufEdit.currentText())
        cat = unicode(self.catEdit.currentText())
        pack = unicode(self.packEdit.currentText())
        desc = unicode(self.descEdit.text())
        data = unicode(self.dataEdit.text())
        comments = unicode(self.commentEdit.toPlainText())
        loc = unicode(self.boxEdit.currentText())
        pos = unicode(self.posEdit.text())
        minqty = self.minQtyEdit.value()
        desqty = self.maxQtyEdit.value()
        qty = self.qtyEdit.value()
        supp1 = [self.supplier1Edit.currentText(), self.key1Edit.text()]
        supp2 = [self.supplier2Edit.currentText(), self.key2Edit.text()]
        supp3 = [self.supplier3Edit.currentText(), self.key3Edit.text()]
            
        try:
            if len(name) == 0:
                raise NameError, ("The name can not be left empty.")
            
            if minqty > desqty:
                raise QtyError, ("Minimum Qty can not be greater than the desired Qty")
            
        except NameError, e:
            QtGui.QMessageBox.warning(self, "Name Error", unicode(e))
            self.nameEdit.selectAll()
            self.nameEdit.setFocus()
            return
        
        except QtyError, e:
            QtGui.QMessageBox.warning(self, "Minimum Qty Error", unicode(e))
            self.minQtyEdit.selectAll()
            self.minQtyEdit.setFocus()
            return
        
        if  self.action == 'add':
            print "Parent:", self.parent
            self.parent.tablemode.insertRows(self.row, 1)
            components.addComponent(self.component)
        
        components[self.row][NAME] = name
        components[self.row][MANUFACTURER] = manuf
        components[self.row][CATEGORY] = cat
        components[self.row][PACKAGE] = pack
        components[self.row][DESCRIPTION] = desc
        components[self.row][DATASHEET] = data
        components[self.row][COMMENTS] = comments
        components[self.row][LOCATION] = loc
        components[self.row][POSITION] = pos
        components[self.row][MINQTY] = minqty
        components[self.row][DESIREDQTY] = desqty
        components[self.row][QTY] = qty
        components[self.row][SUPPLIERS] = [supp1, supp2, supp3]
        
        if self.action == 'add':
            self.parent.tablemode.endInsertRows()
            
        components.recreateSets()
        print "Manuf sets:", sorted(components.getManufacturers())
        
        QtGui.QDialog.accept(self)



class MyTableModel(QtCore.QAbstractTableModel):
    def __init__(self, header, *args):
        QtCore.QAbstractTableModel.__init__(self, *args)
        self.header = header
    def rowCount(self, parent):
        return len(components)
    def columnCount(self, parent):
        return len(header)
    def data(self, index, role):
        if not index.isValid():
            return None
        #Show existing data when editing
        elif role == QtCore.Qt.EditRole:
            return components[index.row()][header[index.column()]]
        elif role == QtCore.Qt.TextColorRole and header[index.column()] == QTY:
            qty = int(components[index.row()][header[index.column()]])
            minQty = int(components[index.row()][MINQTY])
            if qty <= minQty:
                return QtGui.QColor(QtCore.Qt.red)
            else:
                return QtGui.QColor(QtCore.Qt.black)
        elif role == QtCore.Qt.BackgroundColorRole and header[index.column()] == QTY:
            qty = int(components[index.row()][header[index.column()]])
            minQty = int(components[index.row()][MINQTY])
            if qty <= minQty:
                return QtGui.QColor(255,232,232)
            else:
                return QtGui.QColor(255,255,255)
        elif role == QtCore.Qt.TextAlignmentRole and header[index.column()] == QTY:
            return int(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        elif role != QtCore.Qt.DisplayRole:
            return None     
        #QtGui.QBrush.setGreen()
        return components[index.row()][header[index.column()]]
    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return dataLabels[header[col]]
            #if col < len(header):
                #return dataLabels[header[col]]
        return None
        
    def flags(self, index):
        if not index.isValid() or header[index.column()] is not QTY:
            #return QtCore.Qt.ItemIsEnabled
            return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index))
        return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index) | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable)
    
    #setData must be implemented for editable model subclasses - must also emit the dataChanged signal
    #Rapid GUI Programming Pg 449 Table 14.2
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        global components
        if index.isValid() and 0 <= index.row() < len(components):
            column = index.column()
            if header[column] == QTY:
                try: #Make sure it's an integer
                    components[index.row()][QTY] = int(value)
                except:
                    return False
            self.emit(QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
                
            return True
        return False
    
    def getRowData(self, row):
        return components[row]
    
    def sort(self, col, order):
        global components
        print components
        """sort table by given column number col"""
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        #componentsList = sorted(components, key=operator.itemgetter(col))
        componentsList = sorted(components, key=lambda component: component.name)
        print "Col:", col
        print componentsList
        print components
        if order == QtCore.Qt.DescendingOrder:
            componentsList.reverse()
        self.emit(QtCore.SIGNAL("layoutChanged()"))
        
    #def insertRow(self, row, parent):
    #    return self.insertRows(row, 1, parent)

    def insertRows(self, position, rows=1, index=QtCore.QModelIndex()):
        self.beginInsertRows(QtCore.QModelIndex(), position, position + rows - 1)
        #TODO Open Dialog Box
        #for row in range(rows):
            #components.addComponent(position + row, ['Extra', 'Transistor', 'All in one package', 'Through Hole', '10', 'Texas', 'No'])
        #self.endInsertRows()
        return True
    
    def removeRows(self, position, rows=1, index=QtCore.QModelIndex()):
        global components
        self.beginRemoveRows(QtCore.QModelIndex(), position, position + rows - 1)
        #components = components[:position] + components[position + rows:]
        components.removeComponents(position, rows)
        self.endRemoveRows()
        return True

class qtyEditDelegate(QtGui.QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        sbox = QtGui.QSpinBox(parent)
        sbox.setRange(0, 99999)
        return sbox
    
    def setEditorData(self, editor, index):
        itemVar = index.data(QtCore.Qt.DisplayRole)
        #itemStr = itemVar.toPyObject()
        itemInt = int(itemVar)
        editor.setValue(itemInt)
        
    def setModelData(self, editor, model, index):
        dataInt = editor.value()
        #dataVar = QtCore.QVariant(dataInt)
        model.setData(index,dataInt)

def main():

    app = QtGui.QApplication(sys.argv)
    ex = Window()
    sys.exit(app.exec_())
    print components

if __name__ == '__main__':
    main()
