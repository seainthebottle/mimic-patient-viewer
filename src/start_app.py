import sys
from PyQt5.QtWidgets import QApplication, QWidget

from main_app import MainApp

if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MainApp()
   sys.exit(app.exec_())