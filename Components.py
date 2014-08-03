import sys
from PySide import QtGui
from PySide import QtCore
import operator

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


class Component(object):
    
    def __init__(self, name, manuf, cat, pack, desc, datasheet, comments, loc, pos, minqty, desqty, qty):
        self.name = name
        self.manuf = manuf
        self.cat = cat
        self.pack = pack
        self.desc = desc
        self.datasheet = datasheet
        self.comments = comments
        self.loc = loc
        self.pos = pos
        self.minqty = minqty
        self.desqty = desqty
        self.qty = qty
    
    def __getitem__(self, key):
        if (key==NAME):
            return self.name
        elif (key==MANUFACTURER):
            return self.manuf
        elif (key==CATEGORY):
            return self.cat
        elif (key==PACKAGE):
            return self.pack
        elif (key==DESCRIPTION):
            return self.desc
        elif (key==DATASHEET):
            return self.datasheet
        elif (key==COMMENTS):
            return self.comments
        elif (key==LOCATION):
            return self.loc
        elif (key==POSITION):
            return self.pos
        elif (key==MINQTY):
            return self.minqty
        elif (key==DESIREDQTY):
            return self.desqty
        elif (key==QTY):
            return self.qty
        
    def __setitem__(self, key, value):
        if (key==NAME):
            self.name = value
        elif (key==MANUFACTURER):
            self.manuf = value
        elif (key==CATEGORY):
            self.cat = value
        elif (key==PACKAGE):
            self.pack = value
        elif (key==DESCRIPTION):
            self.desc = value
        elif (key==DATASHEET):
            self.datasheet = value
        elif (key==COMMENTS):
            self.comments = value
        elif (key==LOCATION):
            self.loc = value
        elif (key==POSITION):
            self.pos = value
        elif (key==MINQTY):
            self.minqty = value
        elif (key==DESIREDQTY):
            self.desqty = value
        elif (key==QTY):
            self.qty = value
        
class ComponentContainer(object):
    
    #Component IDs start from 1
    def __init__(self, filename):
        self.filename = (filename)
        #self.components = {} #Why use a dictionary?
        self.components = []
        self.manufacturers = set()
        self.categories = set()
        self.location = set()
    
    def __len__(self):
        return len(self.components)
    
    def __iter__(self):
        for component in self.components:
            yield component
    
    def __getitem__(self, key):
        return self.components[key]
    
    def __setitem__(self, key, value):
        self.components[key] = value
    
    def component(self, ident):
        return self.components.get(ident)
    
    def addComponent(self, component):
        #self.components[self.getLastId()+1] = component #Was for dictionary
        self.components.append(component)
        self.manufacturers.add(unicode(component.manuf))
        self.categories.add(unicode(component.cat))
        
        #TODO
        # - Figure out the insertrow of the tablemodel
        print self.components
        print self.manufacturers
        
    def removeComponent(self, ident):
        del self.components[ident]
        
    #def getLastId(self): #Methods for when storqge was with a dictionary
        #if len(self.components) < 1:
            #return 0
        #else:
            #return max(self.components.keys(), key=int)
        
    #def getComponent(self, row, column):
        #return self.components[row][column]
        

def main():
    
    item = Component('LM741', 'Texas Instruments', 'Op-Amp', 'General Purpose Op-Amp', 'PDIP-8', 'http://datasheet.com', 'Not the prettiest but does the job', 'Storage Box', 'B2', '2', '5', '5')
    #['LM741', 'Texas Instruments', 'Op-Amp', 'General Purpose Op-Amp', 'PDIP-8', 'http://datasheet.com', 'Not the prettiest but does the job', 'Storage Box', 'B2', '2', '5', '5']
    print item.manuf
    print 'Hey'
    print item[1]
    
    #print item[2]
    items = ComponentContainer('test.txt')
    items.addComponent(Component('LM741', 'Texas Instruments', 'Op-Amp', 'General Purpose Op-Amp', 'PDIP-8', 'http://datasheet.com', 'Not the prettiest but does the job', 'Storage Box', 'B2', '2', '5', '5'))
    items.addComponent(Component('2N2222', 'Fairchild', 'Transistors', 'NPN General-Purpose Amplifier', 'TO-92', 'http://datasheet.com', 'Very useful chip to have on hand', 'Storage Box', 'A7', '3', '10', '5'))
    
    #print items.getComponent(1,1)
    
    print "----------"
    for item in items:
        for i in range(0, QTY):
            print i
            print item[i]
           
    print items[0][10]
    items[0][10] = 2
    print items[0][10]
    
    
if __name__ == '__main__':
    main()

    
        