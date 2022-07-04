class Sprite:
    def __init__(self, sprite_index, image, x, y, width, height, description='') -> None:
        self.image = image
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)
        self.index = int(sprite_index)
        self.desc = description
        self.rotation = 0
        self.stretch_x = 1
        self.stretch_y = 1
        self.zoom = 1
        self.color_effect = [1, 1, 1, 1]
        self.mode = 0

    def to_string(self) -> str:
        return f"SPRITE {self.index} {self.image} {self.x} {self.y} {self.width} {self.height} {self.desc}"
