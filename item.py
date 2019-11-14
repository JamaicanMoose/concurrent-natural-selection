class Item():
    def __repr__(self):
        return 'I'
    @property
    def id(self):
        return str(id(self))
