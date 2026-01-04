class SecuenciaBloques:
    def __init__(self, bloques: list):
        self.bloques = bloques  

    def esta_vacia(self):
        return len(self.bloques) == 0
