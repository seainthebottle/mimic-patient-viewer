from PyQt5.QtWidgets import * #QApplication, QWidget, QDesktopWidget, QTableWidget
from PyQt5.QtGui import *

class MainApp(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        stay_id = ""

        mainLayout = QGridLayout(self)

        # 상단은 입실번호를 입력한다.
        topWidget = QWidget()  # Creating a widget for the top layout
        topWidget.setStyleSheet("border: 1px solid black;")  # Add a solid black border
        topWidget.setFixedHeight(40)  # Setting the fixed height
        topLayout = QHBoxLayout(topWidget)  # Using QVBoxLayout, but you can choose any layout

        # Adding a QLabel and QLineEdit for stay_id
        stayIdLabel = QLabel("Stay ID:")
        stayIdLabel.setStyleSheet("border: 0px;")  
        stayIdLineEdit = QLineEdit(stay_id)  # Initializing with stay_id
        stayIdLineEdit.setStyleSheet("border: 0px;") 
        stayIdLineEdit.setFixedHeight(20)  # Optionally, set a fixed height for the QLineEdit

        # Add the label and line edit to the top layout
        topLayout.addWidget(stayIdLabel)
        topLayout.addWidget(stayIdLineEdit)
        
        mainLayout.addWidget(topWidget, 0, 0)  # Adding the top widget to the main layout

        # 하단은 정보를 보여준다.
        bottomLayout = QVBoxLayout()
        bottomLabel = QLabel("This is the bottom layout")
        bottomButton = QPushButton("A Button")
        bottomLayout.addWidget(bottomLabel)
        bottomLayout.addWidget(bottomButton)
        bottomWidget = QWidget()
        bottomWidget.setLayout(bottomLayout)
        mainLayout.addWidget(bottomWidget, 1, 0)  # Adding the bottom layout to the main layout


        self.setWindowTitle('MIMIC viewer')
        self.resize(1440, 960)
        self.show()