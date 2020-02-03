"""
This module contains the class for creating an Abstract Syntax Tree.
"""
class AbstractSyntaxTree():
    """
    AbstractSyntaxTree is a class that acts as each node in an Abstract Syntax Tree
    """
    def __init__(self, token, content):
        """
        Construct a new AbstractSyntaxTree object
        :param token: the token type of the node
        :param content: the content of that is tokenized
        :return: this returns nothing
        """
        self.token = token
        self.content = content