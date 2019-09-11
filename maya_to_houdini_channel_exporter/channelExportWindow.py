import  json
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from .widgets import channelExportWindow_UI2
from widgets import MSlider
from widgets import treeWidget
import channelExporter
from widgets import filePathWidget
from pymel.core import *

gChannelBoxName = mel.eval('$temp=$gChannelBoxName')
channelsAttrName = ['mthchannelnames', 'cnm']
setAttrName = ['exportData', 'exp']

version = 1.5

class channelExporterWindowClass(QMainWindow, channelExportWindow_UI2.Ui_channelExportWindow):

    def __init__(self, *args):
        super(channelExporterWindowClass, self).__init__(*args)
        self.setupUi(self)
        # dialog_file = os.path.join(os.path.dirname(__file__), 'widgets', 'channelExportWindow.ui')
        # _loadUi(dialog_file, self)
        # __import__('__main__').__dict__['self'] = self
        self.setWindowTitle('Maya to Houdini Channel Exporter v%s' % version)
        # widgets
        self.tree = treeWidget.channelsTreeWidgetClass()
        self.tree_ly.addWidget(self.tree)
        self.outPath = filePathWidget.filePathWidgetClass(asLoad=0, ext={'Houdini CHOP file':['clip']})
        self.outFile_ly.addWidget(self.outPath)
        self.scale_sbx = MSlider.MSliderClass('Position Scale')
        self.scale_ly.addWidget(self.scale_sbx)
        # ui
        self.setRangeFromScene()
        #connect
        self.addSelectedObject_btn.clicked.connect(self.addSelectedObject)
        self.addFromChannelBox_btn.clicked.connect(self.addFromChannelBox)
        self.export_btn.clicked.connect(self.startExportUi)
        self.removeAll_btn.clicked.connect(self.clearTree)
        self.removeSelected_btn.clicked.connect(self.tree.removeSelected)
        self.setTimeLineRange_btn.clicked.connect(self.setRangeFromScene)
        self.saveToSet_btn.clicked.connect(self.saveSetData)
        self.addFromSet_btn.clicked.connect(self.loadFromSet)
        self.currentTimeToEnd_btn.clicked.connect(self.setEndFrameByCurrent)
        self.currentTimeToStart_btn.clicked.connect(self.setStartFrameByCurrent)
        self.batchMode_btn.clicked.connect(self.selectFilesToBatch)
        self.removeNonExists_btn.clicked.connect(self.tree.cleanNonExistsObjects)
        self.tree.updateInfoSignal.connect(self.showInfo)
        self.saveToFile_btn.clicked.connect(self.saveToFile)
        self.addFromFile_btn.clicked.connect(self.importFromFile)
        self.about_act.triggered.connect(self.about)
        self.manual_act.triggered.connect(self.openManual)
        #start
        self.showInfo()

    def clearTree(self):
        self.tree.clear()
        self.showInfo()

    def addSelectedObject(self):
        sel = cmds.ls(sl=1)
        objects = []
        for s in sel:
            attrs = cmds.listAttr(s,keyable=1,shortNames=1)
            if 'v' in attrs:
                attrs.remove('v')
            for atr in attrs:
                objects.append('.'.join([s,atr]))
        if objects:
            self.tree.addObjects(objects)

    def addFromChannelBox(self):
        data = []
        objects = cmds.channelBox(gChannelBoxName, q=True, mol=True)
        if not objects:
            return
        trChannels = cmds.channelBox(gChannelBoxName, q=True, sma=True)
        shChannels = cmds.channelBox(gChannelBoxName, q=True, ssa=True)
        for obj in objects:
            if trChannels:
                for atr in trChannels:
                    data.append('.'.join([obj,atr]))
            if shChannels:
                for atr in shChannels:
                    data.append('.'.join([obj,atr]))
        if data:
            self.tree.addObjects(data)

    def setRangeFromScene(self):
        st = int(cmds.playbackOptions(q=1, minTime=1))
        self.startRange_spb.setValue(st)
        en = int(cmds.playbackOptions(q=1, maxTime=1))
        self.endRange_spb.setValue(en)

    def setEndFrameByCurrent(self):
        self.endRange_spb.setValue(cmds.currentTime(q=True))

    def setStartFrameByCurrent(self):
        self.startRange_spb.setValue(cmds.currentTime(q=True))

    def startExportUi(self):
        self.startExport(auto=self.autoRange_cbx.isChecked())

    def startExport(self, frange=None, fbx=None, outFile=None, auto=False):
        channels = self.tree.getData()
        if not os.path.exists(os.path.dirname(self.outPath.path())):
            cmds.confirmDialog( title='Empty channels', message='Wrong Output Folder', button=['OK'] )
            return
        if not channels:
            cmds.confirmDialog( title='Empty channels', message='Channels list is empty', button=['OK'] )
            return
        if fbx:
            cmds.file(fbx,
                      i=1,
                      type="FBX",
                      ra=True,
                      rdn=True,
                      mergeNamespacesOnClash=True,
                      namespace=":",
                      options="groups=0;ptgroups=0;materials=0;smoothing=1;normals=1",
                      loadReferenceDepth="all"
                      )
        if not auto:
            if not frange:
                frange = [self.startRange_spb.value(),
                          self.endRange_spb.value()]
        else:
            frange = self.getAutoRange()

        if not outFile:
            outFile = self.outPath.path()
        print 'Output file:'
        print '\t', outFile
        print 'Animation Range:'
        print '\t', frange[0], ':', frange[1]
        scale = self.scale_sbx.value()
        options = dict(scale=scale)
        channelExporter.export(channels, outFile, frange, options, self.progress_pbr)
        self.progress_pbr.setValue(0)

    def getAutoRange(self):
        allCurves = cmds.ls(type='animCurve')
        if allCurves:
            maxTime = max([ x for x in [ max(cmds.keyframe(crv,q=1, tc=1)) for crv in allCurves ] ])
            minTime = min([ x for x in [ min(cmds.keyframe(crv,q=1, tc=1)) for crv in allCurves ] ])
            result = [int(minTime), int(maxTime)]
            return result
        else:
            st = int(cmds.playbackOptions(q=1, minTime=1))
            en = int(cmds.playbackOptions(q=1, maxTime=1))
            return [int(st), int(en)]

    def saveSetData(self):
        objs = self.tree.getObjectsAttr()
        if not objs:
            return
        text, ok = QInputDialog.getText(self, 'Create export set', 'Enter name:', QLineEdit.Normal,'NewSet')
        if ok:
            #check objects exists
            for o in objs.keys():
                if not cmds.objExists(o):
                    del objs[o]
            self.tree.cleanNonExistsObjects()

            setNode = cmds.sets(objs.keys(), n=text)
            for name, attrs in objs.items():
                self.addExportChannelsDataToObject(name, attrs)
            #save path
            if not cmds.attributeQuery(setAttrName[0], node=setNode, exists=True ):
                cmds.addAttr(setNode, ln=setAttrName[0], sn=setAttrName[1],  dt='string')
            # compute data
            data = dict(path=self.outPath.path(),
                        start=self.startRange_spb.value(),
                        end=self.endRange_spb.value(),
                        scale=self.scale_sbx.value(),
                        auto=self.autoRange_cbx.isChecked())
            cmds.setAttr(setNode+'.'+setAttrName[0], json.dumps(data), type="string" )

    def addExportChannelsDataToObject(self, name, attrs):
        if not cmds.attributeQuery( channelsAttrName[0], node=name, exists=True ):
            cmds.addAttr(name, ln=channelsAttrName[0], sn=channelsAttrName[1],  dt='string')
        cmds.setAttr(name+'.'+channelsAttrName[0], ';'.join(attrs), type="string" )

    def loadFromSet(self):
        menuData = []
        sets = cmds.ls(type='objectSet')
        if sets:
            menuData = [x for x in sets if cmds.attributeQuery(setAttrName[0], node=x, exists=True )]

        menu = QMenu(self)
        if menuData:
            for m in menuData:
                menu.addAction(QAction(m, self, triggered=lambda m=m: self.loadSetData(m)))
        else:
            act = QAction('No sets', self)
            act.setEnabled(0)
            menu.addAction(act)
        menu.exec_(QCursor.pos())

    def loadSetData(self, setName):
        self.tree.clear()
        data = []
        content = cmds.sets( setName, q=True )
        for c in content:
            if cmds.attributeQuery( channelsAttrName[0], node=c, exists=True ):
                attrs = cmds.getAttr(c+'.'+channelsAttrName[0])
            else:
                attrs = []
            obj = ['.'.join([c,a]) for a in attrs.split(';')]
            data += obj
        self.tree.addObjects(data)
        #load path
        if cmds.attributeQuery( setAttrName[0], node=setName, exists=True ):
            data = cmds.getAttr(setName+'.'+setAttrName[0])
            try:
                data = json.loads(data)
            except:
                data = None
            if data:
                self.scale_sbx.setValue(data.get('scale',1))
                self.startRange_spb.setValue(data.get('start', 1))
                self.endRange_spb.setValue(data.get('end',100))
                self.autoRange_cbx.setChecked(data.get('auto', False))
                self.outPath.setPath(data.get('path',''))

    def saveToFile(self):
        data = dict(channels=self.tree.getData(),
                    scale=self.scale_sbx.value(),
                    start=self.startRange_spb.value(),
                    end=self.endRange_spb.value(),
                    path=self.outPath.path(),
                    auto=self.autoRange_cbx.isChecked()
        )

        if data:
            path = QFileDialog.getSaveFileName(self,'Save channels')
            if path[0]:
                json.dump(data, open(path[0], 'w'), indent=4)

    def importFromFile(self):
        path = QFileDialog.getOpenFileName(self,
                                           'Load channels')
        if path[0]:
            try:
                data = json.load(open(path[0]))
                self.tree.addObjects(data['channels'])
                self.scale_sbx.setValue(data['scale'])
                self.startRange_spb.setValue(data['start'])
                self.endRange_spb.setValue(data['end'])
                self.outPath.setPath(data['path'])
                self.autoRange_cbx.setChecked(data['auto'])
            except:
                cmds.confirmDialog( title='Error', message='Error read file', button=['OK'] )

    def selectFilesToBatch(self):
        d=cmds.workspace( q=True, rd=True )
        path = QFileDialog.getOpenFileNames(self,'Open file',
                                            d,
                                            "FBX (*.fbx)")
        if path[0]:
            out = QFileDialog.getExistingDirectory(self, 'Output Folder',
                                                   os.path.dirname(path[0][0]))
            self.batchMode(path[0], out)

    def batchMode(self, fbxList, out):
        for i, scene in enumerate(fbxList):
            if out:
                name, ext = os.path.splitext(scene)
                name = os.path.basename(name)
                outPath = os.path.join(out, name+'.clip')
            else:
                name, ext = os.path.splitext(scene)
                outPath = name + '.clip'
            print '='*50
            print name
            print i+1, '/', len(fbxList)
            self.startExport(fbx=scene, outFile=outPath, auto=True)


    def showInfo(self):
        objectCount = self.tree.topLevelItemCount()
        channelCount = sum([self.tree.topLevelItem(x).childCount() for x in range(objectCount)])
        msg = '''\
Objects:  %s
Channels: %s''' % (objectCount, channelCount)
        self.info_lb.setText(msg)

    def openManual(self):
        import webbrowser
        webbrowser.open('http://www.paulwinex.ru/')

    def about(self):
        dial = aboutDialog(self)
        dial.show()


class aboutDialog(QDialog):
    def __init__(self, parent):
        super(aboutDialog, self).__init__(parent)
        self.parent = parent
        self.setWindowFlags( self.windowFlags() & ~Qt.WindowContextHelpButtonHint )
        self.Layout = QVBoxLayout()
        self.text = QLabel()
        self.text.setText('Maya to Houdini channel Exporter v%s\nby Paul Winex' % version)
        self.text.setAlignment(Qt.AlignCenter)
        self.text.mouseReleaseEvent = self.openLink
        self.Layout.addWidget(self.text)

        self.pushButton = QPushButton('Close')
        self.pushButton.clicked.connect(self.close)
        self.Layout.addWidget(self.pushButton)
        self.setLayout(self.Layout)
        self.resize(300,100)
        self.setWindowTitle("About MtH Channel exporter v{0}".format(version))

    def openLink(self, event):
        self.parent.openManual()