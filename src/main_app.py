from PyQt5.QtWidgets import * #QApplication, QWidget, QDesktopWidget, QTableWidget
from PyQt5.QtGui import *

from general_info_widget import GeneralInfoWidget

class MainApp(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):

        stay_id = ""

        mainLayout = QGridLayout(self)

        ###############################################
        # 상단은 입실번호를 입력한다.
        topWidget = QWidget()  # Creating a widget for the top layout
        topWidget.setStyleSheet("border: 1px solid black;")  # Add a solid black border
        topWidget.setFixedHeight(40)  # Setting the fixed height
        topLayout = QHBoxLayout(topWidget)  # Using QVBoxLayout, but you can choose any layout

        # Adding a QLabel and QLineEdit for stay_id
        hadmIdLabel = QLabel("Hospital admission ID:")
        hadmIdLabel.setStyleSheet("border: 0px;")  
        self.hadmIdLineEdit = QLineEdit(stay_id)  # Initializing with stay_id
        self.hadmIdLineEdit.setStyleSheet("border: 0px;") 
        self.hadmIdLineEdit.setFixedHeight(20)  # Optionally, set a fixed height for the QLineEdit

        self.stayIdButton = QPushButton("Submit")  # Button next to line edit
        self.stayIdButton.clicked.connect(self.stayIdButtonClicked)  # Connect the button's clicked signal to the slot
        self.stayIdButton.setStyleSheet("border: 0px;background: white;") 

        # Add the label and line edit to the top layout
        topLayout.addWidget(hadmIdLabel)
        topLayout.addWidget(self.hadmIdLineEdit)
        topLayout.addWidget(self.stayIdButton)
        
        mainLayout.addWidget(topWidget, 0, 0)  # Adding the top widget to the main layout

        ###############################################
        # 하단은 정보를 보여준다.
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)  # Allow the contained widget to resize
        
        containerWidget = QWidget()
        bottomLayout = QVBoxLayout(containerWidget)
        self.generalInfoWidget = GeneralInfoWidget()
        bottomLayout.addWidget(self.generalInfoWidget)
        #bottomButton = QPushButton("A Button")
        #bottomLayout.addWidget(bottomButton)
        #bottomWidget = QWidget()
        #bottomWidget.setLayout(bottomLayout)

        scrollArea.setWidget(containerWidget)
        mainLayout.addWidget(scrollArea, 1, 0)

        ###############################################

        self.setWindowTitle('MIMIC viewer')
        self.resize(1440, 960)
        self.show()

    def stayIdButtonClicked(self):
        hadmId = self.hadmIdLineEdit.text()
        self.generalInfoWidget.initUI(hadmId)