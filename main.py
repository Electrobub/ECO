#!/usr/bin/python
# -*- coding: utf-8 -*-
#TODO
#Something wrong with inserRows??? Cannot add components
#Segfault
#Try:
# in InsertRows():
#       beginInsertRows()
#       List_to_add_to.insert()
#       endInsertRows()
#       return True
#
# Really necessary to reimplement insertRows()? (tried using insertRow... But it doesn't seem to update the view once you are back on the main screen... Until you initiate a refresh such as sorting it...)
# 
# BOTH WORK:
# self.parent.tablemode.insertRow(self.parent.tablemode.rowCount(QtCore.QModelIndex()))
# self.parent.tablemode.insertRows(self.parent.tablemode.rowCount(QtCore.QModelIndex()), 1)
# 
# It's working... It was because row was set to -1 for the Component object... Obviously there are errors if that value is used for the row in QT!! 0.0

#TODO
# - Get relative filename for PDF datasheet
# - Add Same Name Check # is this important? As there can be different packages of same chip -> as long as the (name + package) are unique 
# - Add checks if datasheets / exports directory exists
# - Add icon

#TODO
# - componentDialog - add datasheet lineedit underneath comments? Look nicer?

#DONE (From TODO Lists)
# - Fix Table Sorting (implement __lt__ in ComponentClass? Or other that is required)
# - Check if components.txt file exists, if not create one (Doesn't actually check - opens in append extended mode + seeks to beginning) Create a file if it doesn't already exist
# - Filenames with disallowed characters (eg. /) will not save as file (datasheet pdf d/l) - worth saving some other way than using component name?
# - Add regexp search box on main window (look at QSortFilterProxyModel)
# - Allow for https in url check

#Changelog v0.2 (QT5 & Python3) 30/01/19
# Added sorting by columns (with sort method of TableModel)
# Quantities added with a new component are handled as strings (same as those loaded from a CSV or an existing component)
# Creates components.txt file if it doesn't already exist
# Safe characters used in filenames (invalid characters stripped)
# Added search/filtering of selected column (with QSortFilterProxyModel)
# Accepts https:// in URLs
# Added search shortcut ctrl+F (focus/select-all)
# Fixed index problem with adding items with QSortFilterProxyModel implemented. (Had to simply move / reref. sort() from QAbstractTableModel to QSortFilterProxyModel. Turns out QSortFilterProxyModel reimplements sort() that operates on sortRole()... Read the Docs more closely!!! http://doc.qt.io/qt-5/qsortfilterproxymodel.html )
# super() syntax updated to PY3
# Add checking / removal of commas in any fields (stop screwing up CSV) -> This is a non-issue with csv library...

# v0.2.1
# Add Storage Check - with component dialog (to make sure other component is not in that spot)
# Add Prompt before closing to handle unsaved changes
# Fix -> supplierListIndex starts at 0 (historic reason it was different?...)
# Fixed importing numbers as INTs (CSV read) - helps with exporting code
# Add reorder list export (All by preference (eg. Supplier 1 not Supplier 2) or by individual supplier)
# Fix components.txt -> .csv + minor fix in filename variable

"""
Create a QSortFilterProxyModel and setModel() of the QTableView to it.
setSourceModel() of your QSortFilterProxyModel to your subclassed model.
Set the string you want to filter on using setFilterFixedString() or setFilterRegExp() in your QSortFilterProxyModel

From: https://stackoverflow.com/questions/6785481/how-to-set-filter-option-in-qtablewidget
"""

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

# Checking datasheet response
URLDOWNLOAD = 0
URLTEXT = 1

DATASHEET_DIR = "datasheets/"
EXPORT_DIR    = "exports/"

import sys
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
import operator
from components import ComponentContainer, Component
#import urllib2 #Python 2
from urllib.request import urlopen
import subprocess
import re
import csv

header = [NAME, CATEGORY, DESCRIPTION, PACKAGE, DATASHEET, QTY]
headerSizes = [150, 150, 200, 50, 100, 50]
headerPercent = [18, 18, 30, 10, 12, 12]
windowWidth = 850
unsavedState = False
#header = ['Name', 'Category', 'Description', 'Package', 'Qty', 'Manufacturer', 'Datasheet']
#data = [['2N222', 'Transistor', 'All in one package', 'Through Hole', '10', 'Texas', 'No'],
#['WOWZa', 'MOSFET', 'Does what its told', 'Through Hole', '2', 'SM', 'No']]

dataLabels = ['Name', 'Manufacturer', 'Category', 'Package', 'Description', 'Datasheet', 'Comments', 'Location', 'Position', 'Minimum Qty.', 'Desired Qty.', 'Qty']
#dataset = [['2N2222', 'Fairchild', 'Transistors', 'NPN General-Purpose Amplifier', 'TO-92', 'http://datasheet.com', 'Very useful chip to have on hand', 'Storage Box', 'A7', '3', '10', '5'], ['LM741', 'Texas Instruments', 'Op-Amp', 'General Purpose Op-Amp', 'PDIP-8', 'http://datasheet.com', 'Not the prettiest but does the job', 'Storage Box', 'B2', '2', '5', '5']]

#components = ComponentContainer('components.csv')
components = ComponentContainer()

