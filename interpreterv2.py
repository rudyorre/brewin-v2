from enum import Enum
from intbase import InterpreterBase, ErrorType
from value import Type, Value
from env_v1 import EnvironmentManager
from tokenize import Tokenizer
from func_v1 import FunctionManager

class Interpreter(InterpreterBase):
  '''
  Main interpreter class
  '''
  def __init__(self, console_output=True, input=None, trace_output=False):
    super().__init__(console_output, input)
    self._setup_operations()  # setup all valid binary operations and the types they work on
    self.trace_output = trace_output

  def run(self, program):
    '''
    Run a program, provided in an array of strings, one string per line of source code.
    '''
    self.program = program
    self._compute_indentation(program)  # determine indentation of every line
    self.tokenized_program = Tokenizer.tokenize_program(program)
    self.func_manager = FunctionManager(self.tokenized_program)
    self.ip = self._find_first_instruction(InterpreterBase.MAIN_FUNC)
    self.return_stack = []
    self.terminate = False
    self.env_manager = EnvironmentManager() # used to track variables/scope

    # main interpreter run loop
    while not self.terminate:
      self._process_line()

  def _process_line(self):
    # TODO: remove
    # self.env_manager.print_env(types=True)
    if self.trace_output:
      print(f"{self.ip:04}: {self.program[self.ip].rstrip()}")
    tokens = self.tokenized_program[self.ip]
    if not tokens:
      self._blank_line()
      return

    args = tokens[1:]

    match tokens[0]:
      case InterpreterBase.VAR_DEF:
        self._var(args)
      case InterpreterBase.ASSIGN_DEF:
        self._assign(args)
      case InterpreterBase.FUNCCALL_DEF:
        self.env_manager.push_scope()
        self._funccall(args)
      case InterpreterBase.ENDFUNC_DEF:
        self._endfunc()
        self.env_manager.pop_scope()
      case InterpreterBase.IF_DEF:
        self.env_manager.push_scope()
        self._if(args)
      case InterpreterBase.ELSE_DEF:
        self.env_manager.pop_scope()
        self.env_manager.push_scope()
        self._else()
      case InterpreterBase.ENDIF_DEF:
        self._endif()
        self.env_manager.pop_scope()
      case InterpreterBase.RETURN_DEF:
        self._return(args)
        self.env_manager.pop_scope()
      case InterpreterBase.WHILE_DEF:
        self.env_manager.push_scope()
        self._while(args)
      case InterpreterBase.ENDWHILE_DEF:
        self._endwhile(args)
        self.env_manager.pop_scope()
      case default:
        raise Exception(f'Unknown command: {tokens[0]}')

  def _blank_line(self):
    self._advance_to_next_statement()

  def _var(self, tokens):
    if len(tokens) < 2:
      super().error(ErrorType.SYNTAX_ERROR, 'Invalid variable definition')
    
    var_type = {
      InterpreterBase.INT_DEF : Type.INT,
      InterpreterBase.BOOL_DEF : Type.BOOL,
      InterpreterBase.STRING_DEF : Type.STRING,
    }[tokens[0]]

    var_value = {
      InterpreterBase.INT_DEF : 0,
      InterpreterBase.BOOL_DEF : False,
      InterpreterBase.STRING_DEF : "",
    }[tokens[0]]

    for var_name in tokens[1:]:
      if self.env_manager.exists_scope(var_name):
        super().error(ErrorType.NAME_ERROR, f'Conflicting variable declaration `{var_name}`')
      self.env_manager.add(var_name, Value(var_type, var_value))
      # self._set_value(var_name, Value(var_type, None))
    
    self._advance_to_next_statement()

  def _assign(self, tokens) -> None:
    '''
    All variables must be defined before they are used, so assignment will
    occur only if the variable already exists within the environment manager
    and the assignment value type matches the variable type.
    '''
    var_name = tokens[0]
    value = self._eval_expression(tokens[1:])

    if len(tokens) < 2:
      super().error(ErrorType.SYNTAX_ERROR, 'Invalid assignment statement') #no
    if not self.env_manager.exists(var_name):
      super().error(ErrorType.NAME_ERROR, f'Unable to locate variable: `{var_name}`', self.ip)
    env_var_type = self.env_manager.get(var_name).type()
    if env_var_type != value.type():
      super().error(ErrorType.TYPE_ERROR, f'Mismatching types {env_var_type} and {value.type()}', self.ip)

    self._set_value(tokens[0], value)
    self._advance_to_next_statement()

  def _funccall(self, args):
    if not args:
      super().error(ErrorType.SYNTAX_ERROR,"Missing function name to call", self.ip) #!
    
    # TODO: after built-in functions (print, input, etc) are run, the env_manager
    # pops the most recent scope manually since the IP doesn't run into any
    # returns in the code. Find a cleaner way to implement this functionality.

    if args[0] == InterpreterBase.PRINT_DEF:
      self._print(args[1:])
      self.env_manager.pop_scope()
      self._advance_to_next_statement()
    elif args[0] == InterpreterBase.INPUT_DEF:
      self._input(args[1:])
      # self.env_manager.pop_scope()
      self._advance_to_next_statement()
    elif args[0] == InterpreterBase.STRTOINT_DEF:
      self._strtoint(args[1:])
      # self.env_manager.pop_scope()
      self._advance_to_next_statement()
    else:
      self.return_stack.append(self.ip+1)
      self.ip = self._find_first_instruction(args[0], args[1:])

  def _endfunc(self):
    if not self.return_stack:  # done with main!
      self.terminate = True
    else:
      self.ip = self.return_stack.pop()

  def _if(self, args):
    if not args:
      super().error(ErrorType.SYNTAX_ERROR,"Invalid if syntax", self.ip) #no
    value_type = self._eval_expression(args)
    if value_type.type() != Type.BOOL:
      super().error(ErrorType.TYPE_ERROR,"Non-boolean if expression", self.ip) #!
    
    if value_type.value():
      self._advance_to_next_statement()
      return
    else:
      for line_num in range(self.ip+1, len(self.tokenized_program)):
        tokens = self.tokenized_program[line_num]
        if not tokens:
          continue
        if (tokens[0] == InterpreterBase.ENDIF_DEF or tokens[0] == InterpreterBase.ELSE_DEF) and self.indents[self.ip] == self.indents[line_num]:
          self.ip = line_num + 1
          return
    super().error(ErrorType.SYNTAX_ERROR,"Missing endif", self.ip) #no

  def _endif(self):
    self._advance_to_next_statement()

  def _else(self):
    for line_num in range(self.ip+1, len(self.tokenized_program)):
      tokens = self.tokenized_program[line_num]
      if not tokens:
        continue
      if tokens[0] == InterpreterBase.ENDIF_DEF and self.indents[self.ip] == self.indents[line_num]:
          self.ip = line_num + 1
          self.env_manager.pop_scope() # TODO: not sure if this is good placement or not
          return
    super().error(ErrorType.SYNTAX_ERROR,"Missing endif", self.ip) #no

  def _return(self, args):
    '''
    Returns a value for user-defined functions.

    If a return were to happen within a nested scope (such as an if-statement within the function),
    the scopes created by these structures must be destroyed before moving on. Therefore this function
    will parse through the rest of the user-defined function until it finds an `endfunc` statement,
    while doing so it will pop a scope for every `end` statement it finds.
    '''
    if not args:
      self._endfunc()
      return
    value = self._eval_expression(args)
    # self._set_value(InterpreterBase.RESULT_DEF, value_type)   # return always passed back in result
    symbol = {Type.INT : 'resulti', Type.BOOL : 'resultb', Type.STRING : 'results'}[value.type()]
    self.env_manager.set_return(symbol, value)
    for line_num in range(self.ip + 1, len(self.tokenized_program)):
      tokens = self.tokenized_program[line_num]
      if not tokens:
        continue
      if tokens[0] == InterpreterBase.ENDIF_DEF or tokens[0] == InterpreterBase.ENDWHILE_DEF:
        self.env_manager.pop_scope() # TODO: not sure if this is good placement or not
    self._endfunc()

  def _while(self, args):
    if not args:
      super().error(ErrorType.SYNTAX_ERROR,"Missing while expression", self.ip) #no
    value_type = self._eval_expression(args)
    if value_type.type() != Type.BOOL:
      super().error(ErrorType.TYPE_ERROR,"Non-boolean while expression", self.ip) #!
    if value_type.value() == False:
      self._exit_while()
      return

    # If true, we advance to the next statement
    self._advance_to_next_statement()

  def _exit_while(self):
    while_indent = self.indents[self.ip]
    cur_line = self.ip + 1
    while cur_line < len(self.tokenized_program):
      if self.tokenized_program[cur_line][0] == InterpreterBase.ENDWHILE_DEF and self.indents[cur_line] == while_indent:
        self.ip = cur_line + 1
        return
      if self.tokenized_program[cur_line] and self.indents[cur_line] < self.indents[self.ip]:
        break # syntax error!
      cur_line += 1
    # didn't find endwhile
    super().error(ErrorType.SYNTAX_ERROR,"Missing endwhile", self.ip) #no

  def _endwhile(self, args):
    while_indent = self.indents[self.ip]
    cur_line = self.ip - 1
    while cur_line >= 0:
      if self.tokenized_program[cur_line][0] == InterpreterBase.WHILE_DEF and self.indents[cur_line] == while_indent:
        self.ip = cur_line
        return
      if self.tokenized_program[cur_line] and self.indents[cur_line] < self.indents[self.ip]:
        break # syntax error!
      cur_line -= 1
    # didn't find while
    super().error(ErrorType.SYNTAX_ERROR,"Missing while", self.ip) #no

  def _print(self, args):
    if not args:
      super().error(ErrorType.SYNTAX_ERROR,"Invalid print call syntax", self.ip) #no
    out = []
    for arg in args:
      val_type = self._get_value(arg)
      out.append(str(val_type.value()))
    super().output(''.join(out))

  def _input(self, args):
    if args:
      self._print(args)
    result = super().get_input()
    self._set_value(InterpreterBase.RESULT_DEF, Value(Type.STRING, result))   # return always passed back in result

  def _strtoint(self, args):
    if len(args) != 1:
      super().error(ErrorType.SYNTAX_ERROR,"Invalid strtoint call syntax", self.ip) #no
    value_type = self._get_value(args[0])
    if value_type.type() != Type.STRING:
      super().error(ErrorType.TYPE_ERROR,"Non-string passed to strtoint", self.ip) #!
    self._set_value(InterpreterBase.RESULT_DEF, Value(Type.INT, int(value_type.value())))   # return always passed back in result

  def _advance_to_next_statement(self):
    # for now just increment IP, but later deal with loops, returns, end of functions, etc.
    self.ip += 1

  # create a lookup table of code to run for different operators on different types
  def _setup_operations(self):
    '''
    Creates a lookup table of code to run for different operators on different types.
    '''
    self.binary_op_list = ['+','-','*','/','%','==','!=', '<', '<=', '>', '>=', '&', '|']
    self.binary_ops = {}
    self.binary_ops[Type.INT] = {
     '+': lambda a,b: Value(Type.INT, a.value()+b.value()),
     '-': lambda a,b: Value(Type.INT, a.value()-b.value()),
     '*': lambda a,b: Value(Type.INT, a.value()*b.value()),
     '/': lambda a,b: Value(Type.INT, a.value()//b.value()),  # // for integer ops
     '%': lambda a,b: Value(Type.INT, a.value()%b.value()),
     '==': lambda a,b: Value(Type.BOOL, a.value()==b.value()),
     '!=': lambda a,b: Value(Type.BOOL, a.value()!=b.value()),
     '>': lambda a,b: Value(Type.BOOL, a.value()>b.value()),
     '<': lambda a,b: Value(Type.BOOL, a.value()<b.value()),
     '>=': lambda a,b: Value(Type.BOOL, a.value()>=b.value()),
     '<=': lambda a,b: Value(Type.BOOL, a.value()<=b.value()),
    }
    self.binary_ops[Type.STRING] = {
     '+': lambda a,b: Value(Type.STRING, a.value()+b.value()),
     '==': lambda a,b: Value(Type.BOOL, a.value()==b.value()),
     '!=': lambda a,b: Value(Type.BOOL, a.value()!=b.value()),
     '>': lambda a,b: Value(Type.BOOL, a.value()>b.value()),
     '<': lambda a,b: Value(Type.BOOL, a.value()<b.value()),
     '>=': lambda a,b: Value(Type.BOOL, a.value()>=b.value()),
     '<=': lambda a,b: Value(Type.BOOL, a.value()<=b.value()),
    }
    self.binary_ops[Type.BOOL] = {
     '&': lambda a,b: Value(Type.BOOL, a.value() and b.value()),
     '==': lambda a,b: Value(Type.BOOL, a.value()==b.value()),
     '!=': lambda a,b: Value(Type.BOOL, a.value()!=b.value()),
     '|': lambda a,b: Value(Type.BOOL, a.value() or b.value())
    }

  def _compute_indentation(self, program):
    self.indents = [len(line) - len(line.lstrip(' ')) for line in program]

  def _find_first_instruction(self, funcname, args=[]):
    func_info = self.func_manager.get_function_info(funcname)
    if func_info == None:
      super().error(ErrorType.NAME_ERROR,f"Unable to locate {funcname} function", self.ip) #!

    # TODO: Validate lengths of args and function_info.parameters matches
    # Add parameters to scope
    for i in range(len(args)):
      var_name, param_name = args[i], func_info.names[i]
      
      #if not self.env_manager.exists(var_name):
      #  super().error(ErrorType.NAME_ERROR,f'Unknown variable {var_name}', self.ip) #!
      var = self._get_value(var_name)
      
      if func_info.values[i].ref:
        self.env_manager.add(param_name, var)
      else:
        self.env_manager.add(param_name, var.deepcopy())

    return func_info.start_ip

  def _get_value(self, token):
    '''
    Given a token name (e.g., x, 17, True, "foo"), give us a Value object associated with it.
    '''
    if not token:
      super().error(ErrorType.NAME_ERROR,f"Empty token", self.ip) #no
    if token[0] == '"':
      return Value(Type.STRING, token.strip('"'))
    if token.isdigit() or token[0] == '-':
      return Value(Type.INT, int(token))
    if token == InterpreterBase.TRUE_DEF or token == InterpreterBase.FALSE_DEF:
      return Value(Type.BOOL, token == InterpreterBase.TRUE_DEF)
    value = self.env_manager.get(token)
    if value  == None:
      super().error(ErrorType.NAME_ERROR,f"Unknown variable {token}", self.ip) #!
    return value

  def _set_value(self, varname: str, value_type: Value) -> None:
    '''
    Given a variable name and a Value object, associate the name with the value.
    '''
    self.env_manager.set(varname, value_type)

  def _eval_expression(self, tokens) -> Value:
    '''
    Evaluate expressions in prefix notation: + 5 * 6 x.
    '''
    stack = []

    for token in reversed(tokens):
      if token in self.binary_op_list:
        v1 = stack.pop()
        v2 = stack.pop()
        if v1.type() != v2.type():
          super().error(ErrorType.TYPE_ERROR,f"Mismatching types {v1.type()} and {v2.type()}", self.ip) #!
        operations = self.binary_ops[v1.type()]
        if token not in operations:
          super().error(ErrorType.TYPE_ERROR,f"Operator {token} is not compatible with {v1.type()}", self.ip) #!
        stack.append(operations[token](v1,v2))
      elif token == '!':
        v1 = stack.pop()
        if v1.type() != Type.BOOL:
          super().error(ErrorType.TYPE_ERROR,f"Expecting boolean for ! {v1.type()}", self.ip) #!
        stack.append(Value(Type.BOOL, not v1.value()))
      else:
        value_type = self._get_value(token)
        stack.append(value_type)

    if len(stack) != 1:
      super().error(ErrorType.SYNTAX_ERROR,f"Invalid expression", self.ip) #no

    return stack[0]
