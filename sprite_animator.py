from PyQt5 import QtCore, QtGui, QtWidgets
from ui import Ui_MainWindow
import sys

class Animator_GUI(Ui_MainWindow):
    def __init__(self, MainWindow) -> None:
        super().__init__()
        super().setupUi(MainWindow)

        #link bg_color_btn to change_background_color method
        self.bg_color_btn.clicked.connect(self.change_background_color)

    def change_background_color(self):
        """
        Changes the background color of the window
        """
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            MainWindow.setStyleSheet(f"background-color: {color.name()}")

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    MainWindow = QtWidgets.QMainWindow()
    ui = Animator_GUI(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())