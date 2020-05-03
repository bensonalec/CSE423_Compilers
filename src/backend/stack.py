class stackObj():
    """
    The object that is put on the stack, contains the type of the object on the stack (register, base pointer, etc) and the name of the object
    """
    def __init__(self, **kwarg):
        """
        Initializes the object that goes on the stack

        Args:
            kwarg: A dictionary of various objects
        """
        # Scenarions:
        # Its a known variable being stored
        # Its a register with an unknown value being stored.
        # RBP being pushed

        if "Type" not in kwarg:
            # TODO: Throw some kind of error
            pass

        self.type = kwarg["Type"]
        self.Name = kwarg["Name"]
    
    def __str__(self):
        return f"{self.type} {self.Name}"

class Stack():
    """
    Emulates the stack in order to store the locations of variables not in a register.
    The base pointer is assumed to come before the start of the list. Similarly the stack pointer points exists after the end of the list.
    """
    def __init__(self):
        """
        Initializes the stack
        """

        self.stk = []
        self.lbp = -1

    def push(self, objType, name=""):
        """
        Takes in a list of asm strings using variable names, converts these to use proper register allocation

        Args:
            objType: The object type, essentially is it a base pointer, etc.
            name: The name being stored in the stack object
        """

        obj = stackObj(Name=name, Type=objType)
        if objType == "BpMov":
            self.lbp = 0
        else:
            self.lbp += 1
        
        self.stk.append(obj)
        pass

    def pop(self):
        """
        Pops the top object off of the stack

        Returns:
            the popped stack object
        """
        self.lbp -= 1
        return self.stk.pop()
        pass

    def peek(self):
        """
        Returns the top item on the stack without popping it

        Returns:
            The top object on the stack
        """
        return self.stk[-1]

    def find_offset(self, var, bpSkipsAllowed=0):
        """
        Finds the offset if the variable has an allocated slot on the stack. Otherwise returns None.

        Args:
            var: The variable name that is being checked for
            bpSkipsAllowed: The number of basepointers that can be moved past, used to determine if something has a variable within scope

        Returns: 
            Either none or the newly calulated offset
        """
        skipCnt = -1
        voi = -1

        for i, e in enumerate(reversed(self.stk)):
            if e.type == "BpMov":
                skipCnt += 1
                if skipCnt >= bpSkipsAllowed:
                    return None
            elif e.Name == var:
                voi = i

            if voi != -1:
                return (voi-self.lbp + 1)*8

        # Variable cant be found on the stack
        return None

    def dist_from_base(self):
        """
        Finds the number of bytes between the base pointer and stack pointer

        Returns:
            The number of bytes between the base pointer and the stack pointer
        """
        return self.lbp * 8

    def clear(self):
        """
        Clears the stack for when it is needed
        """
        self.stk = []
        self.lbp = -1

    def __str__(self):
        return str([str(x) for x in self.stk])