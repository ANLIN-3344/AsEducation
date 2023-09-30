from __future__ import print_function
from ctypes import c_bool, sizeof, windll, pointer, c_int, Structure, POINTER
from ctypes.wintypes import DWORD, ULONG
from enum import Enum
from ANewPy.pyqtpro import pyqtpro
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QWidget
import os
import sys
import psutil
import ANewPy

__file__ = sys.argv[0]
os.chdir(os.path.split(__file__)[0])


def CheckIfItIsRunning():
    try:
        pidNotHandle = list(psutil.process_iter())
        get_pid = os.getpid()
        TheName = os.path.split(__file__)[-1]
        for each in pidNotHandle:
            pid = each.pid
            name = each.name()
            if name == TheName and pid != get_pid:
                return True
        return False
    except:
        return False


class DesktopWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AsEducationDesktop ConfigurationParameter Notice Editer")
        self.size = (850, 150)

        self.move(CP["ScreenSize"][0]//2-self.size[0]//2, CP["ScreenSize"][1]//2-self.size[1]//2)
        self.resize(self.size[0], self.size[1])   

        self.L_Logo = QLabel(self)
        self.L_Logo.move(10, 10)
        self.L_Logo.resize(50, 50)
        self.L_Logo.setScaledContents(True)
        self.L_Logo.setPixmap(QPixmap(CP['L_Logo']['path']))

        self.L_Title = QLabel(self)
        self.L_Title.move(70, 10)
        self.L_Title.setFont(QFont(CP["Font"], CP['L_Notice']['size']))
        self.L_Title.setText("AED ConfigurationParameter Notice Editer")

        self.LE_Notice = QLineEdit(self)
        self.LE_Notice.move(10, 70)
        self.LE_Notice.resize(self.size[0] - 20, CP['L_Notice']['size']*5)
        self.LE_Notice.setFont(QFont(CP["Font"], CP['L_Notice']['size']))
        self.LE_Notice.setText(CP['L_Notice']["text"])  

        self.show()

    def save(self):
        CP['L_Notice']["text"] = self.LE_Notice.text()
        text = "{\n"
        for i in CP:
            if isinstance(CP[i], str):
                text += f"\"{i}\": \"{CP[i]}\",\n"
            else:
                text += f"\"{i}\": {CP[i]},\n"
        text += "}"
        ANewPy.open_('ConfigurationParameter.ini').w(text)

    def closeEvent(self, _):
        self.hide()
        self.save()
        ANewPy.quit(1)

CP = ANewPy.open_('ConfigurationParameter.ini').r()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setQuitOnLastWindowClosed(False)
    if CheckIfItIsRunning():
        ANewPy.quit(1)
    else:
        _DesktopWindow = DesktopWindow()
    sys.exit(app.exec_())
