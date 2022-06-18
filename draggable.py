from PyQt5 import QtCore, QtGui, QtWidgets

class DragImage(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, parent, image, x=0, y=0):
        super().__init__(image)
        self.parent = parent
        self.setPos(x, y)
        self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, event):
        self.setCursor(QtCore.Qt.OpenHandCursor)

    def hoverLeaveEvent(self, event):
        self.setCursor(QtCore.Qt.ArrowCursor)

    def mousePressEvent(self, event):
        print("pressed")

    def mouseMoveEvent(self, event):
        orig_pos = event.lastScenePos()
        updated_pos = event.scenePos()
        new_pos = self.pos() + updated_pos - orig_pos
        self.setPos(new_pos)

    def mouseReleaseEvent(self, event):
        x, y = round(self.pos().x()), round(self.pos().y())
        self.setPos(x, y)
        print(x,y)
