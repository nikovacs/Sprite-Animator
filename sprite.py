class Sprite:
    def __init__(self, x, y, width, height, name, rotation=0) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.name = name
        self.rotation = 0