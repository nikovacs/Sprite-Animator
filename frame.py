from sprite import Sprite

class Frame:
    def __init__(self) -> None:
        self.frame_parts = {
            "left": FramePart(),
            "right": FramePart(),
            "up": FramePart(),
            "down": FramePart(),
        }
        self.length = 0.05


class FramePart:
    """
    Frame part class to be used in sprite animator

    A frame part contains sprites in a list.

    Four frame parts make up one frame (one for each dir)

    The order of the list is the order they are drawn onto the screen
    """
    def __init__(self) -> None:
        self.list_of_sprites = []
    
    def add_sprite(self, sprite) -> None:
        self.list_of_sprites.append(sprite)

    def change_order(self, orig_ind, new_ind) -> None:
        """
        Changes the order of the sprites in the list.

        @param orig_ind: The index of the sprite to be moved
        @param new_ind: The index to move the sprite to
        """
        self.list_of_sprites.insert(new_ind, self.list_of_sprites.pop(orig_ind))

    def remove_by_index(self, ind) -> None:
        """
        Removes a sprite from the list

        @param ind: The index of the sprite to be removed
        """
        self.list_of_sprites.pop(ind)
    
    def remove_by_sprite(self, sprite) -> None:
        """
        Removes a sprite from the list

        @param sprite: The sprite to be removed
        """
        self.list_of_sprites.remove(sprite)

    def get_sprite_by_index(self, ind) -> Sprite:
        """
        Gets a sprite from the list

        @param ind: The index of the sprite to be returned
        """
        return self.list_of_sprites[ind]
    
    def get_sprite_by_name(self, name) -> Sprite:
        """
        Gets a sprite from the list

        @param name: The name of the sprite to be returned
        """
        for sprite in self.list_of_sprites:
            if sprite.name == name:
                return sprite