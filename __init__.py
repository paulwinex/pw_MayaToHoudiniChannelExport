'''menuData
act={name:Export Channels to Houdini,action:show()}
'''
'''moduleInfo
Export channels to Houdini *.clip file
'''

from qtimport import *

from . import channelExportWindow
reload(channelExportWindow)

def getMayaWindow():
    ptr = omui.MQtUtil.mainWindow()
    if ptr is not None:
        return wrp(long(ptr), QMainWindow)

wind = channelExportWindow.channelExporterWindowClass(getMayaWindow())
def show():
    wind.show()
