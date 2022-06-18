from PyQt5 import QtCore, QtGui, QtWidgets
from ui import Ui_MainWindow
from new_sprite_ui import Ui_Dialog as NewSpriteDialog
from animation import Animation
from scene import AniGraphicsView
from draggable import DragImage, DragSpriteView
from PIL import Image
from tempfile import TemporaryDirectory
import sys
import os


class Animator_GUI(Ui_MainWindow):
    def __init__(self, MainWindow) -> None:
        super().__init__()
        super().setupUi(MainWindow)
        self.__init_graphics_view()

        self.configs = {}
        self.__load_configs()

        self.curr_dir = "down"
        self.__curr_animation = None
        self.curr_frame = 0
        self.curr_sprite = None
        self.sprite_images = {}  # index: QPixmap

        # link bg_color_btn to change_background_color method
        self.bg_color_btn.clicked.connect(self.__change_background_color)

        # link self.plus_sprite_btn to add_new_sprite method
        self.plus_sprite_btn.clicked.connect(self.__add_new_sprite)

        # link dir_combo_box to change_dir method
        self.dir_combo_box.currentIndexChanged.connect(self.__change_dir)
        # set scroll bar to "down" to start
        self.dir_combo_box.setCurrentIndex(2)

        # link new_btn to new_animation method
        self.new_btn.clicked.connect(self.__new_animation)

        # link save_btn to save_animation method
        self.save_btn.clicked.connect(self.__save_animation)

        # link saveas_btn to save_animation_as method
        self.saveas_btn.clicked.connect(self.__save_animation_as)

        # link reverse_btn to reverse_frames method
        self.reverse_btn.clicked.connect(self.__reverse_frames)

        # link open_btn to new_animation method
        self.open_btn.clicked.connect(lambda: self.__new_animation(from_file=True))

        # link scroll wheel to wheelEvent method
        self.__graphics_view.wheelEvent = self.__do_wheel_event

    def __init_graphics_view(self):
        self.__graphics_view = AniGraphicsView(self.centralwidget, -32, 32, 1.5)
        self.__graphics_view.setObjectName("graphicsView")
        self.horizontalLayout_3.insertWidget(1, self.__graphics_view)
        self.horizontalLayout_3.setStretch(0, 2)
        self.horizontalLayout_3.setStretch(1, 10)
        self.horizontalLayout_3.setStretch(2, 1)
        self.__prepare_graphics_view()

    def __prepare_graphics_view(self):
        self.__graphics_view.scene.clear()
        self.__graphics_view.scene.addLine(0, -100000, 0, 100000)
        self.__graphics_view.scene.addLine(-100000, 0, 100000, 0)

    # setup scroll wheel events for the graphics view
    def __do_wheel_event(self, event):
        if event.angleDelta().y() > 0:
            if self.__graphics_view.transform().m11() < 3: self.__graphics_view.scale(1.1, 1.1)
        else:
            if self.__graphics_view.transform().m11() > 0.4: self.__graphics_view.scale(1 / 1.1, 1 / 1.1)

        event.accept()

    def display_current_frame(self) -> None:
        if len(self.sprite_images) == 0:
            self.__load_sprites_from_ani()
        if self.__curr_animation:
            self.__prepare_graphics_view()
            for sprite, x, y in self.__curr_animation.frames[self.curr_frame].frame_parts[self.curr_dir].list_of_sprites:
                self.__graphics_view.scene.addItem(DragImage(self, sprite, x, y))

    def __load_sprites_from_ani(self):
        def find_image(image_name):
            # TODO if GameFolder in config does not exist, prompt user to enter their game folder path
            for root, dirs, files in os.walk(self.configs["GameFolder"]):
                for file in files:
                    if file.split(".")[0].lower() == image_name or file.lower() == image_name:
                        return os.path.join(root, file)
            image_name = image_name.upper()
            if image_name == "SPRITES":
                return find_image("sprites.png")
            elif image_name == "SHIELD":
                return find_image(self.__curr_animation.attrs['shield'])
            elif image_name == "BODY":
                return find_image(self.__curr_animation.attrs['body'])
            elif image_name == "HEAD":
                return find_image(self.__curr_animation.attrs['head'])
            elif image_name == "ATTR1":
                return find_image(self.__curr_animation.attrs['attr1'])
            elif image_name == "ATTR2":
                return find_image(self.__curr_animation.attrs['attr2'])
            elif image_name == "ATTR3":
                return find_image(self.__curr_animation.attrs['attr3'])
            elif image_name == "ATTR12":
                return find_image(self.__curr_animation.attrs['attr12'])
            elif image_name == "PARAM1":
                return find_image(self.__curr_animation.attrs['param1'])
            elif image_name == "PARAM2":
                return find_image(self.__curr_animation.attrs['param2'])
            elif image_name == "PARAM3":
                return find_image(self.__curr_animation.attrs['param3'])

        if self.__curr_animation:
            with TemporaryDirectory() as tempdir:
                for sprite in self.__curr_animation.sprites:
                    image_path = find_image(sprite.image)
                    if image_path:
                        image = Image.open(image_path)
                        image = image.crop((sprite.x, sprite.y, sprite.x + sprite.width, sprite.y + sprite.height))
                        # TODO add stretch effects, rotation effects, color effects.
                        image.save(os.path.join(tempdir, f"{sprite.index}.png"))
                        self.sprite_images[sprite.index] = QtGui.QPixmap(os.path.join(tempdir, f"{sprite.index}.png"))
                    else:
                        self.sprite_images[sprite.index] = QtGui.QPixmap(sprite.width, sprite.height)

    def __load_configs(self) -> None:
        with open("./config.txt", "r") as f:
            for line in f:
                key, val = line.split("=")
                self.configs[key] = val.strip()

    def __new_animation(self, from_file=False) -> None:
        if from_file:
            # display a QFileDialog to get the file name
            file = self.__get_gani_file()
            if file.endswith(".gani"):
                self.__curr_animation = Animation(from_file=file)
        else:
            self.__curr_animation = Animation()
        self.display_current_frame()
        self.__init_scroll_area()

    def __init_scroll_area(self) -> None:
        """
        Populate the scroll area with the current animation's sprites
        """
        if self.__curr_animation:
            self.sprite_scroll_area.setWidget(QtWidgets.QWidget())
            self.sprite_scroll_area.widget().setLayout(QtWidgets.QVBoxLayout())
            for index, image in self.sprite_images.items():
                im_view = DragSpriteView(self, image, index, self.__curr_animation.sprites)

                im_view.mouseReleaseEvent = lambda e, i=index: self.__add_sprite_to_frame_part(i)

    def __add_sprite_to_frame_part(self, index: int) -> None:
        if self.__curr_animation:
            self.curr_sprite = [sprite for sprite in self.__curr_animation.sprites if sprite.index == index][0].copy()
            # map cursor coordinates to the graphics view scene rectangle
            viewPoint = self.__graphics_view.mapFromGlobal(QtGui.QCursor.pos())
            scenePoint = self.__graphics_view.mapToScene(viewPoint)

            # add sprite to the current frame part
            self.__get_current_frame_part().add_sprite_xs_ys(
                (self.curr_sprite, scenePoint.x() - (self.curr_sprite.width / 2),
                 scenePoint.y() - (self.curr_sprite.height / 2)))
            self.display_current_frame()

    def set_curr_sprite(self, index: int) -> None:
        """
        Set the current sprite to the sprite with the given index
        If there are duplicate sprites on the canvas, it grabs the top one
        """
        self.curr_sprite = [sprite for sprite, x, y in self.__get_current_frame_part().list_of_sprites[::-1] if sprite.index == index][0]

    def __get_current_frame_part(self):
        return self.__get_current_frame().frame_parts[self.curr_dir]

    def __get_current_frame(self):
        return self.__curr_animation.frames[self.curr_frame]

    def __reverse_frames(self) -> None:
        if self.__curr_animation:
            pass

    def __save_animation_as(self) -> None:
        if self.__curr_animation:
            pass

    def __save_animation(self) -> None:
        if self.__curr_animation:
            pass

    def __change_dir(self) -> None:
        self.curr_dir = self.dir_combo_box.currentText().lower()
        self.display_current_frame()

    def __add_new_sprite(self) -> None:
        """
        Creates a new window that allows the user to create a new sprite
        """
        if self.__curr_animation:
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
        # TODO:

    def __change_background_color(self) -> None:
        """
        Changes the background color of the window
        """
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            self.__graphics_view.setBackgroundBrush(color)
            MainWindow.setStyleSheet(f"background-color: {color.name()}")

    def __get_gani_file(self):
        """
        Displays a QFileDialog to get a gani file
        """
        file = QtWidgets.QFileDialog.getOpenFileName(None, "Open Gani File",
                                                     os.path.normpath('E:\Downloads\ganis\ganis'),
                                                     "Gani Files (*.gani)")
        return file[0]


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    MainWindow = QtWidgets.QMainWindow()
    ui = Animator_GUI(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
