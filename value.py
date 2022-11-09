from enum import Enum
from intbase import InterpreterBase

class Type(Enum):
    '''
    Enumerated type for our different language data types.
    '''
    INT = 1
    BOOL = 2
    STRING = 3
    REFINT = 4
    REFBOOL = 5
    REFSTRING = 6
    VOID = 7

class Value:
    '''
    Represents a value, which has a type and its value.
    '''
    def __init__(self, type: Type, value=None, ref=False):
        self.t = type
        self.v = value
        self.ref = ref

    def value(self):
        return self.v

    def set(self, other):
        self.t = other.t
        self.v = other.v

    def type(self):
        return self.t

    def deepcopy(self):
        return Value(type=self.t, value=self.v)