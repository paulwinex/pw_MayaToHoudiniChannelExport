from ..mayaqtimport import *


class filePathWidgetClass(QWidget):
    def __init__(self, asLoad=False, ext=None, buttonText = '...', buttonWidth=30):
        super(filePathWidgetClass, self).__init__()
        self.__extList = ext
        self.__asLoad = asLoad
        self.__ly =QHBoxLayout(self)
        self.__ly.setContentsMargins(0,0,0,0)
        self.__ly.setSpacing(2)
        self.__path_le = QLineEdit()
        self.__browse_btn = QPushButton(buttonText)
        self.__browse_btn.setMaximumWidth(buttonWidth)

        self.__ly.addWidget(self.__path_le)
        self.__ly.addWidget(self.__browse_btn)

        #connect
        self.__browse_btn.clicked.connect(self.__browseFile)

    def path(self):
        return self.__path_le.text()

    def setPath(self, path):
        self.__path_le.setText(path)

    def __browseFile(self):
        filterList = ''
        if self.__extList:
            if isinstance(self.__extList, list):
                filterList = '(' + ' '.join(['*.%s' % x for x in self.__extList]) + ')'
            elif isinstance(self.__extList, dict):
                # filterList = "Images (*.png *.xpm *.jpg);;Text files (*.txt);;XML files (*.xml)"
                types = []
                for key,value in self.__extList.items():
                    s = key + ' (' +' '.join(['*.%s' % x for x in value]) +')'
                    types.append(s)
                filterList = ';;'.join(types)

        path = [0,0]
        if self.__asLoad:
            path = QFileDialog.getOpenFileName(self,'Open file'
                                               , '', filterList)
        else:
            path = QFileDialog.getSaveFileName(self,'Save file'
                                               , '', filterList)
        if path[0]:
            self.__path_le.setText(path[0])
