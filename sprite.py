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
    
    def copy(self) -> "Sprite":
        return Sprite(self.index, self.image, self.x, self.y, self.width, self.height, self.rotation, self.desc)

    def to_string(self) -> str:
        return f"SPRITE\t{self.index}\t{self.image}\t{self.x}\t{self.y}\t{self.width}\t{self.height}\t{self.desc}"
