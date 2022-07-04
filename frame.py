from sprite import Sprite


class Frame:
    def __init__(self) -> None:
        """
        A frame can be instantiated as an empty frame or from another frame
        """
        self.__frame_parts = {
            "up": FramePart(),
            "left": FramePart(),
            "down": FramePart(),
            "right": FramePart()
        }
        self.__length = 0.05
        self.__sfxs = [] # (file, x, y)

    @property
    def length(self) -> float:
        return self.__length

    @property
    def sfxs(self) -> list:
        return self.__sfxs
            
    @property
    def frame_parts(self) -> dict:
        return self.__frame_parts
    
    def reverse(self) -> None:
        """
        Reverses the order of the sprites in the frame
        """
        for key, values in self.frame_parts.items():
            self.frame_parts[key] = values[::-1]
    
    def add_sfx(self, sfx: list) -> None:
        self.__sfxs.append((sfx[0], float(sfx[1])*16, float(sfx[2])*16))

    def set_length(self, length: float) -> None:
        self.__length = length if length >= 0.05 else 0.05

    def set_frame_parts(self, frame_parts: dict) -> None:
        if isinstance(frame_parts, dict) and len(frame_parts) == 4 and set(frame_parts.keys()) == {"up", "left", "down", "right"}:
            self.__frame_parts = frame_parts

    def delete_sprite(self, sprite: Sprite) -> None:
        for frame_part in self.frame_parts.values():
            frame_part.delete_sprite(sprite)

    def change_sfx_pos(self, sfx_index: int, x: int, y: int) -> None:
        self.__sfxs[sfx_index] = (self.__sfxs[sfx_index][0], x, y)

    def delete_sfx(self, sfx_index: int) -> None:
        self.__sfxs.pop(sfx_index)


class FramePart:
    """
    Frame part class to be used in sprite animator

    A frame part contains sprites in a list.

    Four frame parts make up one frame (one for each dir)

    The order of the list is the order they are drawn onto the screen
    """
    def __init__(self, frame_part=None) -> None:
        """
        A frame part can be instantiated as an empty frame part or from another frame part
        """
        if not frame_part:
            self.list_of_sprites_xs_ys = []
        else:
            self.list_of_sprites_xs_ys = [x for x in frame_part.list_of_sprites_xs_ys]

    @property
    def list_of_sprites(self) -> list:
        return self.list_of_sprites_xs_ys

    def change_sprite_xs_ys(self, layer: int, x=None, y=None) -> None:
        """
        Changes the location of the sprite on the screen
        @param layer: The layer of the sprite to be moved
        @param x: The new x coordinate of the sprite
        @param y: The new y coordinate of the sprite
        """
        sprite, old_x, old_y = self.list_of_sprites_xs_ys[layer]
        if not x: x = old_x
        if not y: y = old_y
        self.list_of_sprites_xs_ys[layer] = (sprite, x, y)

    def shift(self, layer: int, direction: str, amount=1) -> None:
        """
        This method is meant to be called to update the position of a specific sprite in the list.\
        @param layer: The layer of the sprite to be moved
        @param direction: The direction of the shift ("horizontal", "vertical")
        @param amount: The amount of pixels to shift the sprite
        """
        sprite, x, y = self.list_of_sprites_xs_ys[layer]
        if direction.lower() == "horizontal":
            x += amount
        elif direction.lower() == "vertical":
            y += amount
        self.list_of_sprites_xs_ys[layer] = (sprite, x, y)

    def delete_sprite(self, sprite: Sprite) -> None:
        self.list_of_sprites_xs_ys = [x for x in self.list_of_sprites_xs_ys if x[0] != sprite]

    def change_layer(self, layer_to_move: int, direction: str) -> bool:
        """
        Changes the layer of the sprite within the list.
        @param layer_to_move: The layer of the sprite to be moved (int)
        @param direction: The direction of the change ("up", "down")
        @return: boolean whether the layer was changed or not (not changed when already at the top or bottom)
        return value is important in order to know whether the curr_sprite pointer is to be changed or not
        """
        if layer_to_move < 0 or layer_to_move >= len(self.list_of_sprites_xs_ys):
            raise ValueError("Layer to move is out of range")
        elif direction.lower() not in ('up', 'down'):
            raise ValueError("Direction must be 'up' or 'down'")

        if direction.lower() == "up":
            if len(self.list_of_sprites_xs_ys)-1 > layer_to_move >= 0:
                self.list_of_sprites_xs_ys[layer_to_move], self.list_of_sprites_xs_ys[layer_to_move + 1] = \
                    self.list_of_sprites_xs_ys[layer_to_move + 1], self.list_of_sprites_xs_ys[layer_to_move]
                return True
        elif direction.lower() == "down":
            if len(self.list_of_sprites_xs_ys) > layer_to_move > 0:
                self.list_of_sprites_xs_ys[layer_to_move], self.list_of_sprites_xs_ys[layer_to_move - 1] = \
                    self.list_of_sprites_xs_ys[layer_to_move - 1], self.list_of_sprites_xs_ys[layer_to_move]
                return True
        return False
    
    def add_sprite_xs_ys(self, sprite_x_y: tuple) -> None:
        """
        Adds a sprite to the list
        Format: (Sprite, x, y)
        """
        self.list_of_sprites_xs_ys.append(sprite_x_y)

    def change_order(self, orig_ind, new_ind) -> None:
        """
        Changes the order of the sprites in the list.

        @param orig_ind: The index of the sprite to be moved
        @param new_ind: The index to move the sprite to
        """
        self.list_of_sprites_xs_ys.insert(new_ind, self.list_of_sprites.pop(orig_ind))

    def remove_by_layer(self, layer) -> None:
        """
        Removes a sprite from the list

        @param ind: The index of the sprite to be removed
        """
        self.list_of_sprites_xs_ys.pop(layer)

    def to_string(self) -> str:
        """
        Returns a string representation of the frame part
        """
        out = ""
        for sprite, x, y in self.list_of_sprites_xs_ys:
            out += f"\t{sprite.index}\t{x}\t{y},"
        return out[:-1]

