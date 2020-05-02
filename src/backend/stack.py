class stackObj():
    def __init__(self, **kwarg):
        # Scenarions:
        # Its a known variable being stored
        # Its a register with an unknown value being stored.
        # RBP being pushed

        if "Type" not in kwarg:
            # TODO: Throw some kind of error
            pass

        self.type = kwarg["Type"]

        if "KnownVar" == kwarg["Type"]:
            self.Name = kwarg["Name"]
        elif "UnknownVar" == kwarg["Type"]:
            self.Name = kwarg["Name"]
            pass
        elif "BpMov" == kwarg["Type"]:
            pass
        else:
            # Something unexpected happened
            pass

class Stack():
    """
    Emulates the stack in order to store the locations of variables not in a register.
    The base pointer is assumed to come before the start of the list. Similarly the stack pointer points exists after the end of the list.
    """

    def __init__(self):
        self.stk = []
        self.lbp = -1

    def push(self, objType, name=""):
        obj = stackObj(Name=name, Type=objType)
        if objType == "BpMove":
            self.lbp = 0
        else:
            self.lbp += 1
        self.stk.append(obj)
        pass

    def pop(self):
        self.lbp -= 1;
        return self.stk.pop()
        pass

    def peek(self):
        return self.stk[-1]

    def find_offset(self, var, bpSkipsAllowed=0):
        """
        Finds the offset if the variable has an allocated slot on the stack. Otherwise returns None.
        """
        skipCnt = -1
        voi = -1

        for i, e in enumerate(reversed(self.stk)):
            if e.type == "BpMov":
                skipCnt += 1
                if skipCnt > bpSkipsAllowed:
                    return None
            elif e.Name == var:
                voi = i

            if voi != -1:
                return (voi-self.lbp)*8
        # return None
        print("this occured")

    def dist_from_base(self):
        """
        Finds the number of bytes between the base pointer and stack pointer
        """
        return self.lbp * 8

