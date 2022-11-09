from value import Type, Value
from intbase import InterpreterBase

def string_to_type(string):
    return {
        InterpreterBase.INT_DEF : Type.INT,
        InterpreterBase.BOOL_DEF : Type.BOOL,
        InterpreterBase.STRING_DEF : Type.STRING,
        InterpreterBase.REFINT_DEF : Type.REFINT,
        InterpreterBase.REFBOOL_DEF : Type.REFBOOL,
        InterpreterBase.REFSTRING_DEF : Type.REFSTRING,
        InterpreterBase.VOID_DEF : Type.VOID,
    }[string]