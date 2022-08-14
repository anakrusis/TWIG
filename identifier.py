# a uniquely named "thing" in the code. I'm not sure how this will work
class Identifier:
    def __init__(self, name, itype):
        self.name = name
        self.parentname = False
        self.itype = itype
