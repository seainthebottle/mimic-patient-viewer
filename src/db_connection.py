import json
from PyQt5.QtWidgets import QDialog, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QFormLayout
from data_manage.data_model import DataModel

class DBConnection(QDialog):
    def __init__(self, parent, dataModel):
        super().__init__(parent)
        self.setWindowTitle("Database Connection")
        self.connection_file = "connection.json"
        self.db_config = None
        self.default_values = self.load_defaults()
        self.data_model = dataModel
        self.init_ui()

    def load_defaults(self):
        """
        Load default values from the connection.json file.
        If the file does not exist, return the initial defaults.
        """
        try:
            with open(self.connection_file, "r") as file:
                self.db_config = json.load(file)
                return self.db_config
        except (FileNotFoundError, json.JSONDecodeError):
            # Return default values if file is missing or malformed
            self.db_config =  {
                "dbname": "mimiciv",
                "host": "localhost",
                "port": "5432",
                "user ID": "",
                "password": "",
            }
            return self.db_config

    def save_defaults(self, db_config):
        """
        Save the current values to the connection.json file.
        """
        with open(self.connection_file, "w") as file:
            json.dump(db_config, file, indent=4)

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Form layout for labels and input fields
        form_layout = QFormLayout()

        # Database Name
        self.db_name_input = QLineEdit(self)
        self.db_name_input.setText(self.default_values.get("dbname", ""))
        form_layout.addRow("Database Name:", self.db_name_input)

        # User ID
        self.user_id_input = QLineEdit(self)
        self.user_id_input.setText(self.default_values.get("user", ""))
        form_layout.addRow("User ID:", self.user_id_input)

        # Password
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setText(self.default_values.get("password", ""))
        form_layout.addRow("Password:", self.password_input)

        # Host
        self.host_input = QLineEdit(self)
        self.host_input.setText(self.default_values.get("host", ""))
        form_layout.addRow("Host:", self.host_input)

        # Port
        self.port_input = QLineEdit(self)
        self.port_input.setText(self.default_values.get("port", ""))
        form_layout.addRow("Port:", self.port_input)

        # Add the form layout to the main layout
        layout.addLayout(form_layout)

        # Buttons (side by side)
        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button = QPushButton("Connect", self)
        self.ok_button.clicked.connect(self.try_connection)

        # Add buttons to the layout
        button_layout.addStretch(1)  # Add a stretchable space to push buttons to the right
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)

        # Add the button layout to the main layout
        layout.addLayout(button_layout)

    def try_connection(self):
        db_name = self.db_name_input.text().strip()
        user_id = self.user_id_input.text().strip()
        password = self.password_input.text().strip()
        host = self.host_input.text().strip()
        port = self.port_input.text().strip()

        if not (db_name and user_id and password and host and port):
            QMessageBox.warning(self, "Error", "All fields must be filled out!")
            return

        # Attempt to connect to the database
        try:
            self.db_config = {
                "dbname": self.db_name_input.text().strip(),
                "host": self.host_input.text().strip(),
                "port": self.port_input.text().strip(),
                "user": self.user_id_input.text().strip(),
                "password": self.password_input.text().strip(),
            }
            self.data_model.connect_db(self.db_config)
            connection_success = True  # Replace with real connection check
            if connection_success:
                QMessageBox.information(self, "Success", "Connected to the database successfully!")
                self.save_defaults(self.db_config)  # Save the entered values to connection.json
                self.accept()
            else:
                raise Exception("Connection failed")  # Replace with actual error
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Failed to connect to the database:\n{str(e)}")
