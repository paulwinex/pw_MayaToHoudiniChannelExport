'''
Maya to Houdini Channel exporter
author: paulWinex
sile: paulwinex.ru

This script save maya animation channels to houdini .clip file.
You can load .clip file via fileCHOP.

Usage
import pw_MayaToHoudiniChannelExport
pw_MayaToHoudiniChannelExport.show()
'''
from __future__ import absolute_import
from pymel.core import ui

def show():
    from maya_to_houdini_channel_exporter import channelExportWindow
    reload(channelExportWindow)
    wind = channelExportWindow.channelExporterWindowClass(ui.PyUI('MayaWindow').asQtObject())
    wind.show()
