class LevelOneIR():
    def __init__(self,astHead,symTable):
        self.astHead = astHead
        self.symTable = symTable

    def construct(self):
        ntv = [self.astHead]

        while ntv != []:
            cur = ntv[0]
            # print(cur.name)
            ntv = [x for x in cur.children] + ntv[1:]
