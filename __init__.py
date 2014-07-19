'''menuData
act={name:Export Channels to Houdini,action:show()}
'''
'''moduleInfo
Export channels to Houdini *.clip file
'''
'''
Maya to Houdini Channel exporter
author: paulWinex
sile: paulwinex.ru

This script save maya animation channels to houdini .clip file.
You can load .clip file via fileCHOP.
'''
from mayaqtimport import *

from . import channelExportWindow
# reload(channelExportWindow)

def getMayaWindow():
    ptr = omui.MQtUtil.mainWindow()
    if ptr is not None:
        return wrp(long(ptr), QMainWindow)

wind = channelExportWindow.channelExporterWindowClass(getMayaWindow())
def show():
    wind.show()
