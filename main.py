from PySide6.QtWidgets import QMainWindow, QApplication, QLabel, QHBoxLayout, QPushButton, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QMouseEvent 
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(390, 140, 1200, 750)
        self.setStyleSheet("""background-color: #383838;""")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # deletes default title bar

        self._drag_position = QPoint()
        self._dragging = False
        if self.windowHandle():
            self.windowHandle().windowStateChanged.connect(self._handleStateChange)

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
        
        self.main_layout.addWidget(self.title_bar_container)
        self.main_layout.addStretch()   # adds space for remaining content
        
        self.addToTitleBar()


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
        minimalize_button = QPushButton('—', self)
        minimalize_button.setStyleSheet("""QPushButton{ color: white;
                                        border: 0px;
                                        font-size: 12px;
                                   }
                                    QPushButton:hover {
                                        background-color: #3d3d3d;}
                                    """)

        close_button.setFixedSize(26, 26)
        minimalize_button.setFixedSize(26, 26)

        close_button.clicked.connect(self.close)
        minimalize_button.clicked.connect(self.showMinimized)

        self.title_bar.addWidget(title_label)
        self.title_bar.addStretch()    # pushes everything to the right
        
        self.title_bar.addWidget(minimalize_button)
        self.title_bar.addWidget(close_button)


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