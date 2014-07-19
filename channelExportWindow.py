import os

from qtimport import *
if qt == 1:
    from widgets import channelExportWindow_UI as ui
else:
    from widgets import channelExportWindow_UIs as ui
from widgets import MSlider
reload(MSlider)
reload(ui)
from widgets import treeWidget
reload(treeWidget)
import channelDataReader
reload(channelDataReader)
from widgets import filePathWidget

gChannelBoxName = mel.eval('$temp=$gChannelBoxName')
channelsAttrName = ['mthchannelnames', 'cnm']
outPathAttrName = ['savepath', 'spt']
version = 1.1

class channelExporterWindowClass(QMainWindow, ui.Ui_channelExportWindow):
    def __init__(self, parent):
        super(channelExporterWindowClass, self).__init__(parent)
        self.setupUi(self)
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
        # self.addFromSet_btn.clicked.connect(self.loadSetData)
        self.addFromSet_btn.clicked.connect(self.loadFromSet)
        self.currentTimeToEnd_btn.clicked.connect(self.setEndFrameByCurrent)
        self.currentTimeToStart_btn.clicked.connect(self.setStartFrameByCurrent)
        self.batchMode_btn.clicked.connect(self.selectFilesToBatch)
        self.tree.updateInfoSignal.connect(self.showInfo)
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
        trChannels = cmds.channelBox(gChannelBoxName, q=True, sma=True)
        shChannels = cmds.channelBox(gChannelBoxName, q=True, ssa=True)
        for obj in objects:
            if trChannels:
                for atr in trChannels:
                    data.append('.'.join([obj,atr]))
            if shChannels:
                for atr in shChannels:
                    data.append('.'.join([obj,atr]))
        # return data
        if data:
            # print data
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

        channels = self.tree.getData()
        print 'Output file:'
        print '\t', outFile
        # print 'Channels:'
        # for c in channels:
        #     print '\t', c
        print 'Animation Range:'
        print '\t', frange[0], ':', frange[1]
        scale = self.scale_sbx.value()
        options = dict(scale=scale)
        channelDataReader.export(channels, outFile,frange, self.progress_pbr, options)
        self.progress_pbr.setValue(0)

    def getAutoRange(self):
        maxTime = max([ x for x in [ max(cmds.keyframe(crv,q=1, tc=1)) for crv in cmds.ls(type='animCurve') ] ])
        minTime = min([ x for x in [ min(cmds.keyframe(crv,q=1, tc=1)) for crv in cmds.ls(type='animCurve') ] ])
        result = [int(minTime), int(maxTime)]
        return result

    def saveSetData(self):
        objs = self.tree.getObjectsAttr()
        if not objs:
            return
        text, ok = QInputDialog.getText(self, 'Create export set', 'Enter name:', QLineEdit.Normal,'NewSet')
        if ok:
            setNode = cmds.sets(objs.keys(), n=text)
            for name, attrs in objs.items():
                self.addExportChannelsDataToObject(name, attrs)

            if not cmds.attributeQuery(outPathAttrName[0], node=setNode, exists=True ):
                cmds.addAttr(setNode, ln=outPathAttrName[0], sn=outPathAttrName[1],  dt='string')
            cmds.setAttr(setNode+'.'+outPathAttrName[0], self.outPath.path(), type="string" )

    def addExportChannelsDataToObject(self, name, attrs):
        if not cmds.attributeQuery( channelsAttrName[0], node=name, exists=True ):
            cmds.addAttr(name, ln=channelsAttrName[0], sn=channelsAttrName[1],  dt='string')
        cmds.setAttr(name+'.'+channelsAttrName[0], ';'.join(attrs), type="string" )

    def loadFromSet(self):
        menuData = []
        sets = cmds.ls(type='objectSet')
        if sets:
            menuData = [x for x in sets if cmds.attributeQuery(outPathAttrName[0], node=x, exists=True )]

        menu = QMenu(self)
        if menuData:
            for m in menuData:
                menu.addAction(QAction(m, self, triggered=lambda m=m: self.loadSetData(m)))
        else:
            act = QAction('No sets', self)
            act.setEnabled(0)
            menu.addAction(act)
        menu.exec_(QCursor.pos())
        # cmds.attributeQuery(outPathAttrName[0], node=setNode, exists=True )

    def loadSetData(self, setName):
        self.tree.clear()
        # sets = cmds.ls(sl=1, type='objectSet')

        data = []
        # if sets:
        content = cmds.sets( setName, q=True )
        for c in content:
            if cmds.attributeQuery( channelsAttrName[0], node=c, exists=True ):
                attrs = cmds.getAttr(c+'.'+channelsAttrName[0])
            else:
                attrs = []
            obj = ['.'.join([c,a]) for a in attrs.split(';')]
            data += obj
        self.tree.addObjects(data)
        if cmds.attributeQuery( outPathAttrName[0], node=setName, exists=True ):
            path = cmds.getAttr(setName+'.'+outPathAttrName[0])
            self.outPath.setPath(path)

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
        # startTime = time.time()
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

# if __name__ == '__main__':
#     app = QApplication([])
#     w = channelExporterWindowClass()
#     w.show()
#     app.exec_()
