class Stack():
    """
    Emulates the stack in order to store the locations of variables not in a register.
    The base pointer is assumed to come before the start of the list. Similarly the stack pointer points exists after the end of the list.
    """
    scopes = []

    def __init__(self):
        self.stk = []

    def scope_change(self):
        """
        Call when the base pointer and stack pointer are both modified to declare a new scope
        """
        self.scopes.append(self.stk)
        self.stk = []

    def scope_return(self):
        """
        Removes current scope and "returns" to previous stack scope.
        """
        self.stk = self.scopes.pop()

    def insert(self, var):
        """
        Inserts variable onto the current stack scope.
        """
        if len(self.stk) > 0:
            base_offset = self.stk[-1][1]
        else:
            base_offset = 0

        self.stk.append((var, base_offset - 4))

        return base_offset - 4

    def find_offset(self, var):
        """
        Finds the offset if the variable has an allocated slot on the stack. Otherwise returns None.
        """
        # print (var)
        candidates = [x[1] for x in self.stk if x[0] == var]
        # print (candidates)
        if candidates == []:
            return None

        return candidates[0]

    def dist_from_base(self):
        """
        Finds the number of bytes between the base pointer and stack pointer
        """
        return len(self.stk) * 4

