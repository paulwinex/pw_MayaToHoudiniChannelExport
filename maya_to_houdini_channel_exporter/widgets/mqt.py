from PySide2.QtWidgets import *
from PySide2.QtCore import *
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance as wrp

def qControl(mayaName, qobj=None):
    if not qobj:
        qobj = QObject
    ptr = omui.MQtUtil.findControl(mayaName)
    if ptr is None:
        ptr = omui.MQtUtil.findLayout(mayaName)
    if ptr is None:
        ptr = omui.MQtUtil.findMenuItem(mayaName)
    return wrp(long(ptr), qobj)