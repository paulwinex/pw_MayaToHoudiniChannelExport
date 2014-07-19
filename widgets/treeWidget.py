from ..mayaqtimport import *

class channelsTreeWidgetClass(QTreeWidget):
    updateInfoSignal = qtsignal()
    def __init__(self):
        super(channelsTreeWidgetClass, self).__init__()
        self.setAlternatingRowColors(True)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # self.setDragEnabled(1)
        self.setColumnCount(1)
        self.header().setVisible(False)
        self.setStyleSheet("QTreeWidget::item{ height: 20px; font-size:14;}")
        self.itemSelectionChanged.connect(self.selectObjects)

    def addObjects(self, objects):
        names = {str(self.topLevelItem(x).text(0)):x for x in range(self.topLevelItemCount())}
        for a in objects:
            #add object
            name = a.split('.')[0]
            if name in names:
                item = self.topLevelItem(names[name])
            else:
                item = QTreeWidgetItem()
                item.setText(0,name)
                self.addTopLevelItem(item)
                names[name] = self.indexOfTopLevelItem(item)
            chan = a.split('.')[-1]
            #add channel
            channels = {item.child(x).text(0): x for x in range(item.childCount())}
            if not chan in channels:
                chanItem = QTreeWidgetItem(item)
                chanItem.setText(0, chan)
        self.updateInfoSignal.emit()


    def getData(self):
        data = []
        for i in range(self.topLevelItemCount()):
            topItem = self.topLevelItem(i)
            name = topItem.text(0)
            if cmds.objExists(name):
                for j in range(topItem.childCount()):
                    atrItem = topItem.child(j)
                    atr = atrItem.text(0)
                    data.append('.'.join([name, atr]))
        return data


    def cleanNonExistsObjects(self):
        for i in range(self.topLevelItemCount()):
            topItem = self.topLevelItem(i)
            name = topItem.text(0)
            if not cmds.objExists(name):
                self.takeTopLevelItem(self.indexOfTopLevelItem(topItem))

    def getObjectsAttr(self):
        data = {}
        for i in range(self.topLevelItemCount()):
            topItem = self.topLevelItem(i)
            name = topItem.text(0)
            attrs = []
            for j in range(topItem.childCount()):
                atrItem = topItem.child(j)
                atr = atrItem.text(0)
                attrs.append(atr)
            data[name] = attrs
        return data

    def removeSelected(self):
        root = self.invisibleRootItem()
        for item in self.selectedItems():
            (item.parent() or root).removeChild(item)
        self.updateInfoSignal.emit()

    def selectObjects(self):
        sel = self.selectedItems()
        objects = []
        for s in sel:
            if self.indexOfTopLevelItem(s) >=0:
                objects.append(s.text(0))
        if objects:
            cmds.select(cl=1)
            for o in objects:
                if cmds.objExists(o):
                    cmds.select(o, add=1)
        self.updateInfoSignal.emit()

