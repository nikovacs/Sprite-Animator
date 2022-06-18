class Sprite:
    def __init__(self, sprite_index, image, x, y, width, height, rotation=0, description='') -> None:
        self.image = image
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)
        self.rotation = int(rotation)
        self.index = int(sprite_index)
        self.desc = description
    
    def copy(self) -> "Sprite":
        return Sprite(self.index, self.image, self.x, self.y, self.width, self.height, self.rotation, self.desc)
