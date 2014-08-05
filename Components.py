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
SUPPLIERS = 12


class Component(object):
    
    def __init__(self, name, manuf, cat, pack, desc, datasheet, comments, loc, pos, minqty, desqty, qty, suppliers):
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
        self.suppliers = suppliers
    
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
        elif (key==SUPPLIERS):
            return self.suppliers
        
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
        elif (key==SUPPLIERS):
            self.suppliers = value
            
    def getSupplier(self, position = 1, value = 'name'):
        listPos = position - 1
        if value == 'name':
            return self.suppliers[listPos][0]
        return self.suppliers[listPos][1]
        
class ComponentContainer(object):
    
    #Component IDs start from 1
    def __init__(self, filename):
        self.filename = (filename)
        #self.components = {} #Why use a dictionary?
        self.components = []
        self.manufacturers = set()
        self.categories = set()
        self.location = set()
        self.packages = set()
        self.suppliers = set()
    
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
        self.location.add(unicode(component.loc))
        self.packages.add(unicode(component.pack))
        
        for supp, key in component.suppliers:
            self.suppliers.add(unicode(supp))
        
        #TODO 
        # - Figure out the insertrow of the tablemodel
        # Works without needing it on KDE, maybe on Windows or Mac?
        print self.components
        print self.manufacturers
        
    def removeComponent(self, ident):
        del self.components[ident]
        
    def recreateSets(self):
        self.manufacturers.clear()
        self.categories.clear()
        self.location.clear()
        self.packages.clear()
        self.suppliers.clear()
        
        for component in self.components:
            self.manufacturers.add(unicode(component.manuf))
            self.categories.add(unicode(component.cat))
            self.location.add(unicode(component.loc))
            self.packages.add(unicode(component.pack))
            
            for supp, key in component.suppliers:
                self.suppliers.add(unicode(supp))
        print "------------------------ Recreating"
            
    
    def getManufacturers(self):
        return self.manufacturers
    
    def getCategories(self):
        return self.categories
    
    def getLocation(self):
        return self.location
    
    def getPackages(self):
        return self.packages
    
    def getSuppliers(self):
        return self.suppliers
    
    def getSortedSuppliers(self):
        sortedSuppliers = sorted(self.suppliers, key = lambda x: x[0])
        return sortedSuppliers
        

def main():
    pass


    

    

    
    
if __name__ == '__main__':
    main()

    
        