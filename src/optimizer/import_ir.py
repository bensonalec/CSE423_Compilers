"""
This module handle ir input from a file
"""


class import_ir():
    def __init__(self,filename):
        """
        This is the contructor for import ir.

        Args:
            filename: The name of the file

        Returns:
            Nothing
        """
        fd = open(filename)

        #read file and strip white space
        self.lines = [x.strip() for x in fd.readlines()]

        fd.close()


    def verify(self):
        """
        This function verifies the IR.

        Returns:
            Prints errors and returns lines
        """

        vars = []
        labels = []
        gotos = []

        #checks for undefined variables.
        for i in self.lines:
            temp_line = i.strip()
            if temp_line.startswith("int"): #make this more robust.
                vars.append(temp_line.split(" ")[1][:-1])
            
            #skip if statement for loop for while for now
            elif(temp_line.startswith("if") or temp_line.startswith("for") or temp_line.startswith("while")):
                continue
            #check if it is user variable assignment.
            elif "=" in temp_line and not temp_line.startswith("_") and not temp_line.startswith("D."):
                #if variable has been declared
                if [x for x in vars if temp_line.split("=")[0].strip() == x.strip()] == []:
                    print("ERROR UNDEFINED VARIABLE")
                    print(temp_line)
            #label
            elif temp_line.endswith(":"):
                labels.append(temp_line[:-1])
            #goto
            elif temp_line.startswith("goto"):
                gotos.append(temp_line.split(" ")[1][:-1])

        #check labels
        for i in gotos:
            if not i in labels:
                print("Invalid Goto")
                print(i)


        return self.lines
