#this file will solve all our problems. indeed.
class ASMNode():
    def __init__(self, command, left, right, **kwarg):
        self.command = command
        self.left = left
        self.right = right

        self.offset = kwarg["offset"] if "offset" in kwarg else None
        self.leftTmp = "leftTmp" in kwarg
        self.rightTmp = "rightTmp" in kwarg

    def __str__(self):
        if self.right:
            return f"{self.command} {self.left}, {self.right}"
        elif self.left:
            return f"{self.command} {self.left}"
        else:
            return f"{self.command}"
