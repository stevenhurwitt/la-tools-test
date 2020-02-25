from PyQt5.QtWidgets import QMenu, QAction, QWidget, QMainWindow, QDialog
from messageBox import Ui_msgDialog

# This class is called when creating a new msgBox either to warn/alert the user of something that went wrong
class msgBox(QDialog, Ui_msgDialog):
    def __init__(self,):
        super(msgBox, self).__init__()
        self.setupUi(self)
