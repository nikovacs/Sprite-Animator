import copy
import math
import sys
from PIL import Image, ImageQt
from PyQt5 import QtWidgets, QtCore, QtGui, QtWidgets
from new_sprite_ui import Ui_Dialog as NewSpriteUI
from sprite import Sprite
import numpy as np

class NewSpriteDialog(NewSpriteUI):
    def __init__(self, animator, parent=None, from_sprite=None):
        self.setupUi(parent)
        self.parent = parent
        self.animator = animator
        parent.setWindowTitle("Add New Sprite")
        sys.setrecursionlimit(10000)

        self.from_sprite = from_sprite
        self.__x_offset = 0
        self.__y_offset = 0

        self.__set_stylesheets()
        self.__init_vars()
        self.listen = False

        self.__init_slicer()
        self.__init_preview()

        self.image_combobox.currentIndexChanged.connect(self.new_image)
        self.image_combobox.lineEdit().returnPressed.connect(self.new_image)

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

        self.zoom_textbox.setText("1")
        self.zoom_textbox.setValidator(QtGui.QDoubleValidator(-100, 100, 2))
        self.zoom_textbox.textChanged.connect(self.__update_zoom)

        self.rotate_textbox.setText("0")
        self.rotate_textbox.setValidator(QtGui.QIntValidator(-360, 360))
        self.rotate_textbox.textChanged.connect(self.__update_rotate)

        self.stretchx_textbox.setText("1")
        self.stretchx_textbox.setValidator(QtGui.QDoubleValidator(-100, 100, 2))
        self.stretchx_textbox.textChanged.connect(self.__update_stretchx)

        self.stretchy_textbox.setText("1")
        self.stretchy_textbox.setValidator(QtGui.QDoubleValidator(-100, 100, 2))
        self.stretchy_textbox.textChanged.connect(self.__update_stretchy)

        color_validator = QtGui.QDoubleValidator(0, 1, 2)
        color_validator.setNotation(QtGui.QDoubleValidator.StandardNotation)

        self.red.setValidator(color_validator)
        self.red.textChanged.connect(self.__validate_color)
        
        self.green.setValidator(color_validator)
        self.green.textChanged.connect(self.__validate_color)

        self.blue.setValidator(color_validator)
        self.blue.textChanged.connect(self.__validate_color)

        self.alpha.setValidator(color_validator)
        self.alpha.textChanged.connect(self.__validate_color)

        self.add_and_continue_btn.clicked.connect(self.__add_and_continue)
        # disable using enter key on the button
        self.add_and_continue_btn.setAutoDefault(False)

        self.add_and_close_btn.clicked.connect(self.__add_and_close)
        # disable using enter key on the button
        self.add_and_close_btn.setAutoDefault(False)

        self.mode_textbox.setText("0")
        self.mode_textbox.setValidator(QtGui.QIntValidator(0, 2))
        self.mode_textbox.textChanged.connect(self.__update_preview)

        self.update()

    def new_image(self) -> None:
        if self.listen:
            self.from_sprite = None
            self.update()
        else:
            self.listen = True

    def __validate_color(self) -> None:
        color_textboxes = [self.red, self.green, self.blue, self.alpha]
        for element in color_textboxes:
            text = element.text()
            if text == "." or text == "": return
            if float(text) > 1: element.setText("1")
            if float(text) < 0: element.setText("0")
        self.__update_preview()

    def __update_zoom(self) -> None:
        if self.zoom_textbox.text()  in ("-", ".", ""):
            return
        self.__update_preview()

    def __update_rotate(self) -> None:
        if self.rotate_textbox.text() in ("-", ".", ""):
            return
        if float(self.rotate_textbox.text()) > 360:
            self.rotate_textbox.setText("360")
        if float(self.rotate_textbox.text()) < -360:
            self.rotate_textbox.setText("-360")
        self.__update_preview()

    def __update_stretchx(self) -> None:
        if self.stretchx_textbox.text() in ("-", ".", ""):
            return
        self.__update_preview()

    def __update_stretchy(self) -> None:
        if self.stretchy_textbox.text() in ("-", ".", ""):
            return
        self.__update_preview()

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
        np_image = NewSpriteDialog.__pixmap_to_numpy(self.slicer_pixmap)

        if x < 0 or y < 0 or x >= np_image.shape[1] or y >= np_image.shape[0]:
            return

        np_pixels_checked = np.zeros(np_image.shape[:-1], dtype=np.uint8)
        self.min_x, self.max_x = None, None
        self.min_y, self.max_y = None, None

        if np_image[y, x, 3] == 0:  # clicked on transparent pixel (no sprite to be found)
            return

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

    # def __sprite_finder(self, x: int, y: int, image: np.ndarray) -> None:
    #     """
    #     Recursive method to find the max and min x y coordinates of a clicked sprite
    #     @param x: x coordinate
    #     @param y: y coordinate
    #     @param image: numpy array of the image
    #     @param pixels_checked: numpy array of the pixels that have been checked (all zeros by default) (1 for checked) (same shape as image)0
    #     """
    #     np_pixels_checked = np.zeros(image.shape[:-1], dtype=np.uint8)


    def __init_vars(self):
        image = self.from_sprite.image if self.from_sprite else "SPRITES"
        self.image_combobox.lineEdit().setText(image)
        self.image_file = ""
        self.slicer_pixmap = None
        self.preview_pixmap = None
        self.desc = self.from_sprite.desc if self.from_sprite else ""
        self.index = self.from_sprite.index if self.from_sprite else ""

    def __init_xywh(self):
        self.x = self.from_sprite.x if self.from_sprite else ""
        self.y = self.from_sprite.y if self.from_sprite else ""
        self.w = self.from_sprite.width if self.from_sprite else ""
        self.h = self.from_sprite.height if self.from_sprite else ""

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
        self.__update_sprite_dimensions_textboxes()
        self.__update_sprite_effects_textboxes()
        self.__update_sprite_textboxes()
        self.__draw_on_slicer()
        self.__update_preview()

    def __update_sprite_textboxes(self) -> None:
        self.sprite_index_textbox.setText(str(self.index))
        self.desc_textbox.setText(self.desc)

    def __update_sprite_effects_textboxes(self) -> None:
        zoom = self.from_sprite.zoom if self.from_sprite else 1
        self.zoom_textbox.setText(str(zoom))
        rotation = self.from_sprite.rotation if self.from_sprite else 0
        self.rotate_textbox.setText(str(rotation))
        stretch_x = self.from_sprite.stretch_x if self.from_sprite else 1
        self.stretchx_textbox.setText(str(stretch_x))
        stretch_y = self.from_sprite.stretch_y if self.from_sprite else 1
        self.stretchy_textbox.setText(str(stretch_y))
        r, g, b, a = self.from_sprite.color_effect if self.from_sprite else (1, 1, 1, 1)
        self.red.setText(str(r))
        self.green.setText(str(g))
        self.blue.setText(str(b))
        self.alpha.setText(str(a))

    def __update_preview(self) -> None:
        self.preview.scene().clear()
        if self.slicer_pixmap and self.x is not None and self.y is not None and self.w and self.h and self.x >= 0 and self.y >= 0 and self.w >= 1 and self.h >= 1:
            sprite = self.__setup_sprite()
            self.preview_pixmap, self.__x_offset, self.__y_offset = NewSpriteDialog.load_and_crop_sprite(self.image_file, sprite)
            self.preview.scene().addPixmap(self.preview_pixmap.copy(self.__x_offset, self.__y_offset, self.w, self.h))
            self.preview.fitInView(self.preview.scene().itemsBoundingRect(), QtCore.Qt.KeepAspectRatio)

    def __setup_sprite(self) -> Sprite:
        index = self.index if isinstance(self.index, int) else -1
        sprite = Sprite(index, self.image_combobox.currentText().strip(), self.x, self.y, self.w, self.h, self.desc_textbox.text())
        if self.zoom_textbox.text() != "1":
            sprite.zoom = float(self.zoom_textbox.text())
        if self.rotate_textbox.text() != "0":
            sprite.rotation = float(self.rotate_textbox.text())
        if self.stretchx_textbox.text() != "1":
            sprite.stretch_x = float(self.stretchx_textbox.text())
        if self.stretchy_textbox.text() != "1":
            sprite.stretch_y = float(self.stretchy_textbox.text())
        if self.red.text() != "1" or self.green.text() != "1" or self.blue.text() != "1" or self.alpha.text() != "1":
            sprite.color_effect = (float(self.red.text()), float(self.green.text()), float(self.blue.text()), float(self.alpha.text()))
        if self.mode_textbox.text() != "":
            sprite.mode = int(self.mode_textbox.text())
        return sprite
            
    def __draw_on_slicer(self) -> None:
        self.slicer_pixmap = QtGui.QPixmap(self.image_file)
        self.slicer.scene().clear()
        self.slicer.scene().addPixmap(self.slicer_pixmap)
        self.slicer.fitInView(self.slicer.scene().itemsBoundingRect(), QtCore.Qt.KeepAspectRatio)

    def update_desc(self) -> None:
        self.desc = self.desc_textbox.text()

    def update_index(self) -> None:
        if self.sprite_index_textbox.text():
            self.index = int(self.sprite_index_textbox.text()) if self.sprite_index_textbox.text() != "-" else self.index
        else:
            self.index = ""

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

    def add_sprite_to_animator(self, sprite: Sprite) -> None:
        self.animator.image_path_map[sprite.index] = self.image_file
        self.animator.add_sprite_to_scroll_area(sprite)

    def __add_and_continue(self) -> None:
        if self.__ready_to_add():
            self.add_sprite_to_animator(self.__setup_sprite())

    def __add_and_close(self) -> None:
        if self.__ready_to_add():
            self.add_sprite_to_animator(self.__setup_sprite())
            QtWidgets.QDialog.accept(self.parent)

    def __ready_to_add(self) -> bool:
        return self.__valid_x() and self.__valid_y() and isinstance(self.index, int)
    
    def __valid_x(self) -> bool:
        return self.x is not None and 0 <= self.x < self.slicer_pixmap.width()
        
    def __valid_y(self) -> bool:
        return self.y is not None and 0 <= self.y < self.slicer_pixmap.height()
        
    """
    static methods
    """
    @staticmethod
    def pad_pixmap(pixmap: QtGui.QPixmap, padding_x: int, padding_y: int) -> QtGui.QPixmap:
        """
        returns a pixmap with padding around it
        """
        new_width, new_height = pixmap.width() + padding_x * 2, pixmap.height() + padding_y * 2
        new_pixmap = QtGui.QPixmap(new_width, new_height)
        new_pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(new_pixmap)
        painter.drawPixmap(padding_x, padding_y, pixmap)
        painter.end()
        return new_pixmap

    @staticmethod
    def rotate_pixmap(sprite, pixmap):
        if sprite.rotation != 0:
            wh = max(pixmap.width(), pixmap.height()) * 2
            if wh % 2 == 1: wh += 1
            pixmap = NewSpriteDialog.pad_pixmap(pixmap, abs(pixmap.width() - wh) / 2, abs(pixmap.height() - wh) / 2)
            x_diff, y_diff = NewSpriteDialog.calculate_diffs(pixmap, wh)
            new_pixmap = QtGui.QPixmap(wh, wh)
            new_pixmap.fill(QtCore.Qt.transparent)
            painter = QtGui.QPainter(new_pixmap)
            painter.translate(pixmap.width() / 2, pixmap.height() / 2)
            painter.rotate(sprite.rotation)
            painter.translate(-pixmap.width() / 2, -pixmap.height() / 2)
            painter.drawPixmap(x_diff, y_diff, pixmap)
            painter.end()
            return new_pixmap
        return pixmap

    @staticmethod
    def calculate_diffs(pixmap, wh):
        x_diff, y_diff = (wh - pixmap.width()) / 2, (wh - pixmap.height()) / 2
        return x_diff, y_diff

    @staticmethod
    def stretch_pixmap(sprite: Sprite, pixmap: QtGui.QPixmap):
        """
        stretches a pixmap in the appropriate direction by the corresponding factor
        @param sprite: the sprite object
        @param pixmap: the pixmap to stretch
        @return: the stretched pixmap, but with maintained 0, 0
        """
        if sprite.stretch_x != 1 or sprite.stretch_y != 1:
            wh = max(pixmap.width(), pixmap.height()) * max(abs(sprite.stretch_x), abs(sprite.stretch_y)) * 2
            if wh % 2 == 1: wh += 1
            pixmap = NewSpriteDialog.pad_pixmap(pixmap, abs(pixmap.width() - wh) / 2, abs(pixmap.height() - wh) / 2)
            x_diff, y_diff = NewSpriteDialog.calculate_diffs(pixmap, wh)
            new_pixmap = QtGui.QPixmap(wh, wh)
            new_pixmap.fill(QtCore.Qt.transparent)
            painter = QtGui.QPainter(new_pixmap)
            painter.translate(pixmap.width() / 2, pixmap.height() / 2)
            painter.scale(sprite.stretch_x, sprite.stretch_y)
            painter.translate(-pixmap.width() / 2, -pixmap.height() / 2)
            painter.drawPixmap(x_diff, y_diff, pixmap)
            painter.end()
            return new_pixmap
        return pixmap

    @staticmethod
    def add_color_effects_to_pixmap(sprite: Sprite, pixmap: QtGui.QPixmap):
        if sprite.color_effect != [1, 1, 1, 1] or sprite.mode == 2:
            alpha = sprite.color_effect[3]
            if (alpha == 1 and sprite.mode != 2) or sprite.mode == 1:
                pixmap = NewSpriteDialog.__add_color_mode_1(sprite, pixmap)
            elif alpha != 1 and sprite.mode == 0:
                pixmap = NewSpriteDialog.__add_color_mode_0(sprite, pixmap)
            elif sprite.mode == 2:
                pixmap = NewSpriteDialog.__add_color_mode_2(sprite, pixmap)
        return pixmap

    @staticmethod
    def __add_color_mode_0(sprite: Sprite, pixmap: QtGui.QPixmap) -> QtGui.QPixmap:
        grayscale = pixmap.toImage().convertToFormat(QtGui.QImage.Format_Grayscale8)
        grayscale = QtGui.QPixmap.fromImage(grayscale)
        np_pixmap = NewSpriteDialog.__pixmap_to_numpy(grayscale)  # remember! in BGRA format
        red, green, blue, alpha = sprite.color_effect
        np_pixmap[:, :, 3] = copy.deepcopy(np_pixmap[:, :, 0]) * alpha
        np_pixmap[:, :, 0] = np_pixmap[:, :, 0] * blue
        np_pixmap[:, :, 1] = np_pixmap[:, :, 1] * green
        np_pixmap[:, :, 2] = np_pixmap[:, :, 2] * red
        # convert back to RGBA
        temp_blue, temp_red = copy.deepcopy(np_pixmap[:, :, 0]), np_pixmap[:, :, 2]
        np_pixmap[:, :, 0] = temp_red
        np_pixmap[:, :, 2] = temp_blue
        return NewSpriteDialog.__numpy_to_pixmap(np_pixmap)

    @staticmethod
    def __add_color_mode_1(sprite: Sprite, pixmap: QtGui.QPixmap) -> QtGui.QPixmap:
        red, green, blue, alpha = sprite.color_effect
        np_pixmap = NewSpriteDialog.__pixmap_to_numpy(pixmap)  # remember! in BGRA format
        np_pixmap[:, :, 0] = np_pixmap[:, :, 0] * blue
        np_pixmap[:, :, 1] = np_pixmap[:, :, 1] * green
        np_pixmap[:, :, 2] = np_pixmap[:, :, 2] * red
        np_pixmap[:, :, 3] = np_pixmap[:, :, 3] * alpha
        # convert back to RGBA
        temp_blue, temp_red = copy.deepcopy(np_pixmap[:, :, 0]), np_pixmap[:, :, 2]
        np_pixmap[:, :, 0] = temp_red
        np_pixmap[:, :, 2] = temp_blue
        return NewSpriteDialog.__numpy_to_pixmap(np_pixmap)

    @staticmethod
    def __add_color_mode_2(sprite: Sprite, pixmap: QtGui.QPixmap) -> QtGui.QPixmap:
        grayscale = pixmap.toImage().convertToFormat(QtGui.QImage.Format_Grayscale8)
        grayscale = QtGui.QPixmap.fromImage(grayscale)
        red, green, blue, alpha = sprite.color_effect
        np_pixmap = NewSpriteDialog.__pixmap_to_numpy(grayscale)  # remember! in BGRA format
        np_pixmap[:, :, 3] = copy.deepcopy(np_pixmap[:, :, 0]) * alpha
        np_pixmap[:, :, 0] = np_pixmap[:, :, 0] - np_pixmap[:, :, 0] * blue
        np_pixmap[:, :, 1] = np_pixmap[:, :, 1] - np_pixmap[:, :, 1] * green
        np_pixmap[:, :, 2] = np_pixmap[:, :, 2] - np_pixmap[:, :, 2] * red
        # convert back to RGBA
        temp_blue, temp_red = copy.deepcopy(np_pixmap[:, :, 0]), np_pixmap[:, :, 2]
        np_pixmap[:, :, 0] = temp_red
        np_pixmap[:, :, 2] = temp_blue
        return NewSpriteDialog.__numpy_to_pixmap(np_pixmap)



    @staticmethod
    def zoom_pixmap(sprite: Sprite, pixmap: QtGui.QPixmap):
        if sprite.zoom != 1:
            if abs(sprite.zoom) > 1:
                wh = max(pixmap.width(), pixmap.height()) * abs(sprite.zoom) * 2
                if wh % 2 == 1: wh += 1
            else:
                wh = max(pixmap.width(), pixmap.height())
            pixmap = NewSpriteDialog.pad_pixmap(pixmap, abs(pixmap.width() - wh) / 2, abs(pixmap.height() - wh) / 2)
            x_diff, y_diff = NewSpriteDialog.calculate_diffs(pixmap, wh)
            new_pixmap = QtGui.QPixmap(wh, wh)
            new_pixmap.fill(QtCore.Qt.transparent)
            painter = QtGui.QPainter(new_pixmap)
            painter.translate(pixmap.width() / 2, pixmap.height() / 2)
            painter.scale(sprite.zoom, sprite.zoom)
            painter.translate(-pixmap.width() / 2, -pixmap.height() / 2)
            painter.drawPixmap(x_diff, y_diff, pixmap)
            painter.end()
            return new_pixmap
        return pixmap

    @staticmethod
    def fix_sprite_xy_and_get_excess_dimensions(im_height, im_width, sprite) -> tuple:
        x_to_increase, y_to_increase = 0, 0
        if sprite.x + sprite.width > im_width:
            x_to_increase = sprite.x + sprite.width - im_width
            sprite.width = im_width - sprite.x
        if sprite.y + sprite.height > im_height:
            y_to_increase = sprite.y + sprite.height - im_height
            sprite.height = im_height - sprite.y
        return x_to_increase, y_to_increase

    @staticmethod
    def expand_pixmap_if_needed(pixmap, x_to_increase=0, y_to_increase=0) -> QtGui.QPixmap:
        if x_to_increase > 0 or y_to_increase > 0:
            new_x = pixmap.width() + x_to_increase
            new_y = pixmap.height() + y_to_increase
            new_pixmap = QtGui.QPixmap(new_x, new_y)
            new_pixmap.fill(QtCore.Qt.transparent)
            painter = QtGui.QPainter(new_pixmap)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            return new_pixmap
        return pixmap
    
    @staticmethod
    def load_and_crop_sprite(image_path, sprite) -> tuple:
        """
        This method is intended to be called from within a with TemporaryDirectory() block.
        @param image_path: the path to the image to load
        @param sprite: the sprite object
        @return: the final pixmap, x_offset, y_offset
        """
        if image_path:
            im = Image.open(image_path, mode="r")
            im_width, im_height = im.size
            x_to_increase, y_to_increase = NewSpriteDialog.fix_sprite_xy_and_get_excess_dimensions(im_height, im_width, sprite)
            im = im.crop((sprite.x, sprite.y, sprite.x + sprite.width, sprite.y + sprite.height))
            im = ImageQt.ImageQt(im.convert("RGBA"))
            original_pixmap = QtGui.QPixmap.fromImage(im)
            original_pixmap = NewSpriteDialog.expand_pixmap_if_needed(original_pixmap, x_to_increase, y_to_increase)
            pixmap = NewSpriteDialog.rotate_pixmap(sprite, original_pixmap)
            pixmap = NewSpriteDialog.stretch_pixmap(sprite, pixmap)
            pixmap = NewSpriteDialog.zoom_pixmap(sprite, pixmap)
            pixmap = NewSpriteDialog.add_color_effects_to_pixmap(sprite, pixmap)
            x_offset, y_offset = NewSpriteDialog.__generate_offsets(original_pixmap, pixmap)
            return pixmap, x_offset, y_offset
        return NewSpriteDialog.__make_default_sprite_img(sprite), 0, 0

    @staticmethod
    def __make_default_sprite_img(sprite: Sprite) -> QtGui.QPixmap:
        return QtGui.QPixmap(sprite.width, sprite.height)

    @staticmethod
    def __generate_offsets(original_pixmap: QtGui.QPixmap, pixmap: QtGui.QPixmap) -> tuple:
        """
        This method is called after modifying the sprite pixmap...
        Such as, rotating, zooming, stretching, or anything else that changes the size of the pixmap.
        @param sprite: Sprite object of the corresponding pixmap. Needed for its attributes (specifically index).
        @param original_pixmap: The original pixmap before any modifications.
        @param pixmap: The pixmap after modifications.
        @return: The x and y offsets of the pixmap.
        """
        return (abs(original_pixmap.width() / 2 - pixmap.width() / 2), abs(original_pixmap.height() / 2 - pixmap.height() / 2))

    @staticmethod
    def __pixmap_to_numpy(pixmap: QtGui.QPixmap) -> np.ndarray:
        """
        returns a numpy array of the pixmap in RGBA format.
        All that matters is that the alpha is the fourth value.
        @param pixmap: QtGui.QPixmap to be turned into a numpy array
        @return: numpy array of the pixmap in RGBA format. (shape: (height, width, 4))
        """
        channels_count = 4
        image = pixmap.toImage()
        s = image.bits().asstring(pixmap.width() * pixmap.height() * channels_count)
        arr = np.fromstring(s, dtype=np.uint8).reshape((pixmap.height(), pixmap.width(), channels_count))
        return arr

    @staticmethod
    def __numpy_to_pixmap(np_image: np.ndarray) -> QtGui.QPixmap:
        """
        returns a QPixmap from a numpy array.
        """
        image = QtGui.QImage(np_image.data, np_image.shape[1], np_image.shape[0], QtGui.QImage.Format_RGBA8888)
        pixmap = QtGui.QPixmap.fromImage(image)
        return pixmap


