from PyQt5 import QtCore, QtGui, QtWidgets


class DragImage(QtWidgets.QGraphicsPixmapItem):
    """
    Subclass of QGraphicsPixMapItem to allow for dragging of sprites on the canvas
    """
    def __init__(self, parent, sprite, layer_index, x=0, y=0, x_offset=0, y_offset=0):
        """
        @param parent: The parent widget of the sprite. Pass in self as arg when instantiating most of the time
        @param sprite: The Sprite Object that is being drawn
        @param layer_index: The index(order) of the sprite on the screen. Bottom-most sprite would be 0.
        @param x: The x position of the sprite on the screen
        @param y: The y position of the sprite on the screen
        """
        super().__init__(parent.sprite_images[sprite.index])
        self.parent = parent
        self.sprite = sprite
        self.layer_index = layer_index
        self.setAcceptHoverEvents(True)
        self.__x, self.__y = x, y
        self.__x_offset = x_offset
        self.__y_offset = y_offset
        self.__set_pos()

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @property
    def real_x(self):
        return self.x - self.__x_offset

    @property
    def real_y(self):
        return self.y - self.__y_offset

    def hoverEnterEvent(self, event):
        self.setCursor(QtCore.Qt.OpenHandCursor)

    def hoverLeaveEvent(self, event):
        self.setCursor(QtCore.Qt.ArrowCursor)

    def mousePressEvent(self, event):
        self.setCursor(QtCore.Qt.ClosedHandCursor)
        self.__set_curr_sprite()

    def mouseMoveEvent(self, event):
        self.setCursor(QtCore.Qt.ClosedHandCursor)
        orig_pos = event.lastScenePos()
        updated_pos = event.scenePos()
        new_pos = self.pos() + updated_pos - orig_pos
        self.__x, self.__y = new_pos.x(), new_pos.y()
        self.__set_pos()

    def mouseReleaseEvent(self, event):
        self.setCursor(QtCore.Qt.OpenHandCursor)
        self.__x, self.__y = round(self.pos().x()), round(self.pos().y())
        self.__set_pos()
        self.__set_new_sprite_pos(self.__x, self.__y)

    def __set_new_sprite_pos(self, old_x: int, old_y: int) -> None:
        x_diff, y_diff = self.__x - old_x, self.__y - old_y
        if x_diff != 0:
            self.parent.shift_sprite("horizontal", x_diff)
        if y_diff != 0:
            self.parent.shift_sprite("vertical", y_diff)

    def __set_curr_sprite(self) -> None:
        self.parent.set_curr_sprite(self.layer_index)

    def __set_pos(self) -> None:
        self.setPos(self.real_x, self.real_y)


class DragSpriteView(QtWidgets.QGraphicsView):
    """
    Subclass of QGraphicsView for dragging sprites from side bar to canvas
    """
    def __init__(self, parent, image, index, all_sprites):
        super().__init__(parent.sprite_scroll_area.widget())
        self.parent = parent
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.setScene(QtWidgets.QGraphicsScene())
        self.scene().addPixmap(image)

        self.sprite = None
        for sprite in all_sprites:
            if sprite.index == index:
                self.sprite = sprite
                break

        self.setToolTip(f"Sprite({index}) " + sprite.desc)
        parent.sprite_scroll_area.widget().layout().addWidget(self)

    def enterEvent(self, event):
        self.setCursor(QtCore.Qt.OpenHandCursor)

    def leaveEvent(self, event):
        self.setCursor(QtCore.Qt.ArrowCursor)

    def keyPressEvent(self, event):
        """
        Calls the keypressevent method of parent so that the sprite can still be moved by the arrow keys without having
        to click on the main canvas window/sprite
        """
        self.parent.key_press_event(event)





