import sys
from PyQt5.QtWidgets import QApplication, QWidget

import main_app

if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = main_app.MainApp()
   sys.exit(app.exec_())