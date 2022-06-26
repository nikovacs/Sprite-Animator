import math
import sys
from PyQt5 import QtWidgets, QtCore, QtGui, QtWidgets
from pygame import Rect
from new_sprite_ui import Ui_Dialog as NewSpriteUI
import numpy as np

class NewSpriteDialog(NewSpriteUI):
    def __init__(self, animator, parent=None):
        self.setupUi(parent)
        self.animator = animator
        parent.setWindowTitle("Add New Sprite")
        sys.setrecursionlimit(10000)
        self.__set_stylesheets()
        self.__init_vars()

        self.__init_slicer()
        self.__init_preview()

        self.image_combobox.currentIndexChanged.connect(self.update)

        self.desc_textbox.textChanged.connect(self.update_desc)

        self.sprite_index_textbox.setValidator(QtGui.QIntValidator(-2000000000, 2000000000))
        self.sprite_index_textbox.textChanged.connect(self.update_index)

        self.x_textbox.setValidator(QtGui.QIntValidator(0, 9999))
        self.x_textbox.textChanged.connect(self.update_x)
        self.y_textbox.setValidator(QtGui.QIntValidator(0, 9999))
        self.y_textbox.textChanged.connect(self.update_y)

        self.width_textbox.setValidator(QtGui.QIntValidator(0, 9999))
        self.width_textbox.textChanged.connect(self.update_w)

        self.height_textbox.setValidator(QtGui.QIntValidator(0, 9999))
        self.height_textbox.textChanged.connect(self.update_h)

        self.slicer.scene().mousePressEvent = self.__slicer_mouse_press_event

        self.update()

    def __slicer_mouse_press_event(self, e) -> None:
        viewPoint = self.slicer.mapFromGlobal(QtGui.QCursor.pos())
        scenePoint = self.slicer.mapToScene(viewPoint)
        self.__generate_x_y_w_h((math.floor(scenePoint.x()), math.floor(scenePoint.y())))
        self.__update_preview()

    def __generate_x_y_w_h(self, point: tuple) -> None:
        """
        This method will automatically slice the sprite

        @param point: (x, y) based on where user clicked on the preview.
        """
        x, y = point
        np_image = self.__pixmap_to_numpy() 
        np_pixels_checked = np.zeros(np_image.shape[:-1], dtype=np.uint8)
        self.min_x, self.max_x = None, None
        self.min_y, self.max_y = None, None

        if np_image[y, x, 3] == 0: # clicked on transparent pixel (no sprite to be found)
            print("transparent pixel")
            return
        
        print("clicked on pixel:", x, y)
        self.__sprite_finder(x, y, np_image, np_pixels_checked)

        self.x = self.min_x
        self.y = self.min_y
        self.w = self.max_x - self.min_x + 1
        self.h = self.max_y - self.min_y + 1

        self.__update_sprite_dimensions_textboxes()

    def __sprite_finder(self, x: int, y: int, image: np.ndarray, pixels_checked: np.ndarray) -> None:
        """
        Recursive method to find the max and min x y coordinates of a clicked sprite
        @param x: x coordinate
        @param y: y coordinate
        @param image: numpy array of the image
        @param pixels_checked: numpy array of the pixels that have been checked (all zeros by default) (1 for checked) (same shape as image)0
        """
        # get coordinates of all surrounding pixels, including diagonals
        surrounding_pixels = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1), (x + 1, y + 1), (x - 1, y - 1), (x + 1, y - 1), (x - 1, y + 1)]
        for x, y in surrounding_pixels:
            if x < 0 or y < 0 or x > image.shape[1]-1 or y > image.shape[0]-1 or pixels_checked[y, x] == 1 or image[y, x, 3] == 0:
                continue
            pixels_checked[y, x] = 1
            if self.max_x is None or x > self.max_x: self.max_x = x
            if self.min_x is None or x < self.min_x: self.min_x = x
            if self.max_y is None or y > self.max_y: self.max_y = y
            if self.min_y is None or y < self.min_y: self.min_y = y
            self.__sprite_finder(x, y, image, pixels_checked)
            
    def __pixmap_to_numpy(self):
        """
        returns a numpy array of the pixmap in BGRA (don't ask me why) format, all that matters is that the last value is alpha.
        """
        channels_count = 4
        image = self.pixmap.toImage()
        s = image.bits().asstring(self.pixmap.width() * self.pixmap.height() * channels_count)
        arr = np.fromstring(s, dtype=np.uint8).reshape((self.pixmap.height(), self.pixmap.width(), channels_count))
        return arr

    def __init_vars(self):
        self.image_file = ""
        self.pixmap = None
        self.desc = ""
        self.index = None
        self.__init_xywh()

    def __init_xywh(self):
        self.x = None
        self.y = None
        self.w = None
        self.h = None

    def __set_stylesheets(self) -> None:
        self.preview.setStyleSheet("background-color: white;")
        self.slicer.setStyleSheet("background-color: white;")

    def __init_preview(self):
        self.preview.setScene(QtWidgets.QGraphicsScene())
        self.preview.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.preview.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.preview.setResizeAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)
        self.preview.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)

    def __init_slicer(self) -> None:
        self.slicer.setScene(QtWidgets.QGraphicsScene())
        self.slicer.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.slicer.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.slicer.wheelEvent = self.__slicer_wheel_event

    def __slicer_wheel_event(self, e) -> None:
        if e.angleDelta().y() > 0:
            if self.slicer.transform().m11() < 15: self.slicer.scale(1.1, 1.1)
        else:
            if self.slicer.transform().m11() > 0.75: self.slicer.scale(1 / 1.1, 1 / 1.1)
        e.accept()

    def update(self) -> None:
        self.__init_xywh()
        self.image_file = self.animator.find_file(self.image_combobox.currentText().strip())
        self.__draw_on_slicer()
        self.__update_preview()

    def __update_preview(self) -> None:
        self.preview.scene().clear()
        if self.pixmap and self.x is not None and self.y is not None and self.w and self.h:
            print("updating preview")
            self.preview.scene().addPixmap(self.pixmap.copy(self.x, self.y, self.w, self.h))
            self.preview.fitInView(self.preview.scene().itemsBoundingRect(), QtCore.Qt.KeepAspectRatio)
            
    def __draw_on_slicer(self) -> None:
        self.pixmap = QtGui.QPixmap(self.image_file)
        self.slicer.scene().clear()
        self.slicer.scene().addPixmap(self.pixmap)
        self.slicer.fitInView(self.slicer.scene().itemsBoundingRect(), QtCore.Qt.KeepAspectRatio)

    def update_desc(self) -> None:
        print("updating desc")
        self.desc = self.desc_textbox.text()

    def update_index(self) -> None:
        print("updating index")
        self.index = int(self.sprite_index_textbox.text()) if self.sprite_index_textbox.text() != "-" else self.index

    def update_x(self, e) -> None:
        text = self.x_textbox.text()
        self.x = int(text) if text else self.x
        self.__update_preview()

    def update_y(self, e) -> None:
        text = self.y_textbox.text()
        self.y = int(text) if text else self.y
        self.__update_preview()

    def update_w(self, e) -> None:
        text = self.width_textbox.text()
        self.w = int(text) if text else self.w
        self.__update_preview()

    def update_h(self, e) -> None:
        text = self.height_textbox.text()
        self.h = int(text) if text else self.h
        self.__update_preview()

    def __update_sprite_dimensions_textboxes(self) -> None:
        self.x_textbox.setText(str(self.x))
        self.y_textbox.setText(str(self.y))
        self.width_textbox.setText(str(self.w))
        self.height_textbox.setText(str(self.h))

