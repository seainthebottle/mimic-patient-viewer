from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit

class DischargeNoteSheetWidget(QWidget):
    def __init__(self, dataModel):
        super().__init__()
        self.dataModel = dataModel
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.note = QTextEdit(self)
        self.note.setPlainText("Patient HADM Id not set")
        
        self.layout.addWidget(self.note)
        self.setLayout(self.layout)

    def display_note(self, hadm_id):
        #print(f"display_note: {hadm_id}")
        note_text = self.generate_note(hadm_id)
        self.note.setPlainText(note_text)

    def generate_note(self, hadm_id):
        note = self.dataModel.fetch_discharge_notes(hadm_id)
        #print(note)
        if note is not None and not note.empty:
            ret_str = ""
            for _, page in note.iterrows():
                ret_str += f"{page['text']}\n"
        else: ret_str = "Note not found."

        return ret_str
