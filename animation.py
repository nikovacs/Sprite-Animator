from frame import Frame
from sprite import Sprite
import copy
import math

class Animation:
    """
    Animation is the "parent" class that holds all the frames, which hold all the frame parts, which holds all the sprites.
    The order of the frames in the list is the order that they wil be displayed.
    """
    def __init__(self, from_file=None) -> None:
        self.__script = []
        self.__rotate_effects = {} # ex. [index: int, angle: float (in degrees)]
        self.__stretch_x_effects = {}  # ex. {index: int, stretch: float}
        self.__stretch_y_effects = {}
        self.__color_effects = {}  # ex. {index: int, [R,G,B,A]}
        self.__zoom_effects = {}  # ex. (index: int, zoom: float)
        self.__frames = []
        self.__sprites_list = []

        self.is_loop = False
        self.is_continuous = False
        self.is_single_dir = False

        self.__attrs = {
            "head": "head19.png",
            "body": "body.png",
            "shield": "shield1.png",
            "attr1": "hat0.png",
            "attr2": "",
            "attr3": "",
            "attr12": "",
            "param1": "",
            "param2": "",
            "param3": "",
        }
        self.__setbackto = ""

        if not from_file:
            self.__frames.append(Frame())
        if from_file:
            self.__set_attrs_from_existing_ani(from_file)
    
    @property
    def frames(self) -> list:
        return self.__frames
    
    @property
    def sprites(self) -> list:
        return self.__sprites_list

    @property
    def attrs(self) -> dict:
        return self.__attrs

    @property
    def setbackto(self) -> str:
        return self.__setbackto

    def add_sprite(self, sprite: Sprite) -> None:
        self.__sprites_list = [tmp_sprite for tmp_sprite in self.sprites if tmp_sprite.index != sprite.index]
        self.__sprites_list.append(sprite)

    def add_new_frame(self, index: int, direction="right", frame_from_clipboard=None) -> None:
        """
        @param index: the index of the frame to insert the new frame
        @param direction: "left" or "right"
        @param frame_from_clipboard: Frame object to insert
        """
        offset = 1 if direction == "right" else 0
        if not frame_from_clipboard:
            self.__frames.insert(index+offset, Frame())
        else:
            self.__frames.insert(index+offset, copy.deepcopy(frame_from_clipboard))

    def remove_frame(self, index: int) -> None:
        self.__frames.pop(index)

    def __set_attrs_from_existing_ani(self, file):
        # set some default values for parsing flags
        self.__record_ani = False # instance variable because used in helper method
        record_script = False

        with open(file, 'r') as f:
            for line in f:
                line = line.strip().split()
                if len(line) == 0:
                    continue
                    # lines in file are tab delimited
                    # ex. ['SPRITE', '-1000', 'ATTR12', '0', '0', '64', '64', 'backpack']
                if record_script:
                    self.__script.append(line)
                elif line[0].upper() == "PLAYSOUND":
                    self.__frames[-1].set_sfx(' '.join(line[1:2]))
                elif line[0].upper() == "WAIT":
                    self.__frames[-1].set_length((int(line[1])+1) * 0.05)
                    # wait times in ganis are weird....
                    # WAIT = wait as it appears on the gani file (an integer)
                    # length = (WAIT+1) * 0.05
                elif line[0].upper() == "SCRIPT":
                    record_script = True
                elif line[0].upper() == "SCRIPTEND":
                    record_script = False
                elif line[0].upper() == "SETBACKTO":
                    self.__setbackto = line[1] if len(line) > 1 else ""
                elif line[0].upper() == "DEFAULTATTR1":
                    self.__attrs["attr1"] = line[1] if len(line) > 1 else "hat0.png"
                elif line[0].lower() == "DEFAULTHEAD":
                    self.__attrs["head"] = line[1] if len(line) > 1 else "head19.png"
                elif line[0].lower() == "DEFAULTBODY":
                    self.__attrs["body"] = line[1] if len(line) > 1 else "body.png"
                elif line[0].lower() == "DEFAULTSHIELD":
                    self.__attrs["shield"] = line[1] if len(line) > 1 else "shield1.png"
                elif line[0].upper() == "ANI":
                    self.__record_ani = True
                    self.__ani_dir = 0
                elif line[0].upper() == "ANIEND":
                    self.__record_ani = False
                elif line[0].upper() == "SINGLEDIRECTION":
                    self.is_single_dir = True
                elif line[0].upper() == "CONTINUOUS":
                    self.is_continuous = True
                elif line[0].upper() == "LOOP":
                    self.is_loop = True
                elif line[0].upper() == "ROTATEEFFECT":
                    self.__rotate_effects[int(line[1])] = Animation.radians_to_degrees(float(line[2]))
                elif line[0].upper() == "STRETCHXEFFECT":
                    self.__stretch_x_effects[int(line[1])] = float(line[2]) if len(line) > 1 else 1
                elif line[0].upper() == "STRETCHYEFFECT":
                    self.__stretch_y_effects[int(line[1])] = float(line[2]) if len(line) > 1 else 1
                elif line[0].upper() == "COLOREFFECT":
                    self.__color_effects[int(line[1])] = [float(x) for x in line[2:]]
                elif line[0].upper() == "ZOOMEFFECT":
                    self.__zoom_effects[int(line[1])] = float(line[2]) if len(line) > 1 else 1
                elif self.__record_ani and not self.is_single_dir:
                    self.__generate_frames(line)
                elif self.__record_ani and self.is_single_dir:
                    self.__generate_frames_for_single_dir(line)
                elif record_script:
                    self.__script.append(line)
                elif self.__is_line_valid_sprite(line):
                    self.__interpret_sprite_line(line[1:])

        if len(self.__rotate_effects) > 0:
            self.__apply_rotate_effects()
        if len(self.__stretch_x_effects) > 0 or len(self.__stretch_y_effects) > 0:
            self.__apply_stretch_effects()
        if len(self.__color_effects) > 0:
            self.__apply_color_effects()
        if len(self.__zoom_effects) > 0:
            self.__apply_zoom_effects()

    def __apply_zoom_effects(self):
        for sprite in self.sprites:
            if sprite.index in self.__zoom_effects:
                sprite.zoom = self.__zoom_effects[sprite.index]

    def __apply_stretch_effects(self) -> None:
        for sprite in self.sprites:
            if sprite.index in self.__stretch_x_effects.keys():
                sprite.stretch_x = self.__stretch_x_effects[sprite.index]
            if sprite.index in self.__stretch_y_effects.keys():
                sprite.stretch_y = self.__stretch_y_effects[sprite.index]

    def __apply_color_effects(self) -> None:
        for sprite in self.sprites:
            if sprite.index in self.__color_effects.keys():
                sprite.color_effect = self.__color_effects[sprite.index]

    def __apply_rotate_effects(self) -> None:
        for sprite in self.sprites:
            if sprite.index in self.__rotate_effects.keys():
                sprite.rotation = self.__rotate_effects[sprite.index]

    def __generate_frames_for_single_dir(self, line: list) -> None:
        """
        @param line: a list containing the contents for a frame part
        """
        self.__frames.append(Frame())
        for i in range(0, len(line), 3):
            sprite_index, x, y = line[i:i+3]
            if y[-1] == ',': y = y[:-1]  # drop comma
            frame = self.__frames[-1]
            frame_part = frame.frame_parts["up"]  # TODO fix
            sprite = None
            for tmp_sprite in self.__sprites_list:
                if tmp_sprite.index == int(sprite_index):
                    sprite = tmp_sprite
            if not sprite: continue
            frame_part.add_sprite_xs_ys((sprite, int(x), int(y)))
            frame.set_frame_parts({
                "up": frame_part,
                "left": frame_part,
                "down": frame_part,
                "right": frame_part,
            })
            
    def __generate_frames(self, line: list) -> None:
        """
        @param line: a list containing the contents for a frame part
        """
        num_dir_map = {0: "up", 1: "left", 2: "down", 3: "right"}
        if self.__ani_dir == 0:
            self.__frames.append(Frame())
        for i in range(0, len(line), 3):
            sprite_index, x, y = line[i:i+3]
            if y[-1] == ',': y = y[:-1]  # drop comma
            frame_part = self.__frames[-1].frame_parts[(num_dir_map[self.__ani_dir])]
            sprite = None
            for tmp_sprite in self.__sprites_list:
                if tmp_sprite.index == int(sprite_index):
                    sprite = tmp_sprite
            if not sprite: continue
            frame_part.add_sprite_xs_ys((sprite, int(x), int(y)))
        self.__ani_dir = self.__ani_dir + 1 if self.__ani_dir < 3 else 0

    def  __interpret_sprite_line(self, line: list) -> None:
        """
        A line being passed to this method should already be a guaranteed sprite.
        The line will be interpreted and added to the sprites_list.
        @param lines: list containing sprite data
        """
        if len(line) == 6:
            self.__sprites_list.append(Sprite(*line))
        else:
            self.__sprites_list.append(Sprite(*line[:6], description=' '.join(line[6:])))

    def __is_line_valid_sprite(self, line: list) -> bool:
        """
        @param line: The line to be checked
        @return: True if the line is a sprite, False otherwise
        """
        if line[0].lower() != "sprite" or len(line) < 7:
            return False
        _, index, _, x, y, w, h = line[:7]
        if not Animation.__is_pos_or_neg_int(index) or not x.isdigit() or not y.isdigit() or not w.isdigit() or not h.isdigit():
            return False
        return True

    @staticmethod
    def __is_pos_or_neg_int(value: str) -> bool:
        if value[0] == '-':
            value = value[1:]
        return value.isdigit()

    def toggle_is_loop(self) -> None:
        self.is_loop = not self.is_loop
    
    def toggle_is_continuous(self) -> None:
        self.is_continuous = not self.is_continuous

    def toggle_single_dir(self) -> None:
        self.is_single_dir = not self.is_single_dir

    def set_attr(self, attr, value) -> None:
        """
        @param attr: The attribute to be changed
        @param value: The value to be set
        """
        self.__attrs[attr.lower()] = value
    
    def set_setbackto(self, setbackto: str) -> None:
        self.__setbackto = setbackto

    def toggle_single_dir(self) -> None:
        def i_plus_one(j):
            return j+1 if j+1 < len(self.__frames) else j
        # up, down, left, right
        if self.is_single_dir:
            new_frames = []
            for i in range(0, len(self.frames), 4):
                new_frame = copy.deepcopy(self.frames[i])
                new_frame.set_frame_parts({
                    # does not matter which direction we grab because they should all be pointing to the same frame.
                    "up": copy.deepcopy(self.frames[i].frame_parts["up"]), 
                    "left": copy.deepcopy(self.frames[i_plus_one(i)].frame_parts["left"]), 
                    "down": copy.deepcopy(self.frames[i_plus_one(i_plus_one(i))].frame_parts["down"]), 
                    "right": copy.deepcopy(self.frames[i_plus_one(i_plus_one(i_plus_one(i)))].frame_parts["right"])
                })
                new_frames.append(new_frame)
            self.__frames = new_frames
        else:
            new_frames = []
            for frame in self.frames:
                for key in ("up", "left", "down", "right"):
                    frame_part = frame.frame_parts[key]
                    new_frame = copy.deepcopy(frame)
                    new_frame.set_frame_parts({
                        "up": frame_part,
                        "down": frame_part,
                        "left": frame_part,
                        "right": frame_part
                    })
                    new_frames.append(new_frame)
            self.__frames = new_frames
        self.is_single_dir = not self.is_single_dir

    def reverse_frames(self) -> None:
        """
        Reverses the frames in the animation
        """
        self.__frames = self.__frames[::-1]

    @staticmethod
    def radians_to_degrees(radians: float) -> float:
        return radians * 180 / math.pi

    @staticmethod
    def degrees_to_radians(degrees: float) -> float:
        return degrees * math.pi / 180

    def save(self, file_name: str) -> None:
        """
        @param file_name: The name of the file to be saved
        """
        with open(file_name, "w") as f:
            f.write(self.to_string())
        
    def to_string(self) -> str:
        """
        @return the string representation of the animation
        """
        string = ""
        string += "Animator by PK Vici\n"
        for sprite in self.__sprites_list:
            string += sprite.to_string() + "\n"
        string += "\n"

        if self.__setbackto:
            string += f"SETBACKTO {self.__setbackto}\n"

        if self.is_loop: string += "LOOP\n"
        if self.is_continuous: string += "CONTINUOUS\n"
        if self.is_single_dir: string += "SINGLEDIRECTION\n"

        for attr, value in self.__attrs.items():
            string += f"DEFAULT{attr.upper()} {value}\n" if value else ""

        
        for sprite in self.sprites:
            #color effects
            if sprite.color_effect != [1,1,1,1]:
                string += f"COLOREFFECT {sprite.index}\t{sprite.color_effect[0]}\t{sprite.color_effect[1]}\t{sprite.color_effect[2]}\t{sprite.color_effect[3]}\n"
            #rotate effects
            if sprite.rotation != 0:
                string+= f"ROTATEEFFECT {sprite.index}\t{Animation.degrees_to_radians(sprite.rotation)}\n"
            #zoom effects
            if sprite.zoom != 1:
                string += f"ZOOMEFFECT {sprite.index}\t{sprite.zoom}\n"
            #stretchxeffects
            if sprite.stretch_x != 1:
                string += f"STRETCHXEFFECT {sprite.index}\t{sprite.stretch_x}\n"
            #stretchyeffects
            if sprite.stretch_y != 1:
                string += f"STRETCHYEFFECT {sprite.index}\t{sprite.stretch_y}\n"

        if len(self.__script) > 0:
            string += "SCRIPT\n"
            for line in self.__script:
                string += line + "\n"
            string += "SCRIPTEND\n"

        string += "\n"

        string += "ANI\n"
        for frame in self.__frames:
            for frame_part in frame.frame_parts.values():
                string += frame_part.to_string() + "\n"
                if self.is_single_dir:
                    break
            string += f"PLAYSOUND {frame.sfx}" if frame.sfx else ""
            string += f"WAIT {int((frame.length / 0.05)-1)}\n" if frame.length > 0.05 else "\n"
            string += "\n"
        string = string[:-1]
        string += "ANIEND\n"
        return string
