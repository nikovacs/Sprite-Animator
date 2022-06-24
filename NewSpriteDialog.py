from PyQt5 import QtWidgets, QtCore, QtGui, QtWidgets
from new_sprite_ui import Ui_Dialog as NewSpriteUI

class NewSpriteDialog(NewSpriteUI):
    def __init__(self, parent=None):
        self.setupUi(parent)
        self.parent = parent
        parent.setWindowTitle("Add New Sprite")

        self.image_file = ""
        self.desc = ""
        self.index = None
        self.x = None
        self.y = None
        self.w = None
        self.h = None


        self.preview.setStyleSheet("background-color: white;")
        self.slicer.setStyleSheet("background-color: white;")

        self.image_combobox.currentIndexChanged.connect(self.update_preview)
        self.desc_textbox.textChanged.connect(self.update_desc)
        self.sprite_index_textbox.setValidator(QtGui.QIntValidator(-2000000000, 2000000000))
        self.sprite_index_textbox.textChanged.connect(self.update_index)
        self.x_textbox.setValidator(QtGui.QIntValidator(0, 9999))
        self.x_textbox.focusOutEvent = self.update_x
        self.y_textbox.setValidator(QtGui.QIntValidator(0, 9999))
        self.y_textbox.focusOutEvent = self.update_y
        self.width_textbox.setValidator(QtGui.QIntValidator(0, 9999))
        self.width_textbox.focusOutEvent = self.update_w
        self.height_textbox.setValidator(QtGui.QIntValidator(0, 9999))
        self.height_textbox.focusOutEvent = self.update_h

    def update_preview(self):
        self.image_file = self.parent.find_file(self.image_combobox.currentText().strip())

    def update_desc(self):
        self.desc = self.desc_textbox.text()

    def update_index(self):
        self.index = int(self.sprite_index_textbox.text())

    def update_x(self, e):
        print(self.x_textbox.text())
        text = self.x_textbox.text()
        self.x = int(text) if text else self.x

    def update_y(self, e):
        print(self.y_textbox.text())
        text = self.y_textbox.text()
        self.y = int(text) if text else self.y

    def update_w(self, e):
        print(self.width_textbox.text())
        text = self.width_textbox.text()
        self.w = int(text) if text else self.w

    def update_h(self, e):
        print(self.height_textbox.text())
        text = self.height_textbox.text()
        self.h = int(text) if text else self.h


# TODO, make custom lineEdit class with focusOutEvent
