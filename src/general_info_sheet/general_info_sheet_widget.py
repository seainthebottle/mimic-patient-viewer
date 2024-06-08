from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit

class GeneralInfoSheetWidget(QWidget):
    def __init__(self, dataModel):
        super().__init__()
        self.dataModel = dataModel
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.info = QTextEdit(self)
        self.info.setPlainText("Patient HADM Id not set")
        self.layout.addWidget(self.info)
        self.setLayout(self.layout)

    def display_info(self, hadm_id):
        info_text = self.generate_info(hadm_id)
        self.info.setPlainText(info_text)

    def generate_info(self, hadm_id):
        info = self.dataModel.fetch_patient_info(hadm_id)
        print(info)
        ret_str = "Hospital admission information not found."
        if info:
            ret_str = f"Gender: {info['gender']}\n"
            ret_str += f"Age: {info['age_at_admission']}\n"
            ret_str += f"Admission time: {info['admittime'].strftime('%Y-%m-%d %H:%M:%S')}\n"
            ret_str += f"Discharge time: {info['dischtime'].strftime('%Y-%m-%d %H:%M:%S')}\n"
            if info['icu_intime']: ret_str += f"ICU intime: {info['icu_intime'].strftime('%Y-%m-%d %H:%M:%S')}\n"
            if info['icu_outtime']: ret_str += f"ICU outtime: {info['icu_outtime'].strftime('%Y-%m-%d %H:%M:%S')}\n"

        #TODO: 질병 코드도 정리해야 한다.
        return ret_str