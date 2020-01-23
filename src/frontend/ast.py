class AbstractSyntaxTree():
    def __init__(self, token, content):
        self.token = token
        self.content = content
        self.children = []
        self.parent = None
        
    def addChild(self,child):
        if(len(child) > 1):
            self.children.extend(child)
            
    def addParent(self,parent):
        self.parent = parent
        self.parent.addChild(self)