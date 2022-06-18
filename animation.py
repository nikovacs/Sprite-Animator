from frame import Frame
from sprite import Sprite

class Animation:
    """
    Animation is the "parent" class that holds all the frames, which hold all the frame parts, which holds all the sprites.
    The order of the frames in the list is the order that they wil be displayed.
    """
    def __init__(self, from_file=None) -> None:
        self.__script = []
        self.__color_effects = []
        self.__rotate_effects = []
        self.__stretch_effects = []
        self.__frames = []
        self.__sprites_list = []

        # initialize these attributes to False.
        # Empty ani defaults these to False and 
        # loading from an existing ani will 
        # overwrite them if needed
        self.__is_loop = False
        self.__is_continuous = False
        self.__single_dir = False

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

    def __set_attrs_from_existing_ani(self, file):
        # set some default values for parsing flags
        self.__record_ani = False # instance variable because used in helper method
        record_script = False

        with open(file, 'r') as f:
            for line in f:
                line = line.split()
                if len(line) == 0:
                    continue
                    # lines in file are tab delimited
                    # ex. ['SPRITE', '-1000', 'ATTR12', '0', '0', '64', '64', 'backpack']
                if self.__record_ani and not self.__single_dir:
                    self.__generate_frames(line)
                elif self.__record_ani and self.__single_dir:
                    self.__generate_frames_for_single_dir(line)
                elif record_script:
                    self.__script.append(line)
                elif line[0].upper() == "PLAYSOUND":
                        self.__frames[-1].set_sfx(line[1:]) 
                elif line[0].upper() == "WAIT":
                    self.__frames[-1].set_wait(line[1])
                if line[0].upper() == "SCRIPT":
                    record_script = True
                elif line[0].upper() == "SCRIPTEND":
                    record_script = False
                elif line[0].upper() == "SETBACKTO":
                    self.setbackto = line[1] if len(line) > 1 else ""
                elif line[0].upper() == "DEFAULTATTR1":
                    self.__attrs["attr1"] = line[1] if len(line) > 1 else ""
                elif line[0].lower() == "DEFAULTHEAD":
                    self.__attrs["head"] = line[1] if len(line) > 1 else ""
                elif line[0].lower() == "DEFAULTBODY":
                    self.__attrs["body"] = line[1] if len(line) > 1 else ""
                elif line[0].lower() == "DEFAULTSHIELD":
                    self.__attrs["shield"] = line[1] if len(line) > 1 else ""
                elif line[0].upper() == "ANI":
                    self.__record_ani = True
                    self.__ani_dir = 0
                elif line[0].upper() == "ANIEND":
                    self.__record_ani = False
                elif line[0].upper() == "SINGLEDIRECTION":
                    self.__single_dir = True
                elif line[0].upper() == "CONTINUOUS":
                    self.__is_continuous = True
                elif line[0].upper() == "LOOP":
                    self.__is_loop = True
                elif line[0].upper() == "COLOREFFECT":
                    self.__color_effects.append(line[1:]  if len(line) > 1 else "")
                elif line[0].upper() == "ROTATEEFFECT":
                    self.__rotate_effects.append(line[1:] if len(line) > 1 else "")
                elif line[0].upper() == "STRETCHEFFECT":
                    self.__stretch_effects.append(line[1:] if len(line) > 1 else "")
                

                elif self.__is_line_valid_sprite(line):
                    self.__interpret_sprite_line(line[1:])

    def __generate_frames_for_single_dir(self, line: list) -> None:
        """
        @param line: a list containing the contents for a frame part
        """
        for i in range(0, len(line), 3):
            sprite_index, x, y = line[i:i+3]
            frame_part = self.__frames[-1].get_frame_part("up")
            frame_part.add_sprite_xs_ys((sprite_index, x, y))
        self.__record_ani = False


    def __generate_frames(self, line: list) -> list:
        """
        @param line: a list containing the contents for a frame part
        """
        num_dir_map = {0: "up", 1: "left", 2: "down", 3: "right"}
        if self.__ani_dir == 0:
            self.__frames.append(Frame())
        for i in range(0, len(line), 3):
            sprite_index, x, y = line[i:i+3]
            if y[-1] == ',': y = y[:-1]  # drop comma
            frame_part = self.__frames[-1].get_frame_part(num_dir_map[self.__ani_dir])
            frame_part.add_sprite_xs_ys((int(sprite_index), int(x), int(y)))

        self.__ani_dir = self.__ani_dir + 1 if self.__ani_dir < 3 else 0
        if self.__ani_dir == 0:
            self.__record_ani = False


    def  __interpret_sprite_line(self, line: list) -> None:
        """
        A line being passed to this method should already be a guaranteed sprite.
        The line will be interpreted and added to the sprites_list.
        @param lines: list containing sprite data
        """
        if len(line) == 6:
            self.__sprites_list.append(Sprite(*line))
        else:
            self.__sprites_list.append(Sprite(*line[:6], description=' '.join(line[7:])))


    def __is_line_valid_sprite(self, line: list) -> bool:
        """
        @param line: The line to be checked
        @return: True if the line is a sprite, False otherwise
        """
        if line[0].lower() != "sprite" or len(line) < 7:
            return False
        _, index, _, x, y, w, h = line[:7]
        if not self.__is_pos_or_neg_int(index) or not x.isdigit() or not y.isdigit() or not w.isdigit() or not h.isdigit():
            return False
        return True
        

    def __is_pos_or_neg_int(self, value: str) -> bool:
        if value[0] == '-':
            value = value[1:]
        return value.isdigit()

    def toggle_is_loop(self) -> None:
        self.is_loop = not self.is_loop
    
    def toggle_is_continuous(self) -> None:
        self.is_continuous = not self.is_continuous

    def toggle_single_dir(self) -> None:
        self.single_dir = not self.single_dir

    def set_attr(self, attr, value) -> None:
        """
        @param attr: The attribute to be changed
        @param value: The value to be set
        """
        self.__attrs[attr.lower()] = value
    
    def set_setbackto(self, setbackto: str) -> None:
        self.set_setbackto = setbackto

    def get_sprites_list(self) -> list:
        return self.__sprites_list