#components.addComponent(Component('LM741', 'Texas Instruments', 'Op-Amp', 'PDIP-8', 'General Purpose Op-Amp', 'http://datasheet.com', 'Not the prettiest but does the job', 'Storage Box', 'B2', '2', '5', '5', [['RS', 1111], ['Conrad', 2222], ['YoShop', 3333]]))
#components.addComponent(Component('2N2222', 'Fairchild', 'Transistors', 'TO-92', 'NPN General-Purpose Amplifier', 'http://datasheet.com', 'Very useful chip to have on hand', 'Storage Box', 'A7', '3', '10', '5', [['RS', 1111], ['Conrad', 2222], ['YoShop', 3333]]))

#components.recreateSets()   
components.loadCsvFile("components.csv")

class Window(QtWidgets.QMainWindow):
    
    def __init__(self):
        #super(Window, self).__init__()
        super().__init__()
        
          
        self.formWidget = Overview(self) 
        self.setCentralWidget(self.formWidget) 
        
        #Actions
        openAction = QtWidgets.QAction('&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open File')
        
        saveAction = QtWidgets.QAction('&Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save File')
        #self.connect(saveAction, QtCore.SIGNAL("clicked()"), components.saveCsvFile)
        saveAction.connect(QtCore.SIGNAL("triggered()"), self.formWidget.saveDialog)

        addAction = QtWidgets.QAction('&Add', self)
        addAction.setShortcut('Ctrl+A')
        addAction.setStatusTip('Add a new component')
        addAction.connect(QtCore.SIGNAL("triggered()"), self.formWidget.openAddDialog)

        modifyAction = QtWidgets.QAction('&Modify', self)
        modifyAction.setShortcut('Ctrl+M')
        modifyAction.setStatusTip('Modify selected component')
        modifyAction.connect(QtCore.SIGNAL("triggered()"), self.formWidget.openModifyDialog)
        #addAction.triggered.connect()

        reorderAction = QtWidgets.QAction('Generate &Reorder List', self)
        reorderAction.setShortcut('Ctrl+R')
        reorderAction.setStatusTip('Generate Reordering List')
        reorderAction.connect(QtCore.SIGNAL("triggered()"), self.formWidget.openReorderDialog)
        
        aboutAction = QtWidgets.QAction('&About', self)
        aboutAction.setStatusTip('About Electronic Components Organiser')
        aboutAction.connect(QtCore.SIGNAL("triggered()"), self.aboutDialog)
        #addAction.triggered.connect()

        

        #Menubar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addSeparator()
        fileMenu.addAction(addAction)
        fileMenu.addAction(modifyAction)

        fileMenu = menubar.addMenu('&Tools')
        fileMenu.addAction(reorderAction)
        
        fileMenu = menubar.addMenu('&Help')
        fileMenu.addAction(aboutAction)
        #fileMenu.addAction(aboutAction)

        findBox = QtWidgets.QWidgetAction(self)
        findBox.setDefaultWidget(QtWidgets.QLineEdit(self))
        #bMenu
        #menubar.addAction("test", findBox)
        #menubar.addSeparator()
        #menubar.setCornerWidget(QtWidgets.QLineEdit(self))
        #menubar.
        
        
        self.setGeometry(300, 300, 850, 550)
        self.setWindowTitle('Electronic Components Organiser')
        self.statusBar().showMessage('Welcome')
        #self.move(200,40)
        
        self.show() #resizeEvent is called
        
        print("Other size:", self.width())
        
    def aboutDialog(self):
        QtWidgets.QMessageBox.information(self, "About", "Components Organiser was made when I could not find a simple program with the options I was looking for to help me organise my SMD components.\n\nThis program was made using Python & QT \n\n\n By: Electrobub")
    
    def resizeEvent (self, event):
        #Call methods to auto update the size of headers

        self.formWidget.windowResized(event)

    def closeEvent(self, event):
        if unsavedState is True:
            reply = QtWidgets.QMessageBox.warning(self, 'Unsaved Changes', 
                            "Components have been modified.\nDo you want to save your changes?", QtWidgets.QMessageBox.Save|QtWidgets.QMessageBox.Discard|QtWidgets.QMessageBox.Cancel)

            if reply == QtWidgets.QMessageBox.Save:
                components.saveCsvFile()
                event.accept()
            elif reply == QtWidgets.QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()

