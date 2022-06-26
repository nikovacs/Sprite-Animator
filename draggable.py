from PyQt5 import QtCore, QtGui, QtWidgets


class DragImage(QtWidgets.QGraphicsPixmapItem):
    """
    Subclass of QGraphicsPixMapItem to allow for dragging of sprites on the canvas
    """
    def __init__(self, parent, sprite, layer_index, x=0, y=0):
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
        self.setPos(x, y)
        self.setAcceptHoverEvents(True)
        self.x, self.y = x, y
        self.__set_curr_sprite()

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
        self.setPos(new_pos)

    def mouseReleaseEvent(self, event):
        old_x, old_y = self.x, self.y
        self.setCursor(QtCore.Qt.OpenHandCursor)
        self.x, self.y = round(self.pos().x()), round(self.pos().y())
        self.setPos(self.x, self.y)
        self.__set_new_sprite_pos(old_x, old_y)

    def __set_new_sprite_pos(self, old_x: int, old_y: int) -> None:
        x_diff, y_diff = self.x - old_x, self.y - old_y
        if x_diff != 0:
            self.parent.shift_sprite("horizontal", x_diff)
        if y_diff != 0:
            self.parent.shift_sprite("vertical", y_diff)

    def __set_curr_sprite(self):
        self.parent.set_curr_sprite(self.layer_index)


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





