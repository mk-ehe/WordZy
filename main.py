from PySide6.QtWidgets import QMainWindow, QApplication, QLabel, QHBoxLayout, QPushButton, QWidget, QVBoxLayout, QGridLayout, QStackedWidget
from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import QMouseEvent, QKeyEvent, QPixmap, QIcon

import requests
import ntplib
from time import ctime
from datetime import datetime, timedelta
import random
import sys
import os

import database
from Entry import EntryScreen


def resourcePath(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(390, 140, 1200, 750)
        self.setStyleSheet("""background-color: #383838;""")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowMinimizeButtonHint)

        self._drag_position = QPoint()
        self._dragging = False
        self.setWindowIcon(QIcon(resourcePath("logo.png")))

        self.invalid_timer = QTimer()
        self.invalid_timer.setSingleShot(True)
        self.invalid_timer.timeout.connect(self.resetInvalidWord)

        self.invalid_word = False

        self.username = ""
        self.int_word = 1

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.base_layout = QVBoxLayout(self.central_widget)
        self.base_layout.setContentsMargins(0, 0, 0, 0)
        self.base_layout.setSpacing(0)


        self.title_bar_container = QWidget()
        self.title_bar_container.setFixedHeight(26)
        self.title_bar_container.setStyleSheet("""background-color: #282828;""")
        self.title_bar = QHBoxLayout(self.title_bar_container)
        self.title_bar.setContentsMargins(0, 0, 0, 0)
        self.title_bar.setSpacing(0)
        self.base_layout.addWidget(self.title_bar_container)


        self.stack = QStackedWidget()
        self.base_layout.addWidget(self.stack)

        self.login_screen = EntryScreen()
        self.login_screen.login_successful.connect(self.showGame)
        self.stack.addWidget(self.login_screen)


        self.game_container = QWidget()
        self.game_layout = QVBoxLayout(self.game_container)
        self.game_layout.setContentsMargins(0, 0, 0, 0)
        self.game_layout.setSpacing(0)
        self.stack.addWidget(self.game_container)
        

        self.valid_words = self.loadValidWords()
        self.extra_words = self.loadExtraWords()
        self.game_finished = False
        

        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.setContentsMargins(0, 10, 0, 0)
        self.default_grid_style = """
            QLabel {
                border: 2px solid #555555;
                color: white;
                background-color: #474747;
                font: bold 32px Arial;
            }
            QLabel[state="filled"] {
                border: 2px solid white;
            }
            QLabel[state="active"] {
                border: 2px solid #949494;
            }
            QLabel[state="correct"] {
                border: 2px solid #00e900;
                color: #00c90a;
            }
            QLabel[state="wrong"] {
                border: 2px solid #1c1c1c;
                color: #1c1c1c;
            }
            QLabel[state="placement"] {
                border: 2px solid #ffdd00;
                color: #ffdd00;
            }
            QLabel[state="invalid"] {
                border: 2px solid red;
                color: red;
            }
        """
        self.current_row = 0
        self.current_col = 0
        self.grid_labels = []
        self.GRID_ROWS = 6
        self.GRID_COLS = 5


        self.middle_container = QWidget()
        self.middle_layout = QHBoxLayout(self.middle_container)
        self.middle_layout.setContentsMargins(0, 0, 0, 0)


        self.left_container = QWidget()
        self.left_container.setStyleSheet("""
            background-color: #282828;  
            border: 1px solid #555555;  
            border-radius: 10px;        
            padding-top: 1px;
            padding-bottom: 2px;
            margin-left: 15px;
        """)
        self.left_container.setFixedSize(175, 280)
        self.left_container.setContentsMargins(0, 0, 0, 0)
        self.left_layout = QVBoxLayout(self.left_container)
        self.left_layout.setSpacing(5)
        self.left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.last_words = self.getLastWords()
        self.last_seven_text = QLabel("Last 7 words")
        self.last_seven_text.setStyleSheet("""
            color: white;
            border: none;
            font: bold 18px Arial 
        """)
        self.last_seven_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.left_layout.addWidget(self.last_seven_text)
        self.addLastWords()


        self.right_container = QWidget()
        self.right_container.setFixedSize(175, 280)
        self.right_container.setContentsMargins(0, 0, 0, 0)
        self.right_container.setStyleSheet("""
            background-color: #282828;  
            border: 1px solid #555555;  
            border-radius: 10px;        
            padding-top: 1px;
            padding-bottom: 2px;
            margin-right: 15px;             
        """)


        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.updateTimer)
        self.seconds = 0
        self.minutes = 0


        self.middle_layout.addStretch(1)
        self.middle_layout.addWidget(self.left_container)
        self.middle_layout.addStretch(1)
        self.middle_layout.addWidget(self.grid_container)
        self.middle_layout.addStretch(1)
        self.middle_layout.addWidget(self.right_container)
        self.middle_layout.addStretch(1)

        self.wordzy_container = QWidget()
        self.wordzy_layout = QGridLayout(self.wordzy_container)
        self.wordzy_layout.setContentsMargins(0, 10, 0, 0)
        self.wordzy_label = QLabel("WordZy")
        self.wordzy_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.wordzy_label.setStyleSheet("""
            font-size: 46px;
            font-weight: bold;
            color: white;
        """)
        self.wordzy_layout.addWidget(self.wordzy_label, 0, 0, Qt.AlignmentFlag.AlignCenter)


        self.username_logo = QLabel()
        self.pixmap = QPixmap(resourcePath("logo.png"))
        self.username_logo.setPixmap(self.pixmap)
        self.username_logo.setStyleSheet("padding-top: 5px; padding-right: 16px")

        self.username_label = QLabel(self.username)
        self.username_label.setStyleSheet("color: white; font: bold 20px Arial; padding-right: 56px; padding-top: 12px;")
        self.wordzy_layout.addWidget(self.username_label, 0, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        self.username_logo.raise_()
        self.wordzy_layout.addWidget(self.username_logo, 0, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)


        self.keyboard_rows = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
                              ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
                              ["Enter","Z", "X", "C", "V", "B", "N", "M", "⌫"]]
        self.keyboard_letters = [letter for row in self.keyboard_rows for letter in row]
        self.keyboard_status = {letter: "default" for letter in self.keyboard_letters}
        self.keyboard_qbuttons = {}

        self.keyboard_container = QWidget()
        self.keyboard_container.setContentsMargins(0, 18, 0, 0)
        self.keyboard_main_layout = QVBoxLayout(self.keyboard_container) 
        self.keyboard_main_layout.setSpacing(5)
        self.keyboard_main_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        

        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("""
            font: bold 18px Arial;
            color: white;
            padding-top: 10px;
        """)


        self.game_layout.addWidget(self.wordzy_container)
        self.game_layout.addWidget(self.middle_container)
        self.game_layout.addWidget(self.info_label)
        self.game_layout.addWidget(self.keyboard_container)


        self.createKeyboard()
        self.addToTitleBar()
        self.createGrid()
        self.createRightLayout()

        self.game_layout.addStretch()


    def restoreGame(self, words):
        for row_idx, word in enumerate(words):
            self.current_row = row_idx
            self.current_col = 0
            
            start_idx = self.current_row * self.GRID_COLS
            for i, letter in enumerate(word):
                self.grid_labels[start_idx + i].setText(letter.upper())
                self.grid_labels[start_idx + i].setProperty("state", "filled")
            
            available_letters = list(self.correct_word)

            for i in range(5):
                idx = start_idx + i
                letter = word[i]
                if letter == self.correct_word[i]:
                    self.grid_labels[idx].setProperty("state", "correct")
                    available_letters[i] = None
                    self.keyboard_status[letter.upper()] = "correct"
            
            for i in range(5):
                idx = start_idx + i
                letter = word[i]
                if self.grid_labels[idx].property("state") == "correct":
                    continue
                if letter in available_letters:
                    self.grid_labels[idx].setProperty("state", "placement")
                    available_letters[available_letters.index(letter)] = None
                    if self.keyboard_status.get(letter.upper()) != "correct":
                        self.keyboard_status[letter.upper()] = "placement"
                else:
                    self.grid_labels[idx].setProperty("state", "wrong")
                    if self.keyboard_status.get(letter.upper()) not in ["correct", "placement"]:
                        self.keyboard_status[letter.upper()] = "wrong"

            for i in range(5):
                self.grid_labels[start_idx + i].style().polish(self.grid_labels[start_idx + i])
            
            if word == self.correct_word:
                self.changeInfoLabelDaily("#00ff00")
                self.game_finished = True
                self.game_timer.stop()


        saved_time = database.getTime(self.username)
        
        if saved_time:
            try:
                parts = saved_time.split(":")
                self.minutes = int(parts[0])
                self.seconds = int(parts[1])
            except:
                self.minutes = 0
                self.seconds = 0
                
            formatted_time = f"{self.minutes:02}:{self.seconds:02}"
            self.time.setText(formatted_time)
        else:
            self.time.setText("00:00")
            self.minutes = 0
            self.seconds = 0
            
        self.updateKeyboardColors()
        
        if not self.game_finished:
            self.current_row = len(words)
            self.int_word = len(words) + 1
            if self.current_row >= 6:
                self.changeInfoLabelDaily("white")
                self.game_finished = True
                self.game_timer.stop()
            else:
                self.setActiveCell()


    def updateTimer(self):
        if self.game_finished:
            self.game_timer.stop()
            return
        self.seconds += 1
        if self.seconds == 60:
            self.seconds = 0
            self.minutes += 1
        self.time.setText(f"{self.minutes:02}:{self.seconds:02}")


    def closeEvent(self, event):
        if self.username and self.username != "Guest" and not self.game_finished:
            current_time_str = self.time.text()
            database.sendTime(self.username, current_time_str)
        event.accept()


    def showGame(self, username):
        database.checkAndResetDaily(username)
        
        self.correct_word = self.getDailyWord()

        self.stack.setCurrentIndex(1)
        self.setFocus()
        self.username_label.setText(username)
        self.username = username
        

        time = database.getTime(self.username)
        if time:
            self.time.setText(time)
        else:
            self.time.setText("00:00")

        played_words = database.getPlayedWords(username)
        
        if played_words:
            self.restoreGame(played_words)
            if not self.game_finished:
                self.game_timer.start(1000)
        else:
            self.game_timer.start(1000)

        self.wins.setText("Won: "+str(database.getUserWins(self.username)))
        self.total_games.setText("Played: "+str(database.getTotalGamesPlayed(self.username)))
        self.streak.setText("Streak: "+str(database.getUserStreak(self.username)))
        if database.getTotalGamesPlayed(self.username) != 0:
            self.percentage.setText("Win: "+str(database.getUserWins(self.username) / database.getTotalGamesPlayed(self.username) * 100)+"%")


    def loadValidWords(self):
        try:
            response = requests.get("https://gist.githubusercontent.com/cfreshman/a03ef2cba789d8cf00c08f767e0fad7b/raw/wordle-answers-alphabetical.txt")
            words = response.text.strip().split("\n")
            return [w.lower().strip() for w in words if w.strip()]
        except:
            return ["error"]
        

    def loadExtraWords(self):
        try:
            response = requests.get(
                "https://raw.githubusercontent.com/tabatkins/wordle-list/main/words"
            )
            words = response.text.strip().split("\n")
            return [w.lower().strip() for w in words if len(w.strip()) == 5]
        except:
            return ["error"]


    def getDailyWord(self, rewind=0):
        today = datetime.now().date()      
        target_date = today - timedelta(days=rewind)
        seed = int(target_date.strftime("%Y%m%d"))
        random.seed(seed)
        daily_word = random.choice(self.valid_words)
        return daily_word
    
    
    def getLastWords(self):
        last_words = []
        for i in range(1, 8):
            last_words.append(self.getDailyWord(i))
        return last_words
        
    
    def isValidWord(self, word):
        return word.lower() in self.extra_words


    def addToTitleBar(self):
        title_label = QLabel("WordZy", self)
        title_label.setStyleSheet("""color: white;
                                     font-weight: bold;
                                     padding-left: 4px;
                                     padding-bottom: 2px""")
        
        close_button = QPushButton("✖", self)
        close_button.setFocusPolicy(Qt.NoFocus)
        close_button.setStyleSheet("""QPushButton{ color: white;
                                     border: 0px;
                                     font-size: 14px;
                                     padding-bottom: 2px
                                    }
                                    QPushButton:hover {
                                        background-color: red;
                                        }
                                    """)
        minimize_button = QPushButton("—", self)
        minimize_button.setFocusPolicy(Qt.NoFocus)
        minimize_button.setStyleSheet("""QPushButton{ color: white;
                                     border: 0px;
                                     font-size: 12px;
                                    }
                                    QPushButton:hover {
                                        background-color: #3d3d3d;}
                                    """)

        close_button.setFixedSize(26, 26)
        minimize_button.setFixedSize(26, 26)

        close_button.clicked.connect(self.close)
        minimize_button.clicked.connect(self.showMinimized)

        self.title_bar.addWidget(title_label)
        self.title_bar.addStretch()
        
        self.title_bar.addWidget(minimize_button)
        self.title_bar.addWidget(close_button)


    def createGrid(self):
        for row in range(self.GRID_ROWS):
            for col in range(self.GRID_COLS):
                label = QLabel() 
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setFixedSize(60, 60)
                label.setStyleSheet(self.default_grid_style)
                label.setProperty("state", "empty")

                self.grid_labels.append(label)
                self.grid_layout.addWidget(label, row, col)

        self.setActiveCell()


    def updateGridCell(self, letter):
        if 0 <= self.current_row < 6 and 0 <= self.current_col < 5:
            label_index = self.current_row * 5 + self.current_col
            label = self.grid_labels[label_index]
            label.setText(letter)
            
            label.setProperty("state", "filled" if letter else "empty")
            label.style().polish(label)


    def setActiveCell(self):
        if 0 <= self.current_row < 6 and 0 <= self.current_col < 5:
            active_idx = self.current_row * 5 + self.current_col

            for i, label in enumerate(self.grid_labels):
                current_state = label.property("state")
                if current_state in ["correct", "wrong", "placement"]:
                    continue
                    
                if i == active_idx:
                    label.setProperty("state", "active" if label.text() == "" else "filled")
                else:
                    label.setProperty("state", "filled" if label.text() else "empty")
                
                label.style().polish(label)


    def addLastWords(self):
        for i, word in enumerate(self.last_words):
            self.left_widget = QLabel(word.upper())
            if i != 0:
                self.left_widget.setStyleSheet("color: white; font: bold 22px Arial; background-color: #808080;")
            else:
                self.left_widget.setStyleSheet("color: white; font: bold 22px Arial; background-color: #00aaed;")
            self.left_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.left_widget.setContentsMargins(0, 2, 0, 0)
            self.left_widget.setFixedWidth(150)
            self.left_layout.addWidget(self.left_widget)


    def createRightLayout(self):
        self.right_widget = QLabel("Your Stats")
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_layout.setSpacing(6)
        self.right_widget.setStyleSheet("color: white; font: bold 18px Arial; border: 0px")
        self.right_widget.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.right_widget.setContentsMargins(0, 0, 0, 0)
        self.right_layout.addWidget(self.right_widget)


        self.wins = QLabel(f"Won: {database.getUserWins(self.username)}")
        self.wins.setStyleSheet("""color: white;
                                background-color: qlineargradient(
                                x1:0, y1:0, x2:0, y2:1,
                                stop:0 #00ff00,
                                stop:1 #006100); 
                                font: bold 18px Arial;
                                border: 2px solid #00ff00""")
        self.wins.setFixedSize(157, 42)
        self.wins.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.right_layout.addWidget(self.wins)


        self.total_games = QLabel(f"Played: {database.getTotalGamesPlayed(self.username)}")
        self.total_games.setStyleSheet("""color: white;
                                    background-color: qlineargradient(
                                    x1:0, y1:0, x2:0, y2:1,
                                    stop:0 #d4d4d4,
                                    stop:1 #3d3d3d); 
                                    font: bold 18px Arial;
                                    border: 2px solid #d4d4d4""")
        self.total_games.setFixedSize(157, 42)
        self.total_games.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.right_layout.addWidget(self.total_games)
        

        self.streak = QLabel(f"Streak: {database.getUserStreak(self.username)}")
        self.streak.setStyleSheet("""color: white;
                                background-color: qlineargradient(
                                x1:0, y1:0, x2:0, y2:1,
                                stop:0 #ffbf00,
                                stop:1 red); 
                                font: bold 18px Arial;
                                border: 2px solid #ffbf00""")
        self.streak.setFixedSize(157, 42)
        self.streak.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.right_layout.addWidget(self.streak)


        percentage = round(database.getUserWins(self.username) / database.getTotalGamesPlayed(self.username) * 100, 2) \
            if database.getTotalGamesPlayed(self.username) != 0 else "0.00"
        self.percentage = QLabel(f"Win: {percentage}")
        self.percentage.setStyleSheet("""color: white;
                                background-color: qlineargradient(
                                x1:0, y1:0, x2:0, y2:1,
                                stop:0 #00b7ff,
                                stop:1 #001cbd); 
                                font: bold 18px Arial;
                                border: 2px solid #00b7ff""")
        self.percentage.setFixedSize(157, 42)
        self.percentage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.right_layout.addWidget(self.percentage)


        self.time = QLabel()
        self.time.setStyleSheet("""color: white;
                            background-color: qlineargradient(
                            x1:0, y1:0, x2:0, y2:1,
                            stop:0 #ff0080,
                            stop:1 #800000); 
                            font: bold 18px Arial;
                            border: 2px solid #ff0080""")
        self.time.setFixedSize(157, 42)
        self.time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.right_layout.addWidget(self.time)

        self.right_layout.addStretch()


    def createKeyboard(self):
        for rows in self.keyboard_rows:
            self.row_container = QWidget()
            self.row_layout = QHBoxLayout(self.row_container)
            self.row_layout.setContentsMargins(0, 0, 0, 0)
            self.row_layout.setSpacing(5)
            self.row_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            for text in rows:
                button = QPushButton(text)
                button.setFocusPolicy(Qt.NoFocus)
                button.clicked.connect(lambda _, t=text: self.handleButtonClick(t))
                font_size = "20px"
                padding_bottom = "4px"

                if text == "Enter" or text == "⌫":
                    button.setFixedSize(76, 50) 
                    if text == "⌫":
                        font_size = "30px"
                        padding_bottom = "6px"
                else:
                    button.setFixedSize(46, 50)
                self.keyboard_qbuttons[text] = button

                button.setStyleSheet(f"""
                    QPushButton{{
                        background-color: #555555;
                        color: white;
                        border: 0px;
                        border-radius: 4px;
                        font: bold Arial;
                        font-size: {font_size} !important;
                        padding-bottom: {padding_bottom};
                    }}
                    QPushButton:hover {{            
                        background-color: #5c5c5c;
                    }}                                  
                    QPushButton:pressed {{
                        background-color: #6a6a6a;
                    }}
                    """)
                self.row_layout.addWidget(button)
            self.keyboard_main_layout.addWidget(self.row_container)


    def updateKeyboardColors(self, flash_letter=None):
        color_map = {
            "correct": "#00c90a",
            "placement": "#d6ba00",
            "wrong": "#1c1c1c",  
            "default": "#555555"
        }

        hover_map = {
            "correct": "#00e900",
            "placement": "#eece00",
            "wrong": "#252525",  
            "default": "#5c5c5c"
        }

        pressed_map = {
            "correct": "#00aa08",
            "placement": "#c5ab00",
            "wrong": "#2C2C2C",  
            "default": "#6a6a6a"
        }

        for letter, status in self.keyboard_status.items():
            button = self.keyboard_qbuttons.get(letter)
            if button:
                color = pressed_map[status] if letter == flash_letter else color_map[status]
                hover_color = hover_map[status]
                pressed_color = pressed_map[status]
                
                font_size = "20px"
                padding_bottom = "4px"
                if letter == "⌫":
                    font_size = "30px"
                    padding_bottom = "6px"

                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {color};
                        color: white;
                        border: 0px;
                        border-radius: 4px;
                        font: bold Arial;
                        font-size: {font_size} !important;
                        padding-bottom: {padding_bottom};
                    }}
                    QPushButton:hover {{            
                        background-color: {hover_color};
                    }}                                  
                    QPushButton:pressed {{
                        background-color: {pressed_color};
                    }}
                    """)
                

    def handleButtonClick(self, text):
        if self.game_finished:
            return
        
        if text.isalpha() and len(text) == 1:
            if self.current_col < 5:
                self.updateKeyboardColors(flash_letter=text)
                QTimer.singleShot(100, lambda: self.updateKeyboardColors())
                self.updateGridCell(text)
                self.current_col += 1
                self.setActiveCell()
        
        elif text == "⌫":
            if self.current_col > 0:
                self.updateKeyboardColors(flash_letter="⌫")
                QTimer.singleShot(100, lambda: self.updateKeyboardColors())
                self.current_col -= 1
                self.updateGridCell("")
                self.setActiveCell()
        
        elif text == "Enter":
            if self.current_col == 5 and self.current_row < 6:
                start_idx = self.current_row * self.GRID_COLS
                word_entered = ""
                for i in range(start_idx, start_idx + self.GRID_COLS):
                    word_entered += self.grid_labels[i].text().lower()

                if not self.isValidWord(word_entered):
                    self.changeInfoLabelInvalid()
                    self.updateKeyboardColors(flash_letter="Enter")
                    QTimer.singleShot(100, lambda: self.updateKeyboardColors())
                    self.showInvalidWord()
                    return

                self.checkCorrectLetters()
                self.current_row += 1
                self.current_col = 0

                if not self.game_finished:
                    self.setActiveCell()

                self.updateKeyboardColors(flash_letter="Enter")
                QTimer.singleShot(100, lambda: self.updateKeyboardColors())

    
    def checkCorrectLetters(self):
        word_entered = ""
        start_idx = self.current_row * self.GRID_COLS
        end_idx = start_idx + self.GRID_COLS

        available_letters = list(self.correct_word)
        current_row_letters = []
        
        for i in range(start_idx, end_idx):
            idx = i - start_idx
            letter = self.grid_labels[i].text().lower()
            word_entered += letter
            current_row_letters.append(letter)
            
            if letter == self.correct_word[idx]:
                self.grid_labels[i].setProperty("state", "correct")
                available_letters[idx] = None
                self.keyboard_status[letter.upper()] = "correct"

        
        for i in range(start_idx, end_idx):
            idx = i - start_idx
            letter = self.grid_labels[i].text().lower()
            key_letter_upper = letter.upper()

            if self.grid_labels[i].property("state") == "correct":
                continue
            
            if letter in available_letters:
                self.grid_labels[i].setProperty("state", "placement")
                available_letters[available_letters.index(letter)] = None
                if self.keyboard_status.get(key_letter_upper) != "correct":
                    self.keyboard_status[key_letter_upper] = "placement"
            else:
                self.grid_labels[i].setProperty("state", "wrong")
                if self.keyboard_status.get(key_letter_upper) not in ["correct", "placement"]:
                    self.keyboard_status[key_letter_upper] = "wrong"

        self.updateKeyboardColors()

        for i in range(start_idx, end_idx):
            self.grid_labels[i].style().polish(self.grid_labels[i])
            

        is_win = (word_entered == self.correct_word)
        is_loss = (self.grid_labels[-1].text() != "" and not is_win)

        if is_win:
            self.changeInfoLabelDaily("#00ff00")
            self.game_finished = True

            if self.username != "Guest":
                self.runInBackground(database.finalizeGame, self.username, True, self.time.text())
                self.updateStatsDisplay(win=True)

        elif is_loss:
            self.changeInfoLabelDaily("white")
            self.game_finished = True

            if self.username != "Guest":
                self.runInBackground(database.finalizeGame, self.username, False, self.time.text())
                self.updateStatsDisplay(win=False)

        if self.username != "Guest":
            self.runInBackground(database.sendWord, self.username, self.int_word, word_entered)
            self.int_word += 1


    def runInBackground(self, func, *args):
        import threading
        thread = threading.Thread(target=func, args=args)
        thread.daemon = True
        thread.start()


    def updateStatsDisplay(self, win):
        try:
            curr_wins = int(self.wins.text().split(": ")[1])
            curr_played = int(self.total_games.text().split(": ")[1])
            curr_streak = int(self.streak.text().split(": ")[1])
        except:
            return

        new_played = curr_played + 1
        new_wins = curr_wins + 1 if win else curr_wins
        new_streak = curr_streak + 1 if win else 0

        self.wins.setText(f"Won: {new_wins}")
        self.total_games.setText(f"Played: {new_played}")
        self.streak.setText(f"Streak: {new_streak}")

        if new_played > 0:
            pct = round((new_wins / new_played) * 100, 2)
            self.percentage.setText(f"Win: {pct}%")
            

    def changeInfoLabelInvalid(self):
        self.info_label.setStyleSheet("font: bold 18px Arial; color: red; padding-top: 10px")
        self.info_label.setText("Invalid word.")
        QTimer.singleShot(1000, lambda: self.info_label.setText(""))


    def changeInfoLabelDaily(self, color):
        self.info_label.setStyleSheet(f"font: bold 18px Arial; color: {color}; padding-top: 10px")
        self.info_label.setText(f"Today's word was: {self.correct_word.upper()}")


    def showInvalidWord(self):
        start_idx = self.current_row * self.GRID_COLS
        end_idx = start_idx + self.GRID_COLS

        for i in range(start_idx, end_idx):
            self.grid_labels[i].setProperty("state", "invalid")
            self.grid_labels[i].style().polish(self.grid_labels[i])

        if not self.invalid_word:
            self.invalid_word = True

        if self.invalid_timer.isActive():
            self.invalid_timer.stop()

        self.invalid_timer.start(1000)


    def resetInvalidWord(self):
        start_idx = self.current_row * self.GRID_COLS
        end_idx = start_idx + self.GRID_COLS

        for i in range(start_idx, end_idx):
            if self.grid_labels[i].property("state") == "invalid":
                self.grid_labels[i].setProperty("state", "filled")
                self.grid_labels[i].style().polish(self.grid_labels[i])

        self.invalid_word = False

    
    def keyPressEvent(self, event: QKeyEvent):
        if self.game_finished:
            return
        
        key = event.key()
        
        if Qt.Key.Key_A <= key <= Qt.Key.Key_Z:
            if self.current_col < 5:
                letter = chr(key) 
                self.updateKeyboardColors(flash_letter=letter)
                QTimer.singleShot(100, lambda: self.updateKeyboardColors())
                self.updateGridCell(letter)
                self.current_col += 1
                self.setActiveCell()

        elif key == Qt.Key.Key_Backspace:
            if self.current_col > 0:
                self.updateKeyboardColors(flash_letter="⌫")
                QTimer.singleShot(100, lambda: self.updateKeyboardColors())
                self.current_col -= 1
                self.updateGridCell("")
                self.setActiveCell()

        elif key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            if self.current_col == 5 and self.current_row < 6:

                if event.isAutoRepeat():
                    self.showInvalidWord()
                    return
                
                start_idx = self.current_row * self.GRID_COLS
                word_entered = ""
                for i in range(start_idx, start_idx + self.GRID_COLS):
                    word_entered += self.grid_labels[i].text().lower()

                if not self.isValidWord(word_entered):
                    self.changeInfoLabelInvalid()
                    self.updateKeyboardColors(flash_letter="Enter")
                    QTimer.singleShot(100, lambda: self.updateKeyboardColors())
                    self.showInvalidWord()
                    return

                self.checkCorrectLetters()
                self.current_row += 1
                self.current_col = 0

                if not self.game_finished:
                    self.setActiveCell()

                self.updateKeyboardColors(flash_letter="Enter")
                QTimer.singleShot(100, lambda: self.updateKeyboardColors())
            else:
                return


    def mousePressEvent(self, event: QMouseEvent):         
        if event.button() == Qt.MouseButton.LeftButton:
            local_pos_int = event.position().toPoint() 
            global_click_pos = self.mapToGlobal(local_pos_int)
            if self.title_bar_container.geometry().contains(self.title_bar_container.mapFromGlobal(global_click_pos)):
                self._dragging = True
                self._drag_position = event.globalPosition().toPoint() - self.pos()
                event.accept()


    def mouseMoveEvent(self, event: QMouseEvent):
        if self._dragging:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()


    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()