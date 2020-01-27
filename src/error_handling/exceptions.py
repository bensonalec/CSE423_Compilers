# Python file defining our custom exceptions

class Error(Exception):
   """Base class for other exceptions"""
   pass

class TokenError(Error):
   """Raised when lexer fails to produce tokens (i.e. invalid token)"""

   def __init__(self, value): 
      self.value = value 
  
   def __str__(self): 
      return(repr(self.value))
   pass