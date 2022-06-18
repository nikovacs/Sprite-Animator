from sprite import Sprite


class Frame:
    def __init__(self, frame=None) -> None:
        """
        A frame can be instantiated as an empty frame or from another frame
        """
        if not frame:
            self.__frame_parts = {
                "up": FramePart(),
                "left": FramePart(),
                "down": FramePart(),
                "right": FramePart()
            }
            self.length = 0.05
            self.sfx_file = ""
            self.wait = 0
        else:
            self.__frame_parts = {k: FramePart(v) for k, v in frame.frame_parts.items()}
            self.length = frame.length
            self.sfx_file = frame.sfx_file
            self.wait = frame.wait
            
    @property
    def frame_parts(self) -> dict:
        return self.__frame_parts
    
    def reverse(self) -> None:
        """
        Reverses the order of the sprites in the frame
        """
        for key, values in self.frame_parts.items():
            self.frame_parts[key] = values[::-1]
    
    def set_sfx(self, file: str) -> None:
        self.sfx_file = file

    def set_wait(self, wait: int) -> None:
        self.wait = wait
    
    def get_frame_part(self, direction: str) -> "FramePart":
        """
        Returns the frame part for the given direction
        
        @param direction: The direction of the frame part ("up", "left", "down", "right")
        """
        return self.frame_parts[direction.lower()]


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

    def remove_by_index(self, ind) -> None:
        """
        Removes a sprite from the list

        @param ind: The index of the sprite to be removed
        """
        self.list_of_sprites_xs_ys.pop(ind)
    
    def remove_by_sprite(self, sprite) -> None:
        """
        Removes a sprite from the list

        @param sprite: The sprite to be removed
        """
        self.list_of_sprites_xs_ys.remove(sprite)

    def get_sprite_by_positional_index(self, ind) -> Sprite:
        """
        Gets a sprite from the list

        @param ind: The index of the sprite to be returned
        """
        return self.list_of_sprites_xs_ys[ind]
    
    def get_sprite_by_description(self, desc) -> Sprite:
        """
        Gets a sprite from the list

        @param name: The name of the sprite to be returned
        """
        for sprite in self.list_of_sprites:
            if sprite.desc == desc:
                return sprite

    def get_sprite_by_index(self, ind) -> Sprite:
        return []