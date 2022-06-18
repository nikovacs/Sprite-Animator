from PyQt5 import QtCore, QtWidgets

class AniGraphicsView(QtWidgets.QGraphicsView):
    """
    This class extends QGraphicsView and contains QGraphicsScene to allow for clicking and dragging on the screen
    """
    def __init__(self, widget, scene_rect_x, scene_rect_y, def_scale):
        """
        @param scene_rect_x/y: may be specified depending on the type of animation. For Ganis, the values should be -32, 32 respectively.
        @param def_scale: the default scale of the view
        """
        super().__init__(widget)

        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setSceneRect(scene_rect_x, scene_rect_y, self.width(), self.height())
        
        self.scene = QtWidgets.QGraphicsScene()
        self.setScene(self.scene)

        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)

        self.scale(def_scale, def_scale)
