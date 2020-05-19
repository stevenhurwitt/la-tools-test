import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit
from PyQt5.QtGui import QIcon
import EPOwebscrape


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'NEPOOL IDR Drop Download'
        self.left = 10
        self.top = 10
        self.width = 1280
        self.height = 960
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        user = self.getUser()
        password = self.getPassword()
        accts = self.getAcct()

        print('logging onto user {} with password {} for accts: {}'.format(user, password, accts))
        EPOwebscrape.idr_download(user, password, accts)
        
        self.show()
        
    def getUser(self):
        user, okPressed = QInputDialog.getText(self, "Get username","User:", QLineEdit.Normal, "")
        return(user)

    def getPassword(self):
        password, okPressed = QInputDialog.getText(self, "Get password","Password:", QLineEdit.Normal, "")
        return(password)

    def getAcct(self):
        accts, okPressed = QInputDialog.getText(self, "Get list of accts","Accounts:", QLineEdit.Normal, "")
        if okPressed and accts != '':
            accts = accts.split(',')
            return(accts)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    #print(app.user, app.password, app.accts)
    ex = App()
    sys.exit(app.exec_())