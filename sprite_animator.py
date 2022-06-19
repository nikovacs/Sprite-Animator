from PyQt5 import QtCore, QtGui, QtWidgets
from ui import Ui_MainWindow
from new_sprite_ui import Ui_Dialog as NewSpriteDialog
from animation import Animation
from scene import AniGraphicsView
from draggable import DragImage, DragSpriteView
from sprite import Sprite
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
        self.curr_sprite = -1 # int (layer in the current frame part) a.k.a. index in the FramePart list
        # acts as an index in an iterable. Ex. -1 can mean upper-most layer
        self.sprite_images = {}  # index: QPixmap

        self.enable_disable_buttons(False)

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

        # add arrow key events
        self.__graphics_view.keyPressEvent = self.key_press_event

        # link +/- layer buttons
        self.plus_layer_btn.clicked.connect(lambda: self.__do_change_layer("up"))
        self.minus_layer_btn.clicked.connect(lambda: self.__do_change_layer("down"))

        # link +/- X/Y buttons
        self.plus_x_btn.clicked.connect(lambda: self.shift_sprite("horizontal", 1))
        self.minus_x_btn.clicked.connect(lambda: self.shift_sprite("horizontal", -1))
        self.plus_y_btn.clicked.connect(lambda: self.shift_sprite("Vertical", 1))
        self.minus_y_btn.clicked.connect(lambda: self.shift_sprite("vertical", -1))

        # link x_textbox and y_textbox on enter key press
        self.x_textbox.setValidator(QtGui.QIntValidator(-100000, 100000))
        self.x_textbox.returnPressed.connect(lambda: self.__set_sprite_location(x=int(self.x_textbox.text())))
        self.y_textbox.setValidator(QtGui.QIntValidator(-100000, 100000))
        self.y_textbox.returnPressed.connect(lambda: self.__set_sprite_location(y=int(self.y_textbox.text())))

        # link select_sprite_textbox and combobox
        self.selected_sprite_text.setValidator(QtGui.QIntValidator(-100000, 100000))
        self.selected_sprite_text.returnPressed.connect(lambda: self.set_curr_sprite(int(self.selected_sprite_text.text())))
        # self.selected_sprite_combo.currentIndexChanged.connect(lambda: self.set_curr_sprite(self.selected_sprite_combo.currentIndex()))
        # self.selected_sprite_combo.currentIndexChanged.connect(lambda: print(self.selected_sprite_combo.currentIndex()))

    def enable_disable_buttons(self, enable: bool) -> None:
        self.save_btn.setEnabled(enable)
        self.saveas_btn.setEnabled(enable)
        self.undo_btn.setEnabled(enable)
        self.redo_btn.setEnabled(enable)
        self.plus_sprite_btn.setEnabled(enable)
        self.minus_unused_btn.setEnabled(enable)
        self.import_btn.setEnabled(enable)
        self.reverse_btn.setEnabled(enable)
        self.plus_layer_btn.setEnabled(enable)
        self.minus_layer_btn.setEnabled(enable)
        self.plus_x_btn.setEnabled(enable)
        self.minus_x_btn.setEnabled(enable)
        self.plus_y_btn.setEnabled(enable)
        self.minus_y_btn.setEnabled(enable)
        self.play_btn.setEnabled(enable)
        self.stop_btn.setEnabled(enable)
        self.plus_frame_btn.setEnabled(enable)
        self.minus_frame_btn.setEnabled(enable)
        self.copy_btn.setEnabled(enable)
        self.paste_left_btn.setEnabled(enable)
        self.paste_right_btn.setEnabled(enable)
        self.plus_sound_btn.setEnabled(enable)
        self.x_textbox.setEnabled(enable)
        self.y_textbox.setEnabled(enable)
        self.selected_sprite_text.setEnabled(enable)
        self.length_textbox.setEnabled(enable)
        self.setbackto_textbox.setEnabled(enable)
        self.def_head_textbox.setEnabled(enable)
        self.def_body_textbox.setEnabled(enable)
        self.def_attr1_textbox.setEnabled(enable)
        self.def_attr2_textbox.setEnabled(enable)
        self.def_attr3_textbox.setEnabled(enable)
        self.def_attr12_textbox.setEnabled(enable)
        self.param1_textbox.setEnabled(enable)
        self.param2_textbox.setEnabled(enable)
        self.param3_textbox.setEnabled(enable)
        self.sound_textbox.setEnabled(enable)
        self.loop_checkbox.setEnabled(enable)
        self.continuous_checkbox.setEnabled(enable)
        self.singledir_checkbox.setEnabled(enable)
        self.dir_combo_box.setEnabled(enable)
        self.selected_sprite_combo.setEnabled(enable)
        self.frame_slider.setEnabled(enable)

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

    def __do_change_layer(self, direction: str) -> None:
        changed = self.__get_current_frame_part().change_layer(self.curr_sprite, direction)
        if changed:
            if direction.lower() == "up":
                self.curr_sprite += 1
            else:
                self.curr_sprite -= 1
            self.__display_current_frame()

    # setup scroll wheel events for the graphics view
    def __do_wheel_event(self, event):
        if event.angleDelta().y() > 0:
            if self.__graphics_view.transform().m11() < 3: self.__graphics_view.scale(1.1, 1.1)
        else:
            if self.__graphics_view.transform().m11() > 0.4: self.__graphics_view.scale(1 / 1.1, 1 / 1.1)
        event.accept()

    def key_press_event(self, event):
        direction = None
        amount = None
        if event.key() == QtCore.Qt.Key_Left:
            direction = "horizontal"
            amount = -1
        elif event.key() == QtCore.Qt.Key_Right:
            direction = "horizontal"
            amount = 1
        elif event.key() == QtCore.Qt.Key_Up:
            direction = "vertical"
            amount = -1
        elif event.key() == QtCore.Qt.Key_Down:
            direction = "vertical"
            amount = 1
        if direction:
            self.shift_sprite(direction, amount)

    def shift_sprite(self, direction: str, amount=0) -> None:
        """
        @param direction: "horizontal" or "vertical"
        @param amount: int amount to shift the sprite
        """
        self.__get_current_frame_part().shift(self.curr_sprite, direction, amount)
        self.__display_current_frame()

    def __update_sprite_textboxes(self) -> None:
        self.__correct_current_sprite()
        self.x_textbox.setText(str(self.__get_current_frame_part().get_sprite_by_layer(self.curr_sprite)[1]))  # TODO consider making these named tuples to avoid indexing
        self.y_textbox.setText(str(self.__get_current_frame_part().get_sprite_by_layer(self.curr_sprite)[2]))
        self.selected_sprite_text.setText(str(self.curr_sprite))
        # populate the combo box with the sprites in the current frame
        self.selected_sprite_combo.clear()
        [self.selected_sprite_combo.addItem(f"{i}: {sprite.desc}")
         for i, (sprite, _, _) in enumerate(self.__get_current_frame_part().list_of_sprites)]
        # set the current selection to the current sprite
        self.selected_sprite_combo.setCurrentIndex(self.curr_sprite)

    def __correct_current_sprite(self):
        if not 0 <= self.curr_sprite < len(self.__get_current_frame_part().list_of_sprites):
            # curr_sprite must be something like -1, so we should convert it to the correct index for display
            if self.curr_sprite < 0:
                self.curr_sprite = len(self.__get_current_frame_part().list_of_sprites) + self.curr_sprite

    def __set_sprite_location(self, x=None, y=None) -> None:
        self.__get_current_frame_part().change_sprite_xs_ys(self.curr_sprite, x, y)
        self.__display_current_frame()

    def __display_current_frame(self) -> None:
        if len(self.sprite_images) == 0:
            self.__load_sprites_from_ani()
        if self.__curr_animation:
            self.__prepare_graphics_view()
            for i, (sprite, x, y) in \
                    enumerate(self.__get_current_frame_part().list_of_sprites):
                self.__graphics_view.scene.addItem(DragImage(self, sprite, i, x, y))
            self.__update_sprite_textboxes()

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
        self.__display_current_frame()
        self.__init_scroll_area()

        self.enable_disable_buttons(True)

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
        """
        Add a sprite to the current frame part on the top layer
        """
        if self.__curr_animation:
            # map cursor coordinates to the graphics view scene rectangle
            viewPoint = self.__graphics_view.mapFromGlobal(QtGui.QCursor.pos())
            scenePoint = self.__graphics_view.mapToScene(viewPoint)

            sprite_to_add = [sprite for sprite in self.__curr_animation.sprites if sprite.index == index][0]

            # add sprite to the current frame part
            sprite_tuple = (sprite_to_add, scenePoint.x() - (sprite_to_add.width / 2),
                            scenePoint.y() - (sprite_to_add.height / 2))
            self.__get_current_frame_part().add_sprite_xs_ys(sprite_tuple)
            self.__display_current_frame()
            self.curr_sprite = -1

    def set_curr_sprite(self, layer: int) -> None:
        """
        Set the current sprite to the sprite with the given layer# (bottom is 0)
        Important to specify this way instead of Sprite is Sprite because there can be duplicate sprites
        on the same frame part in different locations.
        """
        if 0 <= layer < len(self.__get_current_frame_part().list_of_sprites):
            self.curr_sprite = layer
            self.__update_sprite_textboxes()

    def __get_current_frame_part(self):
        """
        Gets the current frame part with respect to the current value of self.curr_dir
        """
        return self.__get_current_frame().frame_parts[self.curr_dir]

    def __get_current_frame(self):
        """
        Gets the current frame with respect to the current value of self.curr_frame
        """
        return self.__curr_animation.frames[self.curr_frame]

    def __reverse_frames(self) -> None:
        """
        Reverses the order of the frames in the current animation
        """
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
        self.__display_current_frame()

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
