from PyQt5 import QtCore, QtGui, QtWidgets


class DragImage(QtWidgets.QGraphicsPixmapItem):
    """
    Subclass of QGraphicsPixMapItem to allow for dragging of sprites on the canvas
    """
    def __init__(self, parent, sprite, x=0, y=0):
        super().__init__(parent.sprite_images[sprite.index])
        self.parent = parent
        self.sprite = sprite
        self.setPos(x, y)
        self.setAcceptHoverEvents(True)
        self.__set_curr_sprite()

    def hoverEnterEvent(self, event):
        self.setCursor(QtCore.Qt.OpenHandCursor)

    def hoverLeaveEvent(self, event):
        self.setCursor(QtCore.Qt.ArrowCursor)

    def mousePressEvent(self, event):
        print("pressed")
        # TODO: Make this sprite the selected sprite

    def mouseMoveEvent(self, event):
        self.setCursor(QtCore.Qt.ClosedHandCursor)
        orig_pos = event.lastScenePos()
        updated_pos = event.scenePos()
        new_pos = self.pos() + updated_pos - orig_pos
        self.setPos(new_pos)

    def mouseReleaseEvent(self, event):
        self.setCursor(QtCore.Qt.OpenHandCursor)
        x, y = round(self.pos().x()), round(self.pos().y())
        self.setPos(x, y)
        print(x, y)

    def __set_new_sprite_pos(self, x, y):
        pass # TODO : Set the new position of the sprite on the current frame part

    def __set_curr_sprite(self):
        self.parent.set_curr_sprite(self.sprite.index)


class DragSpriteView(QtWidgets.QGraphicsView):
    """
    Subclass of QGraphicsView for dragging sprites from side bar to canvas
    """
    def __init__(self, parent, image, index, all_sprites):
        super().__init__(parent.sprite_scroll_area.widget())
        self.parent = parent
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.setScene(QtWidgets.QGraphicsScene())
        self.scene().addPixmap(image)
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

        self.setToolTip(f"Sprite: {index}: " + [sprite.desc for sprite in all_sprites if sprite.index == index][0])
        parent.sprite_scroll_area.widget().layout().addWidget(self)

    def enterEvent(self, event):
        self.setCursor(QtCore.Qt.OpenHandCursor)

    def leaveEvent(self, event):
        self.setCursor(QtCore.Qt.ArrowCursor)





