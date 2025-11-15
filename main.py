from PySide6.QtWidgets import QMainWindow, QApplication, QLabel, QHBoxLayout, QPushButton, QWidget, QVBoxLayout, QGridLayout
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QMouseEvent, QKeyEvent 
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(390, 140, 1200, 750)
        self.setStyleSheet("""background-color: #383838;""")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # deletes default title bar

        self._drag_position = QPoint()
        self._dragging = False

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
        
        
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.setContentsMargins(0, 80, 0, 0)
        self.current_row = 0
        self.current_col = 0
        self.grid_labels = []
        self.GRID_ROWS = 6
        self.GRID_COLS = 5
        self.WORD_LENGTH = 5


        self.main_layout.addWidget(self.title_bar_container)
        self.main_layout.addWidget(self.grid_container)

        
        self.addToTitleBar()
        self.createGrid()

        self.main_layout.addStretch()   # adds space for remaining content


    def addToTitleBar(self):
        title_label = QLabel("Wordle", self)
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
        default_style = """
            QLabel {
                border: 2px solid #555555;
                color: white;
                background-color: #383838;
                font: bold 28pt "Arial";
            }
            QLabel[state="filled"] {
                border: 2px solid white;
            }
            QLabel[state="active"] {
                border: 2px solid #949494;
            }
        """

        for row in range(self.GRID_ROWS):
            for col in range(self.GRID_COLS):
                label = QLabel() 
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setFixedSize(60, 60)
                label.setStyleSheet(default_style)
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
                if i == active_idx:
                    label.setProperty("state", "active" if label.text() == "" else "filled")
                else:
                    label.setProperty("state", "filled" if label.text() else "empty")
                
                label.style().polish(label)

    
    def keyPressEvent(self, event: QKeyEvent):
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
            if self.current_col == 5 and self.current_row < 6:
                self.current_row += 1
                self.current_col = 0
                self.setActiveCell()
    

    def mousePressEvent(self, event: QMouseEvent):        
        if event.button() == Qt.MouseButton.LeftButton:
            local_pos_int = event.position().toPoint() 
            global_click_pos = self.mapToGlobal(local_pos_int)
            d
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