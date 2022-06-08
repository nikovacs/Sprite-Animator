class Sprite:
    def __init__(self, sprite_index, image, x, y, width, height, rotation=0, description='') -> None:
        self.image = image
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rotation = rotation
        self.index = sprite_index
        self.desc = description