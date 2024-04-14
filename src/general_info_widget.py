from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit

from main_model import MainModel

class GeneralInfoWidget(QTextEdit):

    def __init__(self, parent = None):
        super().__init__(parent)

        self.mainModel = MainModel('mimiciv', 'postgres', 'Mokpswd7!')
        self.initUI()


    def initUI(self, hadm_id = None):
        # DB에서 성별, 나이, 입원일수 등의 정보를 가져온다.
        record = None
        if hadm_id != None:
            self.mainModel.connect()
            record = self.mainModel.fetch_admission(hadm_id)
            self.mainModel.close()

        if not record:
            self.setPlaceholderText("No hadm_id specified.")
        else:
            self.setText(f'Admittime: {record[2]}, Dischtime: {record[3]}')