class Overview(QtWidgets.QWidget):

    def __init__(self, parent = None):
        #super(Overview, self).__init__(parent)
        super().__init__(parent)
        
        self.initUI()

    def initUI(self):


        """nameLabel = QtWidgets.QLabel('Name')
        catLabel = QtWidgets.QLabel('Category')
        descLabel = QtWidgets.QLabel('Description')
        packLabel = QtWidgets.QLabel('Package')
        qtyLabel = QtWidgets.QLabel('Qty')
        manufLabel = QtWidgets.QLabel('Manufacturer')
        dataLabel = QtWidgets.QLabel('Datasheet')"""
        
        # Create the view
        self.tableview = QtWidgets.QTableView()
        self.delegate = qtyEditDelegate()
        
        # Set the Model
        self.tablemode = MyTableModel(self)
        #self.tableview.setModel(self.tablemode)   #OLD - just tablemodel no filtering

        self.proxymodel = MySortFilterModel(self)
        #self.proxymodel = QtCore.QSortFilterProxyModel(self)#MySortFilterModel(self)
        self.proxymodel.setSourceModel(self.tablemode)
        self.tableview.setModel(self.proxymodel)
        self.tableview.setItemDelegate(self.delegate)

        #Enable Sorting
        self.tableview.setSortingEnabled(True)
        
        #Select Whole Rows
        self.tableview.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        
        #Hide Grid
        #self.tableview.setShowGrid(False)
        
        #Disable Horizontal Scrollbar
        self.tableview.horizontalScrollBar().setDisabled(True)
        self.tableview.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        #Resize Mode
        self.tableview.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
        #self.tableview.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.Interactive)
        #self.tableview.horizontalHeader().setResizeMode(0, QtWidgets.QHeaderView.Interactive)
        self.tableview.horizontalHeader().setStretchLastSection(True)
        

        self.removeBtn = QtWidgets.QPushButton('Remove', self)
        self.removeBtn.setStatusTip('Remove Selected Component')
        self.modifyBtn = QtWidgets.QPushButton('Modify', self)
        self.modifyBtn.setStatusTip('Modify selected component')
        self.addBtn = QtWidgets.QPushButton('Add', self)
        self.addBtn.setStatusTip('Add a new component')
        self.connect(self.removeBtn, QtCore.SIGNAL("clicked()"), self.removeSelectedRows)
        self.connect(self.addBtn, QtCore.SIGNAL("clicked()"), self.openAddDialog)
        #self.connect(self.addBtn, QtCore.SIGNAL("clicked()"), self.openModifyDialog)
        self.connect(self.modifyBtn, QtCore.SIGNAL("clicked()"), self.openModifyDialog)
        
        self.connect(self.tableview, QtCore.SIGNAL("doubleClicked(const QModelIndex &)"), self.doubleClick)
        
        self.tableview.horizontalHeader().sectionResized.connect(self.resizeColumnWidth)
        

        # NEW ---------------------------------------------
        self.searchBox = QtWidgets.QLineEdit()
        self.searchBox.setPlaceholderText("Find")   # Use QLineEdit::selectAll() ? To grab in text when box is selected?
        self.searchBox.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred) #Ignores the following - width - if not present...
        self.searchBox.setMinimumSize(200, 10)
        self.searchFocus = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+F"), self)
        self.connect(self.searchFocus, QtCore.SIGNAL("activated()"), self.searchBox.setFocus)
        self.connect(self.searchFocus, QtCore.SIGNAL("activated()"), self.searchBox.selectAll)

        self.searchCol = QtWidgets.QComboBox()
        self.searchCol.setMinimumSize(100, 0)
        self.searchCol.addItems([dataLabels[x] for x in header])

        self.connect(self.searchBox, QtCore.SIGNAL("textChanged(const QString &)"), self.filterText)
        self.connect(self.searchCol, QtCore.SIGNAL("currentIndexChanged(int)"), self.filterCol)

        topLayout = QtWidgets.QHBoxLayout()
        topLayout.addStretch()
        topLayout.addWidget(self.searchCol)
        topLayout.addWidget(self.searchBox)
        # --------------------------------------------------

        bottomLayout = QtWidgets.QHBoxLayout()
        bottomLayout.addStretch()
        bottomLayout.addWidget(self.removeBtn)
        bottomLayout.addWidget(self.modifyBtn)
        bottomLayout.addWidget(self.addBtn)

        midLayout = QtWidgets.QVBoxLayout()
        midLayout.addLayout(topLayout) # NEW------------------------- 
        midLayout.addWidget(self.tableview)
        midLayout.addLayout(bottomLayout)

        self.setLayout(midLayout)
        
        self.printSectionSizes(self.tableview)
        
        self.setHeaderSizes(self.tableview)
        
        self.printSectionSizes(self.tableview)
        
        print("Sizehint:", self.tableview.sizeHint())
        
        print("Self Width:", self.tableview.width())
        
    def updateUi(self):
        
        print("rowCount:", self.tablemode.rowCount(self))
        print("columnCount:", self.tablemode.columnCount(self))
        
        
        #print self.tableview.selectionModel().currentIndex()
        #print self.tableview.selectionModel().selectedIndexes()
       
        self.tablemode.insertRows(0)
        
        #self.emit(QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)

        """QtWidgets.QToolTip.setFont(QtWidgets.QFont('SansSerif',  10))

        self.setToolTip('This is a <b>QWidge</b> widget')

        btn = QtWidgets.QPushButton('Button', self)
        btn.setToolTip('This is a <b>QPushButton</b> widget')
        btn.move(50, 50)"""

        #self.show()
    
    def getRowList(self, indexList):
        temp = set()
        for line in indexList:
            temp.add(line.row())
        return list(temp)
       
    def filterText(self, text):
        self.proxymodel.setFilterRegExp(QtCore.QRegExp(text, QtCore.Qt.CaseInsensitive, QtCore.QRegExp.FixedString)) #Change to QRegularExpression

    def filterCol(self, col):
        self.proxymodel.setFilterKeyColumn(col)

    def removeSelectedRows(self):
        
        #Get index list of all selected cells
        indexList = self.tableview.selectionModel().selectedIndexes()
        rowList = self.getRowList(indexList)
        
        if (len(rowList) < 1):
            return
        
        if QtWidgets.QMessageBox.question(self, "Remove Components", ("Are you sure you want to remove "+str(len(rowList))+" components?"), QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
            return
        
        firstRow = rowList[0]
        lastRow = rowList[-1]
        
        rowsToDelete = lastRow - firstRow + 1

        self.tablemode.removeRows(firstRow, rowsToDelete)
        
        
    def openModifyDialog(self):
        
        #Check if more than one row is selected
        indexList = self.tableview.selectionModel().selectedIndexes()
        rowList = self.getRowList(indexList)
        if (len(rowList) > 1):
            QtWidgets.QMessageBox.information(self, "Modify - Multiple Rows Selected", "Multiple Rows Selected - Please Choose A Single Row")
            return
        elif (len(rowList) is 0):
            QtWidgets.QMessageBox.information(self, "Modify", "No Row Selected - Please Choose A Single Row")
            return
        
        row = rowList[0]
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
            self.openModifyDialog()
            return
    
    def saveDialog(self):
        global unsavedState
        if QtWidgets.QMessageBox.question(self, "Save", ("Are you sure you want to save components?"), QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
            return
        components.saveCsvFile()
        unsavedState = False
    
    def openDatasheet(self, index):
        QtWidgets.QMessageBox.information(self, "Datasheet", "Here is your "+str(components[index.row()].name)+" datasheet, sir")
        print("PDF: ", components[index.row()].datasheet)
        #subprocess.call("xdg-open", str(components[index.row()].datasheet))
        #Linux
        if sys.platform == 'linux': #was linux2 in python2
            subprocess.call(["xdg-open " + str(components[index.row()].datasheet)], shell=True)
        #Windows / Mac
        else:
            subprocess.call(["open " + str(components[index.row()].datasheet)], shell=True)
        #Windows
        #os.startfile(filepath)
        
        
    def printSectionSizes(self, tableview):
        for x in range(len(header)):
            print("Header:", x, "Size:", self.tableview.horizontalHeader().sectionSize(x))
            
        x = 6
        print("Header:", x, "Size:", self.tableview.horizontalHeader().sectionSize(x))
        print("Length:", self.tableview.horizontalHeader().length())
    
    def setHeaderSizes(self, tableview):
        for x in range(len(header)):
            self.tableview.horizontalHeader().resizeSection(x, headerSizes[x]) 

    def windowResized(self, event):
        global windowWidth
        windowWidth =  event.size().width()
        print("Event width:", windowWidth)
        self.resizeHeaders()
        
    def resizeHeaders(self):
        offset = 25 #Offset of windowsize to widgetsize
        widgetWidth = windowWidth - offset
        
        for x in range(len(header)):
            newWidth = headerPercent[x]/100.0 * widgetWidth
            self.tableview.horizontalHeader().resizeSection(x, newWidth) 
            print("Header:", x, "Size:", self.tableview.horizontalHeader().sectionSize(x))
            #print "New width:", newWidth
    
    def resizeColumnWidth(self, index, oldSize, newSize):
        pass
    #def resizeColumnWidth(self, index, oldSize, newSize):
        #print "Index:", index
        ##Update the header percentage proportions
        #print "WindowWidth:",windowWidth
        #print "Oldsize:", oldSize
        #print "Newsize:", newSize
        #oldPercent = headerPercent[index]
        #newPercent = newSize * 100.0 / windowWidth
        #diffPercent = newPercent - oldPercent
        ##diffPercent = 0
        
        #print "DiffPercent:", diffPercent
        
        #headerPercent[index] = headerPercent[index] + diffPercent
        
        ##if newSize > oldSize:
            ##headerPercent[index] = headerPercent[index] + diffPercent
        ##else:
            ##headerPercent[index] = headerPercent[index] - diffPercent
        
        #print "Old Percent:", oldPercent
        #print "New Percent:", newPercent
        #print "Column Resized"

    def openReorderDialog(self):
        self.dialog = reorderDialog(self)
        self.dialog.exec_()
        
class reorderDialog(QtWidgets.QDialog):
    
    def __init__(self, parent = None):
        super().__init__(parent)
        
        self.parent = parent
        self.status = -1

        exportAllLabel = QtWidgets.QLabel('Export all based on preferences')
        self.exportAllBtn = QtWidgets.QPushButton("Export All")

        self.supplierList = QtWidgets.QComboBox()
        exportIndivLabel = QtWidgets.QLabel('Export individual supplier')
        self.exportIndivBtn = QtWidgets.QPushButton("Export")
        
        self.connect(self.exportAllBtn, QtCore.SIGNAL('clicked()'), self.exportReorderAll)
        self.connect(self.exportIndivBtn, QtCore.SIGNAL('clicked()'), self.exportReorderSupplier)
        
        self.supplierList.addItems(self.listReorderSuppliers())

        grid = QtWidgets.QGridLayout()
        grid.addWidget(exportAllLabel, 0, 0)
        grid.addWidget(self.exportAllBtn, 1, 1)

        grid.addWidget(exportIndivLabel, 2, 0)
        grid.addWidget(self.supplierList, 3, 0)
        grid.addWidget(self.exportIndivBtn, 3, 1)
        
        #self.resize(270, 80)
        self.setWindowTitle('Reorder')
        
        self.setLayout(grid)

    def listReorderSuppliers(self):
        tempList = list()

        for component in components:
            if component.qty <= component.minqty:  
                for supplier, ref in component.suppliers:
                    if supplier not in tempList and supplier != '':
                        tempList.insert(0, supplier)
        return tempList

    def processReorderList(self, supplierIndiv = None):
        tempList = list()

        for component in components:
            if component.qty <= component.minqty:
                if supplierIndiv is not None:
                    for index, supplier in enumerate(component.suppliers):
                        supplierName = supplier[0]
                        if supplierName == supplierIndiv:
                            tempList.append([component.getSupplier(index, 'name'), component.getSupplier(index, 'ref'), component[NAME], component[PACKAGE], component[DESIREDQTY] - component[QTY]])
                else:
                    tempList.append([component.getSupplier(0, 'name'), component.getSupplier(0, 'ref'), component[NAME], component[PACKAGE], component[DESIREDQTY] - component[QTY]])
        
        tempList = sorted(tempList, key=lambda tempList: tempList[0])
        return tempList

    def exportReorderAll(self):
        reorderList = self.processReorderList()     
        self.saveSuppliersCsv(reorderList, "exports/"+"reorder_list_ALL.csv")

    def exportReorderSupplier(self):
        supplierIndiv = self.supplierList.currentText()
        reorderList = self.processReorderList(supplierIndiv)
        self.saveSuppliersCsv(reorderList, "exports/"+"reorder_list_"+supplierIndiv+".csv")

    def saveSuppliersCsv(self, reorderList, filename):
        print("Exporting Reorder List...")
        self.filename = filename
        with open(self.filename, 'wt') as csvfile:
            compWriter = csv.writer(csvfile, delimiter=',', quotechar='"')
            compWriter.writerow(["Supplier", "Supplier Reference", "Part Name", "Package", "Qty to Order"])
            for row in reorderList:
                compWriter.writerow(row)

class urlDatasheetDialog(QtWidgets.QDialog):
    
    def __init__(self, parent = None):
        #super(urlDatasheetDialog, self).__init__(parent)
        super().__init__(parent)
        
        self.parent = parent
        self.status = -1
        
        self.urlLabel = QtWidgets.QLabel('URL')
        self.urlEdit = QtWidgets.QLineEdit()
        
        self.addUrlBtn = QtWidgets.QPushButton("Add")
        self.dlUrlBtn = QtWidgets.QPushButton("Download")
        self.btnBox = QtWidgets.QDialogButtonBox()
        self.btnBox.addButton(self.addUrlBtn, QtWidgets.QDialogButtonBox.AcceptRole)
        self.btnBox.addButton(self.dlUrlBtn, QtWidgets.QDialogButtonBox.ActionRole)
        
        self.connect(self.addUrlBtn, QtCore.SIGNAL('clicked()'), self.addUrl)
        self.connect(self.dlUrlBtn, QtCore.SIGNAL('clicked()'), self.dlFile)
        
        grid = QtWidgets.QGridLayout()
        grid.addWidget(self.urlLabel, 0, 0)
        grid.addWidget(self.urlEdit, 0, 1)
        grid.addWidget(self.btnBox, 1, 0, 1, 2)
        
        self.resize(270, 80)
        self.setWindowTitle('Datasheet')
        
        self.setLayout(grid)
        #self.connect(self.dataFileBtn, QtCore.SIGNAL('clicked()'), self.selectFile)
    
    def addUrl(self):
        url = self.getUrl()
        if (self.validUrl()):
            self.status = URLTEXT
            QtWidgets.QDialog.accept(self)
    
    def validUrl(self):
        url = self.getUrl()
        if (url.startswith(("http://", "https://")) == False):
            QtWidgets.QMessageBox.warning(self, "Input Error", "URL needs to begin with 'https://' or 'http://'")
            return False
        return True
    
    def getUrl(self):
        urlText = str(self.urlEdit.text())
        return urlText
    
    def getStatus(self):
        return self.status

    def getFilename(self):
        return self.filename
    
    def dlFile(self):
        name = self.parent.getName()
        self.filename = DATASHEET_DIR + get_valid_filename(name+".pdf")
        if (self.validUrl() == False):
            return
        url = self.getUrl()
        
        #LOOK Python 2 -> python 3
        #req = urllib2.Request(url)
        #r = urllib2.urlopen(req)
        r = urlopen(url) #Python 3
        
        headers = r.info()
        filetype = headers['Content-Type']
        
        if filetype == "application/pdf":
            try:
                f = open(self.filename, 'wb')
                f.write(r.read())
                f.close()
            except:
                QtWidgets.QMessageBox.warning(self, "File Error", "Error saving to "+self.filename)
                return
            
            QtWidgets.QMessageBox.information(self, "File Downloaded", "Successfully downloaded to "+self.filename)
            self.status = URLDOWNLOAD
            QtWidgets.QDialog.accept(self)
        else:
            QtWidgets.QMessageBox.warning(self, "File Error", "Expecting PDF file, found '"+filetype+"' instead")
            return
        #urllib.urlretrieve(url, "test.
                    
class componentDialog(QtWidgets.QDialog):
    
    def __init__(self, parent = None, action = 'add', row=-1):
        #action can be add or modify
        #super(componentDialog, self).__init__(parent)
        super().__init__(parent)
        #self.move(400,30)
        
        self.parent = parent
        self.row = row
        self.action = action
        
        if self.action == 'add':
            self.component = Component('', '', '', '', '', '', '', '', '', 2, 10, 0, [['',0], ['',0], ['',0]])
        elif self.action == 'modify':
            self.component = components[self.row]
        
        print(self.component)

        nameLabel = QtWidgets.QLabel('Name')
        manufLabel = QtWidgets.QLabel('Manufacturer')
        catLabel = QtWidgets.QLabel('Category')
        packLabel = QtWidgets.QLabel('Package')
        descLabel = QtWidgets.QLabel('Description')
        dataLabel = QtWidgets.QLabel('Datasheet')
        commentLabel = QtWidgets.QLabel('Comments')
        
        self.nameEdit = QtWidgets.QLineEdit(self.component[NAME])
        self.manufEdit = QtWidgets.QComboBox()
        self.catEdit = QtWidgets.QComboBox()
        self.packEdit = QtWidgets.QComboBox()
        self.descEdit = QtWidgets.QLineEdit(self.component[DESCRIPTION])
        self.dataEdit = QtWidgets.QLineEdit(self.component[DATASHEET])
        self.commentEdit = QtWidgets.QTextEdit(self.component[COMMENTS])
        
        self.dataFileBtn = QtWidgets.QPushButton("Browse")
        self.dataUrlBtn = QtWidgets.QPushButton("URL")
        self.dataBtnBox = QtWidgets.QDialogButtonBox()
        self.dataBtnBox.addButton(self.dataFileBtn, QtWidgets.QDialogButtonBox.ActionRole)
        self.dataBtnBox.addButton(self.dataUrlBtn, QtWidgets.QDialogButtonBox.ActionRole)
        
        self.connect(self.dataFileBtn, QtCore.SIGNAL('clicked()'), self.selectFile)
        self.connect(self.dataUrlBtn, QtCore.SIGNAL('clicked()'), self.addUrl)
        
        boxLabel = QtWidgets.QLabel('Storage Box')
        posLabel = QtWidgets.QLabel('Position')
        
        self.boxEdit = QtWidgets.QComboBox()
        self.posEdit = QtWidgets.QLineEdit(self.component[POSITION])
        
        minQtyLabel = QtWidgets.QLabel('Min. Qty Alert')
        maxQtyLabel = QtWidgets.QLabel('Desired Max Qty')
        qtyLabel = QtWidgets.QLabel('Qty')
        
        self.minQtyEdit = QtWidgets.QSpinBox()
        self.maxQtyEdit = QtWidgets.QSpinBox()
        self.qtyEdit = QtWidgets.QSpinBox()
        

        supplier1Label = QtWidgets.QLabel('Supplier 1')
        key1Label = QtWidgets.QLabel('KeyCode')
        
        self.supplier1Edit = QtWidgets.QComboBox()
        self.supplier1Edit.setMinimumSize(150, 0)
        self.key1Edit = QtWidgets.QLineEdit(str(self.component.getSupplier(0, 'key')))
        
        supplier2Label = QtWidgets.QLabel('Supplier 2')
        key2Label = QtWidgets.QLabel('KeyCode')
        
        self.supplier2Edit = QtWidgets.QComboBox()
        self.key2Edit = QtWidgets.QLineEdit(str(self.component.getSupplier(1, 'key')))
        
        supplier3Label = QtWidgets.QLabel('Supplier 3')
        key3Label = QtWidgets.QLabel('KeyCode')
        
        self.supplier3Edit = QtWidgets.QComboBox()
        self.key3Edit = QtWidgets.QLineEdit(str(self.component.getSupplier(2, 'key')))

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
        print(suppList)
        #print suppRefList
        #suppList = [x[0] for x in suppRefList]
        #self.supplier1Edit.addItems(['RS Components','Element14','Jaycar','Conrad'])
        self.supplier1Edit.addItems(suppList)
        self.supplier1Edit.setEditable(True)
        self.supplier1Edit.setCurrentIndex(suppList.index(self.component.getSupplier(0, 'name')))
        #self.supplier1Edit.setCurrentIndex(suppList.index(self.component[LOCATION]))
        
        self.supplier2Edit.addItems(suppList)
        self.supplier2Edit.setEditable(True)
        self.supplier2Edit.setCurrentIndex(suppList.index(self.component.getSupplier(1, 'name')))
        
        self.supplier3Edit.addItems(suppList)
        self.supplier3Edit.setEditable(True)
        self.supplier3Edit.setCurrentIndex(suppList.index(self.component.getSupplier(2, 'name')))
        
        self.minQtyEdit.setMinimum(-1)
        self.minQtyEdit.setValue(int(self.component[MINQTY]))
        self.maxQtyEdit.setValue(int(self.component[DESIREDQTY]))
        self.qtyEdit.setValue(int(self.component[QTY]))
        

        buttonWidget = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel)
        
        buttonWidget.rejected.connect(self.reject)
        buttonWidget.accepted.connect(self.accept)

        
        groupBox = QtWidgets.QGroupBox('Location')
        reorderBox = QtWidgets.QGroupBox('Reordering')
        qtyBox = QtWidgets.QGroupBox('Stock')
        
        grid = QtWidgets.QGridLayout()
        grid.addWidget(nameLabel, 0, 0)
        grid.addWidget(manufLabel, 1, 0)
        grid.addWidget(catLabel, 2, 0)
        grid.addWidget(packLabel, 3, 0)
        grid.addWidget(descLabel, 4, 0)
        grid.addWidget(dataLabel, 5, 0)
        grid.addWidget(commentLabel, 7, 0)
        
        grid.addWidget(self.nameEdit, 0, 1)
        grid.addWidget(self.manufEdit, 1, 1)
        grid.addWidget(self.catEdit, 2, 1)
        grid.addWidget(self.packEdit, 3, 1)
        grid.addWidget(self.descEdit, 4, 1)
        grid.addWidget(self.dataEdit, 5, 1)
        grid.addWidget(self.dataBtnBox, 6, 1)
        grid.addWidget(self.commentEdit, 7, 1, 1, 1)

        
        locatGrid = QtWidgets.QGridLayout()
        locatGrid.addWidget(boxLabel, 0, 0)
        locatGrid.addWidget(posLabel, 1, 0)
        
        locatGrid.addWidget(self.boxEdit, 0, 1)
        locatGrid.addWidget(self.posEdit, 1, 1)
        locatGrid.setRowStretch(2, 1)
        
        qtyGrid = QtWidgets.QGridLayout()
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
        
        reorderGrid = QtWidgets.QGridLayout()
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
        grid.addWidget(reorderBox, 8, 0, 3, 2)
        grid.addWidget(qtyBox, 7, 2, 3, 1)
        grid.addWidget(buttonWidget, 10, 2, 1, 1)
        
        commentLayout = QtWidgets.QHBoxLayout()
        commentLayout.addWidget(commentLabel)
        commentLayout.addWidget(self.commentEdit)
        
        
        
        
        topLeftLayout = QtWidgets.QVBoxLayout()

        topLayout = QtWidgets.QHBoxLayout()
        
        #TODO Look if this is really necessary? Grid into HBOX? Left over from start...
        topLayout.addLayout(grid)

        self.setLayout(topLayout)

        self.resize(650, 350)
        #self.setGeometry(300, 300, 650, 350)
        self.setWindowTitle('Component Viewer')
        #self.statusBar().showMessage('Welcome')
        
        #self.show()
    
    def selectFile(self):

        #datasheetDir = QtCore.QDir("datasheets")

        datasheetDir = QtCore.QDir()
        #datasheetDir.setCurrent(DATASHEET_DIR)
        #datasheet_dir = QtCore.QDir.currentPath().dir(datasheet_dir)
        #print(datasheetDir.currentPath())
        
        #file = QtWidgets.QFileDialog.getOpenFileName(self, "Open Datasheet", datasheetDir.currentPath(), "PDF(*.pdf)")
        file = QtWidgets.QFileDialog.getOpenFileName(self, "Open Datasheet", QtCore.QDir.currentPath(), "PDF(*.pdf)")
        """filename = QtCore.QFileInfo(file[0]).baseName()
        #path = QtCore.QFileInfo(file[0]).path()
        #path = QtCore.QFileInfo(file[0]).dir(QtCore.QDir.relativeFilePath(datasheetDir))\
        path = datasheetDir.relativeFilePath(file[0])
        print("Filename", filename)
        print("Path:", path)"""
        self.dataEdit.setText(QtCore.QDir.cleanPath(file[0]))
        
    def addUrl(self):
        urlDialog = urlDatasheetDialog(self)
        
        if (urlDialog.exec_()):
            status = urlDialog.getStatus()
            
            if (status == URLDOWNLOAD):
                #filename = get_valid_filename(str(self.nameEdit.text()+".pdf"))
                filename = urlDialog.getFilename()
                self.dataEdit.setText(filename)
            elif (status == URLTEXT):
                self.dataEdit.setText(urlDialog.getUrl())
    
    def getName(self):
        return str(self.nameEdit.text())
    
    def accept(self):
        #global components
        global unsavedState
        class NameError(Exception): pass
        class QtyError(Exception): pass
        class PosError(Exception): pass
        name = str(self.nameEdit.text())
        manuf = str(self.manufEdit.currentText())
        cat = str(self.catEdit.currentText())
        pack = str(self.packEdit.currentText())
        desc = str(self.descEdit.text())
        data = str(self.dataEdit.text())
        comments = str(self.commentEdit.toPlainText())
        loc = str(self.boxEdit.currentText())
        pos = str(self.posEdit.text())
        """minqty = self.minQtyEdit.value()
        desqty = self.maxQtyEdit.value()
        qty = self.qtyEdit.value()"""
        minqty = int(self.minQtyEdit.text())
        desqty = int(self.maxQtyEdit.text())
        qty = int(self.qtyEdit.text())
        supp1 = [self.supplier1Edit.currentText(), self.key1Edit.text()]
        supp2 = [self.supplier2Edit.currentText(), self.key2Edit.text()]
        supp3 = [self.supplier3Edit.currentText(), self.key3Edit.text()]
            
        try:
            if len(name) == 0:
                raise NameError("The name can not be left empty.")
            
            if minqty > desqty:
                raise QtyError("Minimum Qty can not be greater than the desired Qty")

            for row in [x for x in range(len(components)) if x != self.row]:
                component = components[row]

                if loc == component[LOCATION] and pos == component[POSITION]:
                    if not (name == component[NAME] and pack == component[PACKAGE]):
                        raise PosError("Cannot have 2 different components in the same location.\n\n"+"Already exists:\nComponent: "+component[NAME]+"\nPackage: "+component[PACKAGE])

        except NameError as e:    
        #except NameError, e:
            QtWidgets.QMessageBox.warning(self, "Name Error", str(e))
            self.nameEdit.selectAll()
            self.nameEdit.setFocus()
            return
        
        except QtyError as e:
            QtWidgets.QMessageBox.warning(self, "Minimum Qty Error", str(e))
            self.minQtyEdit.selectAll()
            self.minQtyEdit.setFocus()
            return

        except PosError as e:
            QtWidgets.QMessageBox.warning(self, "Same Position Error", str(e))
            self.posEdit.selectAll()
            self.posEdit.setFocus()
            return
        
        if  self.action == 'add':
            # remove below? Indexes are still off
            #self.parent.tablemode.beginInsertRows(QtCore.QModelIndex(), self.parent.tablemode.rowCount(QtCore.QModelIndex()), self.parent.tablemode.rowCount(QtCore.QModelIndex()))
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
            #self.parent.tablemode.insertRow(self.parent.tablemode.rowCount(QtCore.QModelIndex()))
            self.parent.tablemode.insertRows(0, 1)
            print(self.parent.tablemode.columnCount(QtCore.QModelIndex()))
            print(self.parent.proxymodel.columnCount(QtCore.QModelIndex()))
            #self.parent.proxymodel.invalidateFilter()
            # remove below?
            #self.parent.tablemode.endInsertRows()

            #self.parent.proxymodel.insertRow(self.parent.proxymodel.rowCount(QtCore.QModelIndex()))
            #self.parent.tablemode.insertRows(self.parent.tablemode.rowCount(QtCore.QModelIndex()), 1)
            
        components.recreateSets()
        print("Manuf sets:", sorted(components.getManufacturers()))

        unsavedState = True
        QtWidgets.QDialog.accept(self)




class MyTableModel(QtCore.QAbstractTableModel):
    #def __init__(self, header, *args):
    def __init__(self, parent=None):
        super().__init__(parent)
        #QtCore.QAbstractTableModel.__init__(self, parent)
        self.header = header
    def rowCount(self, parent = QtCore.QModelIndex()):
        return len(components)
    def columnCount(self, parent = QtCore.QModelIndex()):
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
        global unsavedState

        if index.isValid() and 0 <= index.row() < len(components):
            column = index.column()
            if header[column] == QTY:
                try: #Make sure it's an integer
                    components[index.row()][QTY] = int(value)
                except:
                    return False
            self.emit(QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex,)"), index, index)
            unsavedState = True
                
            return True
        return False
    
    def getRowData(self, row):
        return components[row]
    
    def sort(self, col, order):
        global components
        print(components)

        """sort table by given column number col"""
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        #componentsList = sorted(components, key=operator.itemgetter(col))
        #if order == QtCore.Qt.DescendingOrder:
        """if order == QtCore.Qt.AscendingOrder:
            components = sorted(components, key=lambda component: component.name)
        else:
            components = sorted(components, key=lambda component: component.name, reverse = True)"""
        """if order == QtCore.Qt.AscendingOrder:
            components = sorted(components, key=lambda component: component[col])
        else:
            components = sorted(components, key=lambda component: component[col], reverse = True)"""
        if order == QtCore.Qt.AscendingOrder:
            components.sort(header[col], 'asc')
        else:
            components.sort(header[col], 'desc')
        print("Col:", col)
        print(components)
        print(components[0].name)
            #componentsList.reverse()
        self.emit(QtCore.SIGNAL("layoutChanged()"))

    def insertRows(self, position, rows=1, index=QtCore.QModelIndex()):
        self.beginInsertRows(QtCore.QModelIndex(), position, position + rows - 1)
        self.endInsertRows()

        return True
    
    def removeRows(self, position, rows=1, index=QtCore.QModelIndex()):
        global components
        self.beginRemoveRows(QtCore.QModelIndex(), position, position + rows - 1)
        #components = components[:position] + components[position + rows:]
        components.removeComponents(position, rows)
        self.endRemoveRows()
        return True

class MySortFilterModel(QtCore.QSortFilterProxyModel):
    def __init__(self, parent):
        super().__init__(parent)
        self.par = parent

    def sort(self, col, order):
        self.par.tablemode.sort(col, order)

class qtyEditDelegate(QtWidgets.QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        sbox = QtWidgets.QSpinBox(parent)
        sbox.setRange(0, 99999)
        return sbox
    
    def setEditorData(self, editor, index):
        itemVar = index.data(QtCore.Qt.DisplayRole)
        itemInt = int(itemVar)
        editor.setValue(itemInt)
        
    def setModelData(self, editor, model, index):
        dataInt = editor.value()
        #dataVar = QtCore.QVariant(dataInt)
        model.setData(index,dataInt)

# ------------ Functions ---------------

def get_valid_filename(s):
    """
    From Django
    Return the given string converted to a string that can be used for a clean
    filename. Remove leading and trailing spaces; convert other spaces to
    underscores; and remove anything that is not an alphanumeric, dash,
    underscore, or dot.
    >>> get_valid_filename("john's portrait in 2004.jpg")
    'johns_portrait_in_2004.jpg'
    """
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)

# ---------------------------------------------

def main():

    app = QtWidgets.QApplication(sys.argv)
    ex = Window()
    sys.exit(app.exec_())
    print(components)

if __name__ == '__main__':
    main()

