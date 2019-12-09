# pylint: skip-file
class Item():
    '''Parent class of Item and Resource'''
    def __repr__(self):
        return 'I'

    @property
    def id(self):
        return str(id(self))

    @property
    def type(self):
        return 'item'
