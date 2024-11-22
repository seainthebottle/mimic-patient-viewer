from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QTableWidget, QTableWidgetItem
from data_manage.data_model import DataModel

class GeneralInfoSheetWidget(QWidget):
    def __init__(self, dataModel):
        super().__init__()
        self.dataModel = dataModel
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.info = QTextEdit(self)
        self.info.setPlainText("Patient HADM Id not set")

        self.diagnosis_table = QTableWidget(self)
        self.diagnosis_table.setColumnCount(4)
        self.diagnosis_table.setHorizontalHeaderLabels(["Sequential number", "ICD Version", "ICD Code", "Diagnosis Description"])
        
        self.layout.addWidget(self.info)
        self.layout.addWidget(self.diagnosis_table)
        self.setLayout(self.layout)

    def clear(self):
        """초기 상태로 self.info와 self.diagnosis_table을 설정."""
        # Reset info text
        self.info.setPlainText("Patient HADM Id not set")
        # Clear diagnosis table
        self.diagnosis_table.clearContents()  # 테이블 내용을 삭제
        self.diagnosis_table.setRowCount(0)  # 테이블의 행 개수를 0으로 설정

    def display_info(self, hadm_id):
        #print(f"display_info: {hadm_id}")
        info_text = self.generate_info(hadm_id)
        self.info.setPlainText(info_text)
        self.update_diagnosis_table(hadm_id)

    def generate_info(self, hadm_id):
        info = self.dataModel.fetch_patient_info(hadm_id)
        #print(info)
        ret_str = "Hospital admission information not found."
        if info:
            ret_str = f"HADM id: {hadm_id}\n"
            ret_str += f"Gender: {info['gender']}\n"
            ret_str += f"Age at admission: {info['age_at_admission']}\n"
            ret_str += f"Admission time: {info['admittime'].strftime('%Y-%m-%d %H:%M:%S')}\n"
            ret_str += f"Discharge time: {info['dischtime'].strftime('%Y-%m-%d %H:%M:%S')}\n"
            if info['icu_intime']: ret_str += f"ICU intime: {info['icu_intime'].strftime('%Y-%m-%d %H:%M:%S')}\n"
            if info['icu_outtime']: ret_str += f"ICU outtime: {info['icu_outtime'].strftime('%Y-%m-%d %H:%M:%S')}\n"

            ret_str += "\n"
            diagnosis = self.dataModel.fetch_procedure_data(hadm_id)
            if diagnosis is not None and diagnosis.shape[0] > 0:
                for _, row_data in diagnosis.iterrows():
                    seq_num = str(row_data['sequential_number'])
                    icd_version = str(row_data['icd_version'])
                    icd_code = row_data['icd_code']
                    procedure_name = row_data['procedure_name']
                    procedure_date = row_data['procedure_date']
                    ret_str += f"{seq_num}\t{icd_version}\t{icd_code}\t{procedure_date}\t{procedure_name}\n"
            else: ret_str += "No procedures done."


        return ret_str
    
    def update_diagnosis_table(self, hadm_id):
        diagnosis_data = self.dataModel.fetch_diagnosis_data(hadm_id)
        #print(diagnosis_data)
        self.diagnosis_table.setRowCount(len(diagnosis_data))
        for row_index, row_data in diagnosis_data.iterrows():
            seq_num_item = QTableWidgetItem(str(row_data['sequential_number']))
            icd_version_item = QTableWidgetItem(str(row_data['icd_version']))
            icd_code_item = QTableWidgetItem(row_data['icd_code'])
            diagnosis_description_item = QTableWidgetItem(row_data['diagnosis_description'])
            self.diagnosis_table.setItem(row_index, 0, seq_num_item)
            self.diagnosis_table.setItem(row_index, 1, icd_version_item)
            self.diagnosis_table.setItem(row_index, 2, icd_code_item)
            self.diagnosis_table.setItem(row_index, 3, diagnosis_description_item)
        
        # 컬럼 사이즈를 조절한다.
        self.diagnosis_table.resizeColumnsToContents()