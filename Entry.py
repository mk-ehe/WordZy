from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, Signal

import database

class EntryScreen(QWidget):
    login_successful = Signal(str)

    def __init__(self):
        super().__init__()

        self.window_layout = QVBoxLayout(self)
        self.window_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.main_container = QWidget()
        self.main_container.setFixedSize(700, 520)
        self.main_container.setStyleSheet("background-color: #282828; border-radius: 10px;")
    
        self.main_layout = QVBoxLayout(self.main_container)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.setSpacing(15)
        self.window_layout.addWidget(self.main_container)

        
        title = QLabel("Enter your credentials")
        title.setStyleSheet("color: white; font: bold 34px Arial;")
        title.setContentsMargins(0, 0, 0, 6)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(title)


        input_style = """
            QLineEdit {
                background-color: #555555;
                border: 2px solid #555555;
                border-radius: 5px;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 8px;
            }
            QLineEdit:focus { border: 2px solid white; }
        """


        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setFixedWidth(300)
        self.username_input.setStyleSheet(input_style)
        self.main_layout.addWidget(self.username_input, alignment=Qt.AlignmentFlag.AlignCenter)


        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedWidth(300)
        self.password_input.setStyleSheet(input_style)
        self.main_layout.addWidget(self.password_input, alignment=Qt.AlignmentFlag.AlignCenter)


        self.buttons_container = QWidget()
        self.horizontal_buttons = QHBoxLayout(self.buttons_container)
        self.horizontal_buttons.setContentsMargins(0, 4, 0, 0)

        self.register_btn = QPushButton("REGISTER")
        self.register_btn.setFixedWidth(130)
        self.register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: #00c90a;
                color: white;
                font: bold 17px Arial;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #00e900; }
            QPushButton:pressed { background-color: #00aa08; }
        """)
        self.register_btn.clicked.connect(self.registerUser)
        self.horizontal_buttons.addWidget(self.register_btn)
        

        self.login_btn = QPushButton("LOGIN")
        self.login_btn.setFixedWidth(130)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #007de3;
                color: white;
                font: bold 17px Arial;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #008cff; }
            QPushButton:pressed { background-color: #026dc4; }
        """)
        self.horizontal_buttons.addWidget(self.login_btn)
        self.login_btn.clicked.connect(self.loginUser)

        self.main_layout.addWidget(self.buttons_container)


        self.guest_btn = QPushButton("GUEST")
        self.guest_btn.setFixedWidth(150)
        self.guest_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.guest_btn.setStyleSheet("""
            QPushButton {
                background-color: #6b6b6b;
                color: white;
                font: bold 17px Arial;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #808080; }
            QPushButton:pressed { background-color: #454545; }
        """)
        self.guest_btn.setContentsMargins(0, 0, 0, 0)
        self.guest_btn.clicked.connect(self.continueAsGuest)
        self.main_layout.addWidget(self.guest_btn, alignment=Qt.AlignmentFlag.AlignCenter)


        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font: bold 18px Arial;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.error_label)


    def registerUser(self):
        user = self.username_input.text().strip()
        password = self.password_input.text().strip()
        

        if user and password:
            if len(user) > 30:
                self.error_label.setText("Username too long, MAX:30")
                return
            
            if len(password) < 5:
                self.error_label.setText("Password too short, MIN:6")
                return
        else:
            return

        if database.register(user, password):
            self.error_label.setText("")
            self.login_successful.emit(user) 
        else:
            self.error_label.setText("Username already exists!")


    def loginUser(self):
        user = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if database.login(user, password):
            self.error_label.setText("")
            self.login_successful.emit(user)
        else:
            self.error_label.setText("Wrong credentials.") 
    

    def continueAsGuest(self):
        self.login_successful.emit("Guest")