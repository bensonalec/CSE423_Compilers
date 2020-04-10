#this file will solve all our problems. indeed.
class ASMNode():
    def __init__(self, command, left, right):
        self.command = command
        self.left = left
        self.right = right

    def __str__(self):
        if right:
            return f"{self.command} {self.left}, {self.right};"
        elif left:
            return f"{self.command} {self.left};"
        else:
            return f"{self.command};"

    def __repr__(self):
        pass