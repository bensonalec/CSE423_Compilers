class import_ir():
    def __init__(self,filename):
        fd = open(filename)

        self.lines = [x.strip() for x in fd.readlines()]

        fd.close()


    def verify(self):

        vars = []
        labels = []
        gotos = []

        #checks for undefined variables.
        for i in self.lines:
            if i.startswith("int"): #make this more robust.
                vars.append(i.split(" ")[1][:-1])
            elif "=" in i and not i.startswith("_") and not i.startswith("D."):
                if [x for x in vars if i.split("=")[0].strip() == x.strip()] == []:
                    print("ERROR UNDEFINED VARIABLE")
                    print(i)
            elif i.endswith(":"):
                labels.append(i[:-1])
            elif i.startswith("goto"):
                gotos.append(i.split(" ")[1][:-1])

        #check labels
        for i in gotos:
            if not i in labels:
                print("Invalid Goto")
                print(i)


        return self.lines
