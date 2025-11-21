from PySide6.QtWidgets import QMainWindow, QApplication, QLabel, QHBoxLayout, QPushButton, QWidget, QVBoxLayout, QGridLayout
from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import QMouseEvent, QKeyEvent
import sys
import requests
from datetime import datetime
import random


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(390, 140, 1200, 750)
        self.setStyleSheet("""background-color: #383838;""")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # deletes default title bar

        self._drag_position = QPoint()
        self._dragging = False

        self.invalid_timer = QTimer()
        self.invalid_timer.setSingleShot(True)
        self.invalid_timer.timeout.connect(self.resetInvalidWord)

        self.invalid_word = False

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        

        self.title_bar_container = QWidget()
        self.title_bar_container.setFixedHeight(26)
        self.title_bar_container.setStyleSheet("""background-color: #282828;""")
        self.title_bar = QHBoxLayout(self.title_bar_container)
        self.title_bar.setContentsMargins(0, 0, 0, 0)
        self.title_bar.setSpacing(0)
        

        self.valid_words = self.loadValidWords()
        self.correct_word = self.getDailyWord()
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
                border: 2px solid #00d90b;
                color: #00d90b;
            }
            QLabel[state="wrong"] {
                border: 2px solid #1c1c1c;
                color: #1c1c1c;
            }
            QLabel[state="placement"] {
                border: 2px solid #f2d202;
                color: #f2d202;
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
        self.last_seven_text.setStyleSheet("")
        self.last_seven_text.setStyleSheet("""
            color: white;
            border: none;
            font: bold 18px Arial 
        """)
        self.last_seven_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.left_layout.addWidget(self.last_seven_text)

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


        self.right_container = QWidget()
        self.right_container.setFixedSize(175, 280)
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_widget = QLabel("Right panel")
        self.right_widget.setStyleSheet("color: white; font-size: 20px;")
        self.right_widget.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.right_widget.setContentsMargins(0, 0, 20, 0)
        self.right_layout.addWidget(self.right_widget)
        

        self.middle_layout.addStretch(1)
        self.middle_layout.addWidget(self.left_container)
        self.middle_layout.addStretch(1)
        self.middle_layout.addWidget(self.grid_container)
        self.middle_layout.addStretch(1)
        self.middle_layout.addWidget(self.right_container)
        self.middle_layout.addStretch(1)


        self.wordzy_container = QWidget()
        self.wordzy_layout = QVBoxLayout(self.wordzy_container)
        self.wordzy_layout.setContentsMargins(0, 10, 0, 0)

        self.wordzy_label = QLabel("WordZy", self.wordzy_container)
        self.wordzy_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.wordzy_label.setStyleSheet("""
            font-size: 46px;
            font-weight: bold;
            color: white;
        """)
        self.wordzy_layout.addWidget(self.wordzy_label)


        self.keyboard_rows = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
                               ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
                               ["Enter","Z", "X", "C", "V", "B", "N", "M", "⌫"]]
        self.keyboard_container = QWidget()
        self.keyboard_container.setContentsMargins(0, 48, 0, 0)
        self.keyboard_main_layout = QVBoxLayout(self.keyboard_container) 
        self.keyboard_main_layout.setSpacing(5)
        self.keyboard_main_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.createKeyboard()


        self.main_layout.addWidget(self.title_bar_container)
        self.main_layout.addWidget(self.wordzy_container)
        self.main_layout.addWidget(self.middle_container)
        self.main_layout.addWidget(self.keyboard_container)

        self.addToTitleBar()
        self.createGrid()

        self.main_layout.addStretch()


    def loadValidWords(self):
        try:
            response = requests.get("https://gist.githubusercontent.com/cfreshman/a03ef2cba789d8cf00c08f767e0fad7b/raw/wordle-answers-alphabetical.txt")
            words = response.text.strip().split('\n')
            return [w.lower().strip() for w in words if w.strip()]
        except:
            return ["error"]


    def getDailyWord(self, rewind = 0):
        today = datetime.now().date()
        seed = int(today.strftime("%Y%m%d"))
        random.seed(seed - rewind)
        daily_word = random.choice(self.valid_words)
        return daily_word
    
    
    def getLastWords(self):
        last_words = []
        for i in range(1, 8):
            last_words.append(self.getDailyWord(i))
        return last_words
        
        
    def isValidWord(self, word):
        return word.lower() in self.valid_words


    def addToTitleBar(self):
        title_label = QLabel("WordZy", self)
        title_label.setStyleSheet("""color: white;
                                  font-weight: bold;
                                  padding-left: 4px;
                                  padding-bottom: 2px""")
        
        close_button = QPushButton('✖', self)
        close_button.setStyleSheet("""QPushButton{ color: white;
                                        border: 0px;
                                        font-size: 14px;
                                        padding-bottom: 2px
                                   }
                                   QPushButton:hover {
                                        background-color: red;
                                        }
                                   """)
        minimize_button = QPushButton('—', self)
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
        self.title_bar.addStretch()    # pushes everything to the right
        
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


    def createKeyboard(self):
        for rows in self.keyboard_rows:
            self.row_container = QWidget()
            self.row_layout = QHBoxLayout(self.row_container)
            self.row_layout.setContentsMargins(0, 0, 0, 0)
            self.row_layout.setSpacing(5)
            self.row_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            for text in rows:
                self.button = QPushButton(text)
                font_size = "20px"
                padding_bottom = "4px"

                if text == "Enter" or text == "⌫":
                    self.button.setFixedSize(76, 50) 
                    if text == "⌫":
                        font_size = "30px"
                        padding_bottom = "6px"
                else:
                    self.button.setFixedSize(46, 50)

                self.button.setStyleSheet(f"""
                    background-color: #555555;
                    color: white;
                    border: 0px;
                    border-radius: 4px;
                    font: bold Arial;
                    font-size: {font_size} !important;
                    padding-bottom: {padding_bottom};
                    """)
                self.row_layout.addWidget(self.button)
            self.keyboard_main_layout.addWidget(self.row_container)

    
    def checkCorrectLetters(self):
        word_entered = ""
        start_idx = self.current_row * self.GRID_COLS
        end_idx = start_idx + self.GRID_COLS

        available_letters = list(self.correct_word)
        
        for i in range(start_idx, end_idx):
            idx = i - start_idx
            letter = self.grid_labels[i].text().lower()
            word_entered += letter
            
            if letter == self.correct_word[idx]:
                self.grid_labels[i].setProperty("state", "correct")
                available_letters[idx] = None

        
        for i in range(start_idx, end_idx):
            idx = i - start_idx
            
            if self.grid_labels[i].property("state") == "correct":
                continue
            
            letter = self.grid_labels[i].text().lower()
            
            if letter in available_letters:
                self.grid_labels[i].setProperty("state", "placement")
                available_letters[available_letters.index(letter)] = None
            else:
                self.grid_labels[i].setProperty("state", "wrong")
        
        for i in range(start_idx, end_idx):
            self.grid_labels[i].style().polish(self.grid_labels[i])
            
        if word_entered == self.correct_word:
            print("You guessed correctly!")
            self.game_finished = True
        elif self.grid_labels[-1].text() != "":
            print(f"Today's word was: {self.correct_word}")
            self.game_finished = True


    def showInvalidWord(self):
        start_idx = self.current_row * self.GRID_COLS
        end_idx = start_idx + self.GRID_COLS

        for i in range(start_idx, end_idx):
            self.grid_labels[i].setProperty("state", "invalid")
            self.grid_labels[i].style().polish(self.grid_labels[i])

        if not self.invalid_word:
            print("Invalid word!")
            self.invalid_word = True

        if self.invalid_timer.isActive():
            self.invalid_timer.stop()

        self.invalid_timer.start(1100)


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
                self.updateGridCell(letter)
                self.current_col += 1
                self.setActiveCell()

        elif key == Qt.Key.Key_Backspace:
            if self.current_col > 0:
                self.current_col -= 1
                self.updateGridCell("")
                self.setActiveCell()

        elif key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            if event.isAutoRepeat():
                self.showInvalidWord()
                return

            if self.current_col == 5 and self.current_row < 6:
                start_idx = self.current_row * self.GRID_COLS
                word_entered = ""
                for i in range(start_idx, start_idx + self.GRID_COLS):
                    word_entered += self.grid_labels[i].text().lower()

                if not self.isValidWord(word_entered):
                    self.showInvalidWord()
                    return
                
                self.checkCorrectLetters()
                self.current_row += 1
                self.current_col = 0

                if not self.game_finished:
                    self.setActiveCell()


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