from frame import Frame

class Animation:
    """
    Animation is the "parent" class that holds all the frames, which hold all the frame parts, which holds all the sprites.
    """
    def __init__(self) -> None:
        self.frames = [Frame()]