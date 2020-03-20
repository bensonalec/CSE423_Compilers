class import_ir():
    def __init__(self,filename):
        fd = open(filename)

        self.lines = [x.strip() for x in fd.readlines()]


    def verify(self):

        return self.lines
