import random
from qtimport import *


class MSliderClass(QWidget):
    def __init__(self, text):
        super(MSliderClass, self).__init__()
        self.mayaName = 'scaleSliderExporter'+str(random.random()).replace('.','')
        self.ly = QHBoxLayout(self)
        self.ly.setContentsMargins(0,0,0,0)
        self.ly.setSpacing(0)
        self.slider = self.getMayaSlider(text)
        self.ly.addWidget(self.slider)

    def showEvent(self, *args, **kwargs):
        super(MSliderClass, self).showEvent(*args, **kwargs)
        self.val = [x for x in cmds.lsUI(controls=1, long=1) if self.mayaName in x][0]

    def getMayaSlider(self, text):
        window = cmds.window()
        cmds.columnLayout()
        sld = cmds.floatSliderGrp(self.mayaName,
                                  label=text,
                                  field=True,
                                  minValue=0.0,
                                  maxValue=2.0,
                                  fieldMinValue=0.0,
                                  fieldMaxValue=10000.0,
                                  value=0.01,
                                  precision=3,
                                  columnWidth3=[90,80,150]
                                  )
        qSlid = qControl(sld, QWidget)
        qSlid.setParent(self)
        return qSlid

    def value(self):
        return cmds.floatSliderGrp(self.val, q=1, v=1)

    def setValue(self, val):
        cmds.floatSliderGrp(self.val, e=1, v=val)
