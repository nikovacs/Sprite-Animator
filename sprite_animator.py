import os
import sys
import threading
import time
import requests
from PyQt5 import QtCore, QtGui, QtWidgets
from animation import Animation
from sprite import Sprite
from draggable import DragImage, DragSpriteView, SfxImage
from new_sprite_ui import Ui_Dialog as NewSpriteDialog
from scene import AniGraphicsView
from ui import Ui_MainWindow
from NewSpriteDialog import NewSpriteDialog
import pygame

__version__ = "v.0.2.0-alpha"

class Animator_GUI(Ui_MainWindow):
    def __init__(self, MainWindow) -> None:
        super().__init__()
        super().setupUi(MainWindow)
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Animation Editor"))
        self.MainWindow = MainWindow

        self.__check_for_update()
        self.__init_graphics_view()

        self.__init_vars()
        self.file_path_map = {} # not in init method because I want it to persist as long as the program is open
        self.curr_file = ""

        btns = self.enable_disable_buttons(False)

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
        MainWindow.keyPressEvent = self.key_press_event
        self.__graphics_view.keyPressEvent = self.key_press_event
        for btn in btns: btn.keyPressEvent = self.key_press_event

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
        self.__listen = False  # while loading the gani, some events are triggered, but we do not want to listen to them yet.
        self.selected_sprite_combo.currentIndexChanged.connect(self.__do_sprite_combo_changed_event)

        # link length textbox
        self.length_textbox.setValidator(QtGui.QDoubleValidator(0.05, 100000, 2))
        self.length_textbox.returnPressed.connect(lambda: self.__set_frame_length(float(self.length_textbox.text())))

        # link loop, continuous, and singledir checkboxes
        self.loop_checkbox.stateChanged.connect(self.__do_loop_checkbox_changed_event)
        self.continuous_checkbox.stateChanged.connect(self.__do_continuous_checkbox_changed_event)
        self.singledir_checkbox.stateChanged.connect(self.__do_singledir_checkbox_changed_event)

        # link play and stop buttons
        self.play_btn.clicked.connect(self.__play_animation)
        self.stop_btn.clicked.connect(self.__stop_animation)

        # link frame slider
        self.frame_slider.valueChanged.connect(self.__do_frame_slider_changed_event)

        # link plus frame and minus frame
        self.plus_frame_btn.clicked.connect(self.__add_frame)
        self.minus_frame_btn.clicked.connect(self.__remove_frame)

        # link copy button
        self.copy_btn.clicked.connect(self.__copy_frame)

        # link paste buttons
        self.paste_left_btn.clicked.connect(lambda: self.__paste_frame("left"))
        self.paste_right_btn.clicked.connect(lambda: self.__paste_frame("right"))

        # link ani attrs
        self.def_head_textbox.returnPressed.connect(lambda: self.__set_attr("head", self.def_head_textbox.text().strip()))
        self.def_body_textbox.returnPressed.connect(lambda: self.__set_attr("body", self.def_body_textbox.text().strip()))
        self.def_attr1_textbox.returnPressed.connect(lambda: self.__set_attr("attr1", self.def_attr1_textbox.text().strip()))
        self.def_attr2_textbox.returnPressed.connect(lambda: self.__set_attr("attr2", self.def_attr2_textbox.text().strip()))
        self.def_attr3_textbox.returnPressed.connect(lambda: self.__set_attr("attr3", self.def_attr3_textbox.text().strip()))
        self.def_attr12_textbox.returnPressed.connect(lambda: self.__set_attr("attr12", self.def_attr12_textbox.text().strip()))
        self.param1_textbox.returnPressed.connect(lambda: self.__set_attr("param1", self.param1_textbox.text().strip()))
        self.param2_textbox.returnPressed.connect(lambda: self.__set_attr("param2", self.param2_textbox.text().strip()))
        self.param3_textbox.returnPressed.connect(lambda: self.__set_attr("param3", self.param3_textbox.text().strip()))

        # link sound textbox
        self.sound_textbox.returnPressed.connect(lambda: self.__set_sfx(self.sound_textbox.text().strip()))

        # link sound button
        self.plus_sound_btn.clicked.connect(lambda: self.__add_sfx())

        # link edit script button
        self.edit_script_btn.clicked.connect(self.__edit_script)
    
    def __check_for_update(self):
        """
        Checks if there is an update available.
        """
        try:
            response = requests.get("https://api.github.com/repos/nikovacs/sprite-animator/releases/latest")
            if response.status_code == 200:
                version = response.json()["name"]
                if version != __version__:
                    message_box = QtWidgets.QMessageBox()
                    message_box.setWindowTitle("Sprite Animator - Update Available")
                    message_box.setTextFormat(QtCore.Qt.RichText)
                    message_box.setText(f"<b>Sprite Animator</b> has been updated to version <b>{version}</b>!<br>" \
                                "Download <a href='https://github.com/nikovacs/sprite-animator/releases/latest'>here</a>.")
                    message_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
                    message_box.exec_()
        except:
            QtWidgets.QMessageBox.warning(None, "Sprite Animator - Error", "Could not check for updates.")

    def __edit_script(self):
        """
        Opens a script editor window using Plain Text Edit widget
        """
        editor = QtWidgets.QPlainTextEdit()
        editor.setPlainText(self.curr_animation.script if self.curr_animation.script else "")
        editor.setWindowTitle("Edit Script")
        editor.resize(600, 400)
        font = editor.font()
        font.setPointSize(14)
        editor.setFont(font)
        editor.show()
        editor.textChanged.connect(lambda: self.curr_animation.set_script(editor.toPlainText()))
        # wait for the editor to close
        while editor.isVisible():
            QtWidgets.QApplication.processEvents()

    def __add_sfx(self):
        self.sound_textbox.setText("")
        self.get_current_frame().add_sfx()
        self.last_sfx_num = -1
        self.__display_current_frame()

    def __set_sfx(self, sfx):
        print(self.last_sfx_num)
        if self.curr_animation and isinstance(self.last_sfx_num, int):
            self.get_current_frame().set_sfx(sfx, self.last_sfx_num)
            self.__display_current_frame()

    def __clear_sfx_textbox(self) -> None:
        self.sound_textbox.setText("")

    def update_sfx_textbox(self, sfx_num: int) -> None:
        if self.curr_animation:
            self.sound_textbox.setText(self.get_current_frame().sfxs[sfx_num][0])

    def __set_attr(self, attr: str, value: str) -> None:
        if self.curr_animation:
            self.curr_animation.set_attr(attr, value)
            self.__update_attr_image(attr)
            self.__display_current_frame()

    def __paste_frame(self, direction) -> None:
        """
        @param direction: "left" or "right"
        """
        if self.__clipboard is None: return
        direction = direction.lower()
        if self.curr_animation:
            self.curr_animation.add_new_frame(self.curr_frame, direction, self.__clipboard)
            if direction == "right":
                self.curr_frame += 1
            self.__display_current_frame()

    def __copy_frame(self):
        if self.curr_animation:
            self.__clipboard = self.get_current_frame()

    def __add_frame(self) -> None:
        if self.curr_animation:
            self.curr_animation.add_new_frame(self.curr_frame)
            self.curr_frame += 1
            self.__display_current_frame()

    def __remove_frame(self) -> None:
        if self.curr_animation:
            num_frames = self.__ani_length
            self.curr_animation.remove_frame(self.curr_frame)
            if not num_frames - 1 > self.curr_frame:
                self.curr_frame -= 1
            self.__display_current_frame()

    def __init_vars(self):
        # pygame being used for playing .wav files
        pygame.init()
        pygame.mixer.init()

        self.play = False
        self.__play_thread = None
        self.curr_dir = "down"
        self.curr_animation = None
        self.curr_frame = 0
        self.curr_sprite = None  # int (layer in the current frame part) a.k.a. index in the FramePart list
        # acts as an index in an iterable. Ex. -1 can mean upper-most layer
        self.sprite_images = {}  # index: QPixmap
        self.sprite_offsets = {}  # index: (x_offset, y_offset) for adjusted sprite images which are no longer their original sizes
        self.__sfx_dict = {}  # {sfx_file.wav: pygame.mixer.Sound)}
        self.__clipboard = None
        self.time_label.setText("0.00")
        self.__listen = False
        self.last_sfx_num = None

    @property
    def __ani_length(self) -> int:
        return len(self.curr_animation.frames)

    def __do_frame_slider_changed_event(self) -> None:
        if self.__listen:
            self.curr_frame = self.frame_slider.value()
            timer_val = sum([self.curr_animation.frames[i].length for i in range(self.curr_frame + 1)])
            self.time_label.setText(f"{timer_val:.2f}")
            self.curr_frame = self.frame_slider.value()
            self.__display_current_frame()

    def __set_frame_slider(self) -> None:
        if self.__ani_length-1 != self.frame_slider.maximum():
            self.__set_frame_slider_max()
        self.frame_slider.setValue(self.curr_frame)

    def __set_frame_slider_max(self) -> None:
        self.frame_slider.setMaximum(self.__ani_length - 1)
    
    def __stop_animation(self) -> None:
        self.play = False
        self.__play_thread = None
    
    def __play_animation(self) -> None:
        def overwrite_thread(parent):
            parent.__play_thread = None
        if self.play: return
        self.__play_thread = RunAniWorker(self)
        self.__play_thread.update_screen_signal.connect(self.__display_current_frame)
        self.play = True
        self.__play_thread.start()
        self.__play_thread.finished.connect(lambda: overwrite_thread(self))

    def __do_loop_checkbox_changed_event(self) -> None:
        if self.curr_animation and self.__listen:
            self.curr_animation.is_loop = self.loop_checkbox.isChecked()
            if self.loop_checkbox.isChecked():
                self.continuous_checkbox.setChecked(False)
                self.curr_animation.is_continuous = False
            
    def __do_continuous_checkbox_changed_event(self) -> None:
        if self.curr_animation and self.__listen:
            self.curr_animation.is_continuous = self.continuous_checkbox.isChecked()
            if self.continuous_checkbox.isChecked():
                self.loop_checkbox.setChecked(False)
                self.curr_animation.is_loop = False

    def __do_singledir_checkbox_changed_event(self) -> None:
        if self.curr_animation and self.__listen:
            self.curr_animation.toggle_single_dir()
            self.__play = False
            self.curr_frame = 0
            self.__display_current_frame()

    def __set_frame_length(self, length: int or float) -> None:
        if self.curr_animation:
            length = round(length, 2)
            length = round(length / 0.05) * 0.05
            if length < 0.05: length = 0.05
            self.length_textbox.setText(str(length))
            self.get_current_frame().set_length(length)

    def __do_sprite_combo_changed_event(self):
        if self.__listen:
            self.set_curr_sprite(self.selected_sprite_combo.currentIndex())
            self.__update_sprite_textboxes()

    def enable_disable_buttons(self, enable: bool) -> list:
        """
        This method enables/disables all the buttons/other widgets in the GUI.
        It alsos serves as an easy way to retrieve all the widgets in the GUI 
        that we want to change the keyPressEvent of, so we return those widgets.
        @param enable: True to enable, False to disable
        """
        lst_btns = [
            self.edit_script_btn,
            self.plus_sound_btn,
            self.save_btn,
            self.saveas_btn,
            self.plus_sprite_btn,
            self.reverse_btn,
            self.plus_layer_btn,
            self.minus_layer_btn,
            self.plus_x_btn,
            self.minus_x_btn,
            self.plus_y_btn,
            self.minus_y_btn,
            self.play_btn,
            self.stop_btn,
            self.plus_frame_btn,
            self.minus_frame_btn,
            self.copy_btn,
            self.paste_left_btn,
            self.paste_right_btn,
            self.frame_slider,
            self.continuous_checkbox,
            self.singledir_checkbox,
            self.dir_combo_box,
            self.selected_sprite_combo,
            self.loop_checkbox,
        ]

        others = [ # elements that we do not want to change the keyPressEvent of
            self.x_textbox,
            self.y_textbox,
            self.selected_sprite_text,
            self.length_textbox,
            self.setbackto_textbox,
            self.def_head_textbox,
            self.def_body_textbox,
            self.def_attr1_textbox,
            self.def_attr2_textbox,
            self.def_attr3_textbox,
            self.def_attr12_textbox,
            self.param1_textbox,
            self.param2_textbox,
            self.param3_textbox,
            self.sound_textbox,
        ]

        [btn.setEnabled(enable) for btn in lst_btns]
        [other.setEnabled(enable) for other in others]

        # these buttons are not yet implemented
        self.import_btn.setEnabled(False)
        self.minus_unused_btn.setEnabled(False)
        self.undo_btn.setEnabled(False)
        self.redo_btn.setEnabled(False)

        return lst_btns  # return the things we want to change the keyPressEvent of

    def __init_graphics_view(self):
        self.__graphics_view = AniGraphicsView(self.centralwidget, -24, 0, 2)
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
        self.__graphics_view.scene.addLine(0, 49, 49, 49)
        self.__graphics_view.scene.addLine(49, 0, 49, 49)

    def __do_change_layer(self, direction: str) -> None:
        if self.__sprites_exist() and self.get_current_frame_part().change_layer(self.curr_sprite, direction):
            if direction.lower() == "up":
                self.curr_sprite += 1
            else:
                self.curr_sprite -= 1
            self.__display_current_frame()

    # setup scroll wheel events for the graphics view
    def __do_wheel_event(self, event):
        if event.angleDelta().y() > 0:
            if self.__graphics_view.transform().m11() < 15: self.__graphics_view.scale(1.1, 1.1)
        else:
            if self.__graphics_view.transform().m11() > 0.75: self.__graphics_view.scale(1 / 1.1, 1 / 1.1)
        event.accept()

    def __delete_curr_sprite(self) -> None:
        if self.curr_animation and self.curr_sprite is not None and self.curr_sprite >= 0:
            self.get_current_frame_part().list_of_sprites.pop(self.curr_sprite)
            self.curr_sprite = -1 if len(self.get_current_frame_part().list_of_sprites) > 0 else None
            self.__display_current_frame()

    def key_press_event(self, event) -> None:
        if not self.curr_animation or not self.__sprites_exist(): return
        if event.key() == QtCore.Qt.Key_Delete or event.key() == QtCore.Qt.Key_Backspace:
            self.__delete_curr_sprite()
            return
        if event.key() == QtCore.Qt.Key_PageUp:
            self.set_curr_sprite(self.curr_sprite + 1)
            return
        if event.key() == QtCore.Qt.Key_PageDown:
            self.set_curr_sprite(self.curr_sprite - 1)
            return
        if event.key() == QtCore.Qt.Key_Space:
            if self.play: 
                self.play = False
            else:
                self.__play_animation()
            return

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
        if not self.__sprites_exist(): return
        self.get_current_frame_part().shift(self.curr_sprite, direction, amount)
        self.__display_current_frame()

    def __sprites_exist(self) -> bool:
        return len(self.get_current_frame_part().list_of_sprites) > 0

    def  __update_sprite_textboxes(self) -> None:
        if not self.__sprites_exist(): return
        self.__listen = False
        self.__correct_current_sprite()
        self.x_textbox.setText(str(self.get_current_frame_part().list_of_sprites[self.curr_sprite][1]))  # TODO consider making these named tuples to avoid indexing
        self.y_textbox.setText(str(self.get_current_frame_part().list_of_sprites[self.curr_sprite][2]))
        self.selected_sprite_text.setText(str(self.curr_sprite))
        self.selected_sprite_combo.clear()
        self.selected_sprite_combo.addItems([f"{i}: {sprite.desc}" for i, (sprite, _, _) in enumerate(self.get_current_frame_part().list_of_sprites)])
        self.selected_sprite_combo.setCurrentIndex(self.curr_sprite)
        self.__listen = True
        self.length_textbox.setText(f"{self.get_current_frame().length:.2f}")

    def __correct_current_sprite(self):
        """
        # curr_sprite must be something like -1, so we should convert it to the correct index for display
        """
        if self.curr_sprite is None and self.__sprites_exist(): 
            self.curr_sprite = -1 
        else: 
            return

        if not 0 <= self.curr_sprite < len(self.get_current_frame_part().list_of_sprites):
            if self.curr_sprite < 0:
                self.curr_sprite = len(self.get_current_frame_part().list_of_sprites) + self.curr_sprite

    def __set_sprite_location(self, x=None, y=None) -> None:
        if not self.__sprites_exist(): return
        self.get_current_frame_part().change_sprite_xs_ys(self.curr_sprite, x, y)
        self.__display_current_frame()

    def __display_current_frame(self) -> None:
        if self.curr_animation:
            if self.get_current_frame().sfxs:
                for sfx, _, _ in self.get_current_frame().sfxs:
                    if sfx not in self.__sfx_dict:
                        self.__load_sfx_from_ani()
            self.curr_sprite = self.curr_sprite if self.curr_sprite is None or 0 <= self.curr_sprite < len(self.get_current_frame_part().list_of_sprites) else -1
            self.__correct_current_sprite()
            self.__prepare_graphics_view()
            for i, (sprite, x, y) in enumerate(self.get_current_frame_part().list_of_sprites):
                offsets = self.sprite_offsets.get(sprite.index)
                x_offset, y_offset = offsets if offsets else (0, 0)
                self.__graphics_view.scene.addItem(DragImage(self, sprite, i, x, y, x_offset, y_offset))
            for i, (sfx, x, y) in enumerate(self.get_current_frame().sfxs):
                self.__graphics_view.scene.addItem(SfxImage(self, sfx, self.__sfx_dict.get(sfx, None), x, y, i))
            self.__update_sprite_textboxes()
            self.__set_frame_slider()
            self.__play_frame_sfx()
            self.__clear_sfx_textbox()

    def change_sfx_pos(self, sfx_index: int, x: int, y: int) -> None:
        self.get_current_frame().change_sfx_pos(sfx_index, x, y)
        self.__display_current_frame()

    def delete_sfx(self, sfx_index: int) -> None:
        self.get_current_frame().delete_sfx(sfx_index)
        self.__display_current_frame()
    
    def add_sprite_to_scroll_area(self, sprite: Sprite) -> None:
        self.curr_animation.add_sprite(sprite)
        pixmap, x_offset, y_offset = NewSpriteDialog.load_and_crop_sprite(self.file_path_map[sprite.index], sprite)
        self.sprite_offsets[sprite.index] = (x_offset, y_offset)
        self.sprite_images[sprite.index] = pixmap
        self.__init_scroll_area()

    def __play_frame_sfx(self) -> None:
        if sfxs := self.get_current_frame().sfxs:
            for sfx, _, _ in sfxs:
                if pygame_sfx := self.__sfx_dict.get(sfx, None):
                    pygame_sfx.play()

    def __update_attr_image(self, attr: str) -> None:
        attr = attr.upper()
        sprites = [sprite for sprite in self.curr_animation.sprites if sprite.image == attr]
        for sprite in sprites:
            pixmap, x_offset, y_offset = NewSpriteDialog.load_and_crop_sprite(self.find_file(sprite.image), sprite)
            self.sprite_offsets[sprite.index] = (x_offset, y_offset)
            self.sprite_images[sprite.index] = pixmap

    def __load_sfx_from_ani(self) -> None:
        if self.curr_animation:
            for frame in self.curr_animation.frames:
                for sfx, x, y in frame.sfxs:
                    if sfx and sfx not in self.__sfx_dict.keys():
                        sfx_path = self.find_file(sfx)
                        self.__sfx_dict[sfx] = pygame.mixer.Sound(sfx_path) if sfx_path else None

    def __load_sprites_from_ani(self):
        if self.curr_animation and len(self.curr_animation.sprites) > 0:
            threads = []
            for sprite in self.curr_animation.sprites:
                thread = QtCore.QThread(None)
                thread.run = lambda s=sprite: self.__load_sprites_from_ani_helper(s)
                threads.append(thread)
                thread.start()
            [thread.wait() for thread in threads]

            #     threads.append(threading.Thread(target=lambda s=sprite: self.__load_sprites_from_ani_helper(s)))
            # [thread.start() for thread in threads]
            # [thread.join() for thread in threads]

    def __load_sprites_from_ani_helper(self, sprite):
        image_path = self.find_file(sprite.image)
        pixmap, x_offset, y_offset = NewSpriteDialog.load_and_crop_sprite(image_path, sprite)
        if x_offset or y_offset:
            self.sprite_offsets[sprite.index] = (x_offset, y_offset)
        self.sprite_images[sprite.index] = pixmap

    def find_file(self, file_name: str):
        if file_name in self.file_path_map:
            return self.file_path_map[file_name]
        for root, dirs, files in os.walk(r"C:\Users\kovac\Graal"):
            for file in files:
                if (file.split(".")[0].lower() == file_name or file.lower() == file_name) and not file.lower().endswith((".gani", ".txt")):
                    self.file_path_map[file_name] = os.path.join(root, file)
                    return os.path.join(root, file)
        file_name = file_name.upper()  # TODO: make these already be in self.file_path_map from start.
        if file_name == "SPRITES":
            return self.find_file("sprites.png")
        elif file_name == "SHIELD":
            return self.find_file(self.curr_animation.attrs['shield'])
        elif file_name == "BODY":
            return self.find_file(self.curr_animation.attrs['body'])
        elif file_name == "HEAD":
            return self.find_file(self.curr_animation.attrs['head'])
        elif file_name == "ATTR1":
            return self.find_file(self.curr_animation.attrs['attr1'])
        elif file_name == "ATTR2":
            return self.find_file(self.curr_animation.attrs['attr2'])
        elif file_name == "ATTR3":
            return self.find_file(self.curr_animation.attrs['attr3'])
        elif file_name == "ATTR12":
            return self.find_file(self.curr_animation.attrs['attr12'])
        elif file_name == "PARAM1":
            return self.find_file(self.curr_animation.attrs['param1'])
        elif file_name == "PARAM2":
            return self.find_file(self.curr_animation.attrs['param2'])
        elif file_name == "PARAM3":
            return self.find_file(self.curr_animation.attrs['param3'])

    def __new_animation(self, from_file=False) -> None:
        old_file = ""
        if self.curr_file: 
            old_file = self.curr_file
        if from_file:
            # display a QFileDialog to get the file name
            file = self.__get_gani_file()
            print("file:",file)
            if file.endswith(".gani"):
                self.curr_file = file
                self.__init_vars()
                self.curr_animation = Animation(from_file=file)
        else:
            self.curr_file = ""
            self.__init_vars()
            self.curr_animation = Animation()

        if self.curr_animation and old_file != self.curr_file:
            self.__load_sprites_from_ani()
            self.enable_disable_buttons(True)
            self.__set_frame_slider_max()
            self.__set_animation_textboxes()
            self.__set_animation_checkboxes()
            self.__load_sfx_from_ani()
            self.__init_scroll_area()
            self.__display_current_frame()
            self.dir_combo_box.setCurrentIndex(2)
            self.__listen = True

    def __set_animation_checkboxes(self) -> None:
        self.loop_checkbox.setChecked(self.curr_animation.is_loop)
        self.singledir_checkbox.setChecked(self.curr_animation.is_single_dir)
        self.continuous_checkbox.setChecked(self.curr_animation.is_continuous)

    def __set_animation_textboxes(self) -> None:
        if self.curr_animation:
            self.setbackto_textbox.setText(self.curr_animation.setbackto)
            self.def_head_textbox.setText(self.curr_animation.attrs['head'])
            self.def_body_textbox.setText(self.curr_animation.attrs['body'])
            self.def_attr1_textbox.setText(self.curr_animation.attrs['attr1'])
            self.def_attr2_textbox.setText(self.curr_animation.attrs['attr2'])
            self.def_attr3_textbox.setText(self.curr_animation.attrs['attr3'])
            self.def_attr12_textbox.setText(self.curr_animation.attrs['attr12'])
            self.param1_textbox.setText(self.curr_animation.attrs['param1'])
            self.param2_textbox.setText(self.curr_animation.attrs['param2'])
            self.param3_textbox.setText(self.curr_animation.attrs['param3'])

    def __init_scroll_area(self) -> None:
        """
        Populate the scroll area with the current animation's sprites
        """
        if self.curr_animation:
            self.sprite_scroll_area.setWidget(QtWidgets.QWidget())
            self.sprite_scroll_area.widget().setLayout(QtWidgets.QVBoxLayout())

            for index, image in sorted(self.sprite_images.items(), key=lambda x: x[0]):
                im_view = DragSpriteView(self, image, index, self.curr_animation.sprites)
                im_view.mouseReleaseEvent = lambda e, i=index: self.__drag_sprite_view_mouse_event(e, i)

    def __drag_sprite_view_mouse_event(self, event, i) -> None:
        # make sure the event is a left mouse release event
        if event.button() == QtCore.Qt.LeftButton:
            self.__add_sprite_to_frame_part(i)

    def __add_sprite_to_frame_part(self, index: int) -> None:
        """
        Add a sprite to the current frame part on the top layer
        """
        if self.curr_animation:
            # map cursor coordinates to the graphics view scene rectangle
            viewPoint = self.__graphics_view.mapFromGlobal(QtGui.QCursor.pos())
            scenePoint = self.__graphics_view.mapToScene(viewPoint)

            sprite_to_add = None
            for sprite in self.curr_animation.sprites:
                if sprite.index == index:
                    sprite_to_add = sprite
                    break

            # add sprite to the current frame part
            sprite_tuple = (sprite_to_add, round(scenePoint.x() - (sprite_to_add.width / 2)),
                            round(scenePoint.y() - (sprite_to_add.height / 2)))
            self.get_current_frame_part().add_sprite_xs_ys(sprite_tuple)
            self.set_curr_sprite(-1)
            self.__correct_current_sprite()
            self.__display_current_frame()

    def set_curr_sprite(self, layer: int) -> None:
        """
        Set the current sprite to the sprite with the given layer# (bottom is 0)
        Important to specify this way instead of Sprite is Sprite because there can be duplicate sprites
        on the same frame part in different locations.
        """
        if 0 <= layer < len(self.get_current_frame_part().list_of_sprites):
            self.curr_sprite = layer
            self.__update_sprite_textboxes()

    def delete_sprite(self, sprite: Sprite) -> None:
        """
        Delete the provided sprite from the sprite scroll area and animation
        """
        if self.curr_animation:
            self.curr_animation.delete_sprite(sprite)
            del self.sprite_images[sprite.index]
            if sprite.index in self.sprite_offsets:
                del self.sprite_offsets[sprite.index]
            self.__init_scroll_area()
            self.__display_current_frame()

    def edit_sprite(self, sprite: Sprite) -> None:
        """
        Edit the provided sprite in the sprite scroll area and animation
        """
        if self.curr_animation:
            self.__add_new_sprite(sprite)

    def get_current_frame_part(self):
        """
        Gets the current frame part with respect to the current value of self.curr_dir
        """
        return self.get_current_frame().frame_parts[self.curr_dir]

    def get_current_frame(self):
        """
        Gets the current frame with respect to the current value of self.curr_frame
        """
        return self.curr_animation.frames[self.curr_frame]

    def __reverse_frames(self) -> None:
        """
        Reverses the order of the frames in the current animation
        """
        if self.curr_animation:
            self.curr_animation.reverse_frames()
            self.__display_current_frame()

    def __save_animation_as(self) -> None:
        if self.curr_animation:
            self.curr_file = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Animation As', '', 'Gani (*.gani)')[0]
            if self.curr_file:
                self.__save_animation()

    def __save_animation(self) -> None:
        if self.curr_animation:
            if self.curr_file:
                self.curr_animation.save(self.curr_file)
            else:
                self.__save_animation_as()

    def __change_dir(self) -> None:
        self.curr_dir = self.dir_combo_box.currentText().lower()
        self.__display_current_frame()

    def __add_new_sprite(self, from_sprite: Sprite) -> None:
        """
        Creates a new window that allows the user to create a new sprite
        """
        if self.curr_animation:
            new_sprite_window = QtWidgets.QDialog()
            NewSpriteDialog(self, new_sprite_window, from_sprite)
            new_sprite_window.exec_()
            self.__display_current_frame()

    def __change_background_color(self) -> None:
        """
        Changes the background color of the window
        """
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            self.__graphics_view.setBackgroundBrush(color)

    def __get_gani_file(self) -> str:
        """
        Displays a QFileDialog to get a gani file
        """
        file = QtWidgets.QFileDialog.getOpenFileName(None, "Open Gani File",
                                                     os.path.normpath('./levels/ganis'), "Gani Files (*.gani)")
        return file[0]


class RunAniWorker(QtCore.QThread):
    update_screen_signal = QtCore.pyqtSignal()

    def __init__(self, parent: Animator_GUI):
        super().__init__()
        self.parent = parent

    def run(self):
        if self.parent.curr_animation:
            while self.parent.play:
                for i in range(len(self.parent.curr_animation.frames)):
                    self.parent.curr_frame = i
                    self.update_screen_signal.emit()
                    if not self.parent.play: return  # allows stopping mid-animation
                    time.sleep(self.parent.get_current_frame().length)
                if not self.parent.curr_animation.is_loop:
                    self.parent.play = False


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    MainWindow = QtWidgets.QMainWindow()
    ui = Animator_GUI(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
