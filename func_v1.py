from intbase import InterpreterBase, ErrorType
from value import Type, Value
import util

class FuncInfo:
    '''
    FuncInfo is a class that represents information about a function
    Right now, the only thing this tracks is the line number of the first executable instruction
    of the function (i.e., the line after the function prototype: func foo)
    '''
    def __init__(self, start_ip):
        self.start_ip = start_ip    # line number, zero-based
        self.names = []
        self.values = []
        self.return_type = None

    def add_parameter(self, symbol, value):
        self.names.append(symbol)
        self.values.append(value)

    def set_return_type(self, return_type):
        self.return_type = return_type

class FunctionManager:
    '''
    FunctionManager keeps track of every function in the program, mapping the function name
    to a FuncInfo object (which has the starting line number/instruction pointer) of that function.
    '''
    # TODO: verify validity of parameter and return types:
    # valid parameters: int, bool, string, refint, refbool, refstring
    # valid returns: int, bool, string, void
    def __init__(self, tokenized_program):
        self.func_cache = {}
        self._cache_function_line_numbers(tokenized_program)

    def get_function_info(self, func_name):
        if func_name not in self.func_cache:
          return None
        return self.func_cache[func_name]

    def _cache_function_line_numbers(self, tokenized_program):
        # Enumerate every line in the tokenized list
        for line_num, line in enumerate(tokenized_program):
            if line and line[0] == InterpreterBase.FUNC_DEF:
                if len(line) < 3:
                    InterpreterBase.error(ErrorType.SYNTAX_ERROR, 'Invalid function declaration')
                # Set the function name and store line_num
                func_name = line[1]
                func_info = FuncInfo(line_num + 1)   # function starts executing on line after funcdef

                # Set the parameters (symbols & types, including references)
                for parameter in line[2:-1]:
                    tokens = parameter.split(':')
                    if len(tokens) != 2:
                        InterpreterBase.error(ErrorType.SYNTAX_ERROR, 'Invalid parameter definition')
                    
                    symbol, var_type = tokens
                    value = Value(util.string_to_type(var_type), None)
                    if 'ref' in var_type:
                        var_type = util.string_to_type(var_type[3:])
                        value = Value(var_type, None, ref=True)
                    func_info.add_parameter(symbol, value)
                    # print(value.type(), value.value(), value.ref)

                # Set the return type of this function
                func_info.set_return_type(util.string_to_type(line[-1]))

                if func_info.return_type == Type.REFBOOL or func_info.return_type == Type.REFINT or func_info.return_type == Type.REFSTRING:
                    InterpreterBase.error(ErrorType.TYPE_ERROR, 'Invalid return type')

                self.func_cache[func_name] = func_info
       