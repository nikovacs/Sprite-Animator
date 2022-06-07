class Sprite:
    def __init__(self, image, x, y, width, height, name, sprite_index, rotation=0, description='') -> None:
        self.image = image
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.name = name
        self.rotation = 0
        self.index = sprite_index