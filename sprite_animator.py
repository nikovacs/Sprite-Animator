from PyQt5 import QtCore, QtGui, QtWidgets
from ui import Ui_MainWindow
from new_sprite_ui import Ui_Dialog as NewSpriteDialog
from animation import Animation
import sys
import os

class Animator_GUI(Ui_MainWindow):
    def __init__(self, MainWindow) -> None:
        super().__init__()
        super().setupUi(MainWindow)
        self.graphics_view_init()

        self.curr_dir = self.dir_combo_box.currentText()
        self.curr_animation = None

        #link bg_color_btn to change_background_color method
        self.bg_color_btn.clicked.connect(self.change_background_color)

        # link self.plus_sprite_btn to add_new_sprite method
        self.plus_sprite_btn.clicked.connect(self.add_new_sprite)

        # link dir_combo_box to change_dir method
        self.dir_combo_box.currentIndexChanged.connect(self.change_dir)

        # link new_btn to new_animation method
        self.new_btn.clicked.connect(self.new_animation)

        # link save_btn to save_animation method
        self.save_btn.clicked.connect(self.save_animation)

        # link saveas_btn to save_animation_as method
        self.saveas_btn.clicked.connect(self.save_animation_as)

        # link reverse_btn to reverse_frames method
        self.reverse_btn.clicked.connect(self.reverse_frames)

        # link open_btn to new_animation method
        self.open_btn.clicked.connect(lambda: self.new_animation(from_file=True))

        # link scroll wheel to wheelEvent method
        self.graphicsView.wheelEvent = self.wheelEvent
    
    def graphics_view_init(self):
        self.graphicsView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.graphicsView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.graphicsView.setSceneRect(25, 50, self.graphicsView.width(), self.graphicsView.height())

        # the intersection of the following lines is 0,0
        self.graphicsView.setScene(QtWidgets.QGraphicsScene())
        scene = self.graphicsView.scene()
        scene.addLine(0, -1000, 0, 1000)
        scene.addLine(-1000, 0, 1000, 0)

        # set anchors to be center of the screen
        self.graphicsView.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)
        self.graphicsView.setResizeAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)

        # set default zoom percentage
        self.graphicsView.scale(1.5, 1.5)

        # draw a circle on the screen
        scene.addEllipse(0, 0, 100, 100)
        
    # setup scroll wheel events for the graphics view
    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.graphicsView.scale(1.1, 1.1)
        else:
            self.graphicsView.scale(1 / 1.1, 1 / 1.1)
        event.accept()


    def new_animation(self, from_file=False) -> None:
        if from_file:
            # display a QFileDialog to get the file name
            file = self.__get_gani_file()
            if file.endswith(".gani"):
                self.curr_animation = Animation(from_file=file)
        else:
            self.curr_animation = Animation()

    def reverse_frames(self) -> None:
        if self.curr_animation:
            pass

    def save_animation_as(self) -> None:
        if self.curr_animation:
            pass

    def save_animation(self) -> None:
        if self.curr_animation:
            pass

    def change_dir(self) -> None:
        self.curr_dir = self.dir_combo_box.currentText()
    
    def add_new_sprite(self) -> None:
        """
        Creates a new window that allows the user to create a new sprite
        """
        if self.curr_animation:
            new_sprite_window = QtWidgets.QDialog()
            new_sprite_ui = NewSpriteDialog()
            new_sprite_ui.setupUi(new_sprite_window)
            new_sprite_window.exec_()

            # new_sprite_window.new_sprite_image_combobox
            # new_sprite_window.new_sprite_custom_img_textbox
            # new_sprite_window.new_sprite_description_textbox
            # new_sprite_window.new_sprite_x_coord_textbox
            # new_sprite_window.new_sprite_y_coord_textbox
            # new_sprite_window.new_sprite_width_textbox
            # new_sprite_window.new_sprite_height_textbox
            # new_sprite_window.add_sprite_btn


        # link add_sprite_btn to add_sprite_to_current_frame method
        #TODO:

    def change_background_color(self) -> None:
        """
        Changes the background color of the window
        """
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            self.graphicsView.setBackgroundBrush(color)
            MainWindow.setStyleSheet(f"background-color: {color.name()}")

    def __get_gani_file(self):
        """
        Displays a QFileDialog to get a gani file
        """
        file = QtWidgets.QFileDialog.getOpenFileName(None, "Open Gani File", os.path.normpath('E:\Downloads\ganis\ganis'), "Gani Files (*.gani)")
        return file[0]

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    MainWindow = QtWidgets.QMainWindow()
    ui = Animator_GUI(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())